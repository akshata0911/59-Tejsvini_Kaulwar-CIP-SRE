"""CloudScale Lab - Load Balancer and Auto-Scaling Simulator (Flask + SQLite)."""
import random
import sqlite3
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "cloudscale.db"

CAPACITY = 100        # requests/sec one virtual server can handle
PRICE_PER_HOUR = 0.10  # simulated cost of one server per hour
MIN_SERVERS = 2
MAX_SERVERS = 8
SCALE_OUT_CPU = 70    # add a server above this average CPU %
SCALE_IN_CPU = 30     # remove a server below this average CPU %
COOLDOWN_TICKS = 2    # wait between scaling actions
HEAL_TICKS = 5        # seconds before a failed server is replaced
FIXED_SERVERS = 6     # big fixed setup: safe but expensive
FIXED_SMALL = 2       # small fixed setup: cheap but crashes under load

SCENARIOS = {"normal": (120, "Normal day"), "flash_sale": (550, "Flash sale"),
             "exam_result": (650, "Exam result day"), "night": (40, "Night time")}

# Demo script: (seconds, action, value, caption)
DEMO = [(6, "traffic", 120, "Normal day: 2 servers handle the traffic easily."),
        (10, "traffic", 550, "Big sale starts: traffic jumps and new servers are added automatically."),
        (8, "kill", 0, "A server crashes: traffic moves to the others while a replacement starts."),
        (8, "wait", 0, "Self-healing: the failed server is replaced automatically."),
        (10, "traffic", 60, "Sale ends: traffic drops and extra servers are removed to save money."),
        (5, "end", 0, "Demo finished. Check the comparison and the total bill below.")]

app = Flask(__name__)
lock = threading.Lock()
state = {}
history = deque(maxlen=60)
events = deque(maxlen=30)


def db_init():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "time TEXT, level TEXT, message TEXT)")


def log(message, level="info"):
    stamp = datetime.now().strftime("%H:%M:%S")
    events.appendleft({"time": stamp, "level": level, "message": message})
    with sqlite3.connect(DB_PATH) as con:
        con.execute("INSERT INTO events(time, level, message) VALUES(?,?,?)", (stamp, level, message))


def new_server(sid):
    return {"id": sid, "status": "up", "cpu": 0, "rps": 0, "heal": 0}


def reset_state():
    state.clear()
    state.update({"traffic": 120, "algo": "round_robin", "auto": True, "cooldown": 0, "next_id": 3,
                  "servers": [new_server(1), new_server(2)], "avg_cpu": 0, "latency": 40, "t": 0,
                  "demo": None, "caption": "", "peak": 0, "maxsrv": 2, "fails": 0, "outs": 0, "ins": 0,
                  "bill": 0.0, "bill6": 0.0, "lost": 0, "lost_fixed": 0, "lost_now": 0,
                  "fixed": {"servers": FIXED_SMALL, "cpu": 0, "latency": 40, "lost": 0}})
    history.clear()
    events.clear()
    with sqlite3.connect(DB_PATH) as con:
        con.execute("DELETE FROM events")
    log("Simulation started with 2 servers", "info")


def alive_servers():
    return [s for s in state["servers"] if s["status"] == "up"]


def tick():
    """One simulated second: balance traffic, check health, auto-scale."""
    state["t"] += 1
    demo_step()
    for s in state["servers"]:
        if s["status"] == "failed":
            s["heal"] -= 1
            if s["heal"] <= 0:
                s["status"] = "up"
                log(f"Server {s['id']} replaced automatically (self-healing)", "success")

    alive = alive_servers()
    load = state["traffic"] * random.uniform(0.97, 1.03)
    if alive:
        # Round robin gives uneven request sizes; least connections evens them out.
        spread = (0.80, 1.20) if state["algo"] == "round_robin" else (0.97, 1.03)
        weights = [random.uniform(*spread) for _ in alive]
        total = sum(weights)
        for s, w in zip(alive, weights):
            s["rps"] = round(load * w / total)
            s["cpu"] = min(100, round(s["rps"] / CAPACITY * 100))
    for s in state["servers"]:
        if s["status"] == "failed":
            s["rps"], s["cpu"] = 0, 0

    avg = round(sum(s["cpu"] for s in alive) / len(alive)) if alive else 0
    state["avg_cpu"] = avg
    state["latency"] = round(40 + (avg / 100) ** 3 * 500 + (300 if avg >= 100 else 0))

    if state["cooldown"] > 0:
        state["cooldown"] -= 1
    elif state["auto"] and alive:
        if avg > SCALE_OUT_CPU and len(alive) < MAX_SERVERS:
            state["servers"].append(new_server(state["next_id"]))
            log(f"CPU at {avg}%: scaled out to {len(alive) + 1} servers (added Server {state['next_id']})", "warn")
            state["next_id"] += 1
            state["outs"] += 1
            state["cooldown"] = COOLDOWN_TICKS
        elif avg < SCALE_IN_CPU and len(alive) > MIN_SERVERS:
            victim = alive[-1]
            state["servers"].remove(victim)
            state["ins"] += 1
            log(f"CPU at {avg}%: scaled in to {len(alive) - 1} servers (removed Server {victim['id']})", "success")
            state["cooldown"] = COOLDOWN_TICKS

    fcap = FIXED_SMALL * CAPACITY
    fcpu = min(100, round(load / fcap * 100))
    state["fixed"] = {"servers": FIXED_SMALL, "cpu": fcpu, "lost": max(0, round(load - fcap)),
                      "latency": round(40 + (fcpu / 100) ** 3 * 500 + (300 if fcpu >= 100 else 0))}
    state["lost_now"] = max(0, round(load - len(alive) * CAPACITY))
    state["lost"] += state["lost_now"]
    state["lost_fixed"] += state["fixed"]["lost"]
    state["bill"] += len(alive) * PRICE_PER_HOUR / 60   # 1 second = 1 simulated minute
    state["bill6"] += FIXED_SERVERS * PRICE_PER_HOUR / 60
    state["peak"] = max(state["peak"], round(load))
    state["maxsrv"] = max(state["maxsrv"], len(alive_servers()))
    history.append({"rps": round(load), "cpu": avg, "servers": len(alive_servers()),
                    "bill": round(state["bill"], 3), "bill6": round(state["bill6"], 3)})


def loop():
    while True:
        time.sleep(1)
        with lock:
            tick()


def snapshot():
    alive = alive_servers()
    failed = len(state["servers"]) - len(alive)
    avg = state["avg_cpu"]
    if failed:
        status = ("Recovering", "warn")
    elif avg >= 90:
        status = ("Overloaded", "danger")
    elif avg > SCALE_OUT_CPU:
        status = ("High load", "warn")
    else:
        status = ("Healthy", "ok")
    cost = round(len(alive) * PRICE_PER_HOUR, 2)
    fixed = round(FIXED_SERVERS * PRICE_PER_HOUR, 2)
    saving = max(0, round((1 - cost / fixed) * 100)) if fixed else 0
    return {"traffic": state["traffic"], "algo": state["algo"], "auto": state["auto"],
            "servers": state["servers"], "avg_cpu": avg, "latency": state["latency"],
            "active": len(alive), "status": status[0], "status_level": status[1],
            "cost": cost, "fixed_cost": fixed, "saving": saving,
            "rps": history[-1]["rps"] if history else state["traffic"],
            "history": list(history), "events": list(events),
            "compare": {"auto": {"servers": len(alive), "cpu": avg, "latency": state["latency"], "lost": state["lost_now"]},
                        "fixed": state["fixed"]},
            "bill": state["bill"], "bill6": state["bill6"], "saved": max(0, state["bill6"] - state["bill"]),
            "lost_total": state["lost"], "lost_fixed_total": state["lost_fixed"],
            "caption": state["caption"], "demo": state["demo"] is not None,
            "rules": {"out": SCALE_OUT_CPU, "in": SCALE_IN_CPU, "min": MIN_SERVERS, "max": MAX_SERVERS}}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/state")
def api_state():
    with lock:
        return jsonify(snapshot())


@app.route("/api/traffic", methods=["POST"])
def api_traffic():
    value = int((request.get_json(silent=True) or {}).get("value", 120))
    with lock:
        state["traffic"] = max(20, min(800, value))
        return jsonify(snapshot())


@app.route("/api/spike", methods=["POST"])
def api_spike():
    with lock:
        state["traffic"] = 550
        log("Traffic spike: load jumped to 550 requests/sec", "warn")
        return jsonify(snapshot())


@app.route("/api/kill", methods=["POST"])
def api_kill():
    with lock:
        if not kill_one():
            return jsonify({**snapshot(), "error": "Keep at least one server running."})
        return jsonify(snapshot())


@app.route("/api/algo", methods=["POST"])
def api_algo():
    algo = (request.get_json(silent=True) or {}).get("algo")
    with lock:
        if algo in ("round_robin", "least_connections"):
            state["algo"] = algo
            log("Load balancing: " + algo.replace("_", " ").capitalize(), "info")
        return jsonify(snapshot())


@app.route("/api/autoscale", methods=["POST"])
def api_autoscale():
    with lock:
        state["auto"] = bool((request.get_json(silent=True) or {}).get("enabled", True))
        log("Auto-scaling " + ("enabled" if state["auto"] else "disabled"), "info")
        return jsonify(snapshot())


@app.route("/api/reset", methods=["POST"])
def api_reset():
    with lock:
        reset_state()
        return jsonify(snapshot())


def kill_one():
    alive = alive_servers()
    if len(alive) < 2:
        return False
    victim = random.choice(alive)
    victim["status"], victim["heal"] = "failed", HEAL_TICKS
    state["fails"] += 1
    log(f"Server {victim['id']} failed: traffic rerouted to {len(alive) - 1} healthy servers", "danger")
    return True


def demo_step():
    d = state["demo"]
    if d is None:
        return
    if d["left"] <= 0:
        d["i"] += 1
        if d["i"] >= len(DEMO):
            state["demo"], state["caption"] = None, ""
            return
        secs, action, value, caption = DEMO[d["i"]]
        d["left"], state["caption"] = secs, caption
        if action == "traffic":
            state["traffic"] = value
        elif action == "kill":
            kill_one()
    d["left"] -= 1


@app.route("/api/scenario", methods=["POST"])
def api_scenario():
    name = (request.get_json(silent=True) or {}).get("name")
    with lock:
        if name in SCENARIOS:
            state["traffic"] = SCENARIOS[name][0]
            log(f"Scenario: {SCENARIOS[name][1]} ({SCENARIOS[name][0]} requests/sec)", "warn")
        return jsonify(snapshot())


@app.route("/api/demo", methods=["POST"])
def api_demo():
    start = bool((request.get_json(silent=True) or {}).get("start", True))
    with lock:
        if start:
            reset_state()
            state["demo"] = {"i": -1, "left": 0}
            log("Automatic demo started", "info")
        else:
            state["demo"], state["caption"] = None, ""
        return jsonify(snapshot())


@app.route("/api/report.csv")
def api_report():
    with lock:
        rows = [("Peak traffic (requests/sec)", state["peak"]), ("Most servers used", state["maxsrv"]),
                ("Scale-out actions", state["outs"]), ("Scale-in actions", state["ins"]),
                ("Server failures", state["fails"]),
                ("Total bill with auto-scaling ($)", round(state["bill"], 2)),
                ("Total bill with fixed 6 servers ($)", round(state["bill6"], 2)),
                ("Requests lost with auto-scaling", state["lost"]),
                ("Requests lost with fixed 2 servers", state["lost_fixed"])]
    with sqlite3.connect(DB_PATH) as con:
        ev = con.execute("SELECT time, level, message FROM events ORDER BY id").fetchall()
    out = ["Metric,Value"] + [f"{k},{v}" for k, v in rows] + ["", "Time,Level,Event"]
    out += [f'{t},{l},"{m}"' for t, l, m in ev]
    return Response("\n".join(out), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=cloudscale_report.csv"})


db_init()
reset_state()

if __name__ == "__main__":
    threading.Thread(target=loop, daemon=True).start()
    print("CloudScale Lab running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
