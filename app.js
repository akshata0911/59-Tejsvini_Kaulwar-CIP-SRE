const $ = id => document.getElementById(id);
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
let dragging = false, demoOn = false;

async function call(url, body) {
  const r = await fetch(url, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body || {})});
  const d = await r.json();
  if (d.error) { $("msg").textContent = d.error; setTimeout(() => $("msg").textContent = "", 3000); }
  render(d);
}

const barColor = c => c >= 80 ? "#dc3f3a" : c >= 60 ? "#d98a00" : "#16a34a";

function chart(id, series, max, lines) {
  const c = $(id), ctx = c.getContext("2d"), w = c.width = c.clientWidth * 2, h = c.height = 260;
  ctx.clearRect(0, 0, w, h);
  const top = max || Math.max(10, ...series.flatMap(s => s.data)) * 1.2;
  const f = v => top < 10 ? v.toFixed(2) : Math.round(v);
  ctx.lineWidth = 2; ctx.fillStyle = css("--mute"); ctx.font = "20px Segoe UI";
  for (let i = 0; i <= 4; i++) {
    const y = h - 24 - (h - 40) * i / 4;
    ctx.strokeStyle = css("--line"); ctx.beginPath(); ctx.moveTo(70, y); ctx.lineTo(w, y); ctx.stroke();
    ctx.fillText(f(top * i / 4), 4, y + 6);
  }
  (lines || []).forEach(v => {
    const y = h - 24 - (h - 40) * v / top;
    ctx.setLineDash([8, 8]); ctx.strokeStyle = "#d98a00"; ctx.beginPath(); ctx.moveTo(70, y); ctx.lineTo(w, y); ctx.stroke(); ctx.setLineDash([]);
  });
  series.forEach(s => {
    if (s.data.length < 2) return;
    ctx.strokeStyle = s.color; ctx.lineWidth = 4; ctx.lineJoin = "round"; ctx.setLineDash(s.dash ? [10, 8] : []); ctx.beginPath();
    s.data.forEach((v, i) => {
      const x = 70 + (w - 80) * i / 59, y = h - 24 - (h - 40) * Math.min(v, top) / top;
      i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
    });
    ctx.stroke(); ctx.setLineDash([]);
  });
}

function compare(d) {
  const col = (t, cls, o) => `<div class="cm ${cls}"><h3>${t}</h3><p>Servers <b>${o.servers}</b></p><p>Workload <b>${o.cpu}%</b></p><p>Waiting time <b>${o.latency} ms</b></p><p>Requests lost now <b class="${o.lost ? "bad" : ""}">${o.lost}/s</b></p></div>`;
  $("compare").innerHTML = col("With auto-scaling", "good", d.compare.auto) + col("Without it (fixed 2 servers)", "bad", d.compare.fixed);
  $("c-totals").innerHTML = `Requests lost so far: <b class="green">${d.lost_total}</b> with auto-scaling vs <b class="bad">${d.lost_fixed_total}</b> without. Bill so far: <b>$${d.bill.toFixed(2)}</b> vs <b>$${d.bill6.toFixed(2)}</b> for a fixed 6-server setup (saved $${d.saved.toFixed(2)}).`;
}

function render(d) {
  $("status").textContent = d.status; $("status").className = "pill " + d.status_level;
  $("k-rps").textContent = d.rps; $("k-srv").textContent = d.active;
  $("k-cpu").textContent = d.avg_cpu + "%"; $("k-lat").textContent = d.latency + " ms";
  $("k-cost").textContent = "$" + d.cost.toFixed(2);
  $("c-fixed").textContent = "$" + d.fixed_cost.toFixed(2) + " / hr";
  $("c-now").textContent = "$" + d.cost.toFixed(2) + " / hr";
  $("c-save").textContent = d.saving + "%";
  $("rules").textContent = `Add a server above ${d.rules.out}% workload, remove one below ${d.rules.in}% (min ${d.rules.min}, max ${d.rules.max}).`;
  if (!dragging) $("traffic").value = d.traffic;
  $("t-out").textContent = d.traffic + " req/s";
  $("algo").value = d.algo; $("auto").checked = d.auto;
  demoOn = d.demo; $("demo").textContent = demoOn ? "Stop demo" : "Run demo";
  $("caption").hidden = !d.caption; $("caption").textContent = d.caption;

  $("servers").innerHTML = d.servers.map(s => s.status === "failed"
    ? `<div class="srv failed"><div class="row"><span>Server ${s.id}</span><span class="bad">Failed</span></div><small>Replacing in ${s.heal}s</small></div>`
    : `<div class="srv"><div class="row"><span>Server ${s.id}</span><span>${s.cpu}%</span></div><div class="bar"><i style="width:${s.cpu}%;background:${barColor(s.cpu)}"></i></div><small>${s.rps} req/s</small></div>`).join("");
  $("log").innerHTML = d.events.slice(0, 8).map(e => `<li><time>${e.time}</time><span class="${e.level}">${e.message}</span></li>`).join("");
  compare(d);

  const H = d.history;
  chart("c1", [{data: H.map(p => p.rps), color: "#2563eb"}]);
  chart("c2", [{data: H.map(p => p.cpu), color: "#0d9488"}], 100, [d.rules.out, d.rules.in]);
  chart("c3", [{data: H.map(p => p.servers), color: "#7c3aed"}], d.rules.max);
  chart("c4", [{data: H.map(p => p.bill), color: "#2563eb"}, {data: H.map(p => p.bill6), color: "#dc3f3a", dash: true}]);
}

async function poll() { try { render(await (await fetch("/api/state")).json()); } catch (e) {} }

$("traffic").addEventListener("input", e => { dragging = true; $("t-out").textContent = e.target.value + " req/s"; });
$("traffic").addEventListener("change", e => { dragging = false; call("/api/traffic", {value: +e.target.value}); });
$("spike").onclick = () => call("/api/spike");
$("kill").onclick = () => call("/api/kill");
$("reset").onclick = () => call("/api/reset");
$("demo").onclick = () => call("/api/demo", {start: !demoOn});
$("algo").onchange = e => call("/api/algo", {algo: e.target.value});
$("auto").onchange = e => call("/api/autoscale", {enabled: e.target.checked});
document.querySelectorAll("[data-s]").forEach(b => b.onclick = () => call("/api/scenario", {name: b.dataset.s}));

const root = document.documentElement;
function setTheme(t) { root.dataset.theme = t; $("theme").textContent = t === "dark" ? "Light mode" : "Dark mode"; try { localStorage.setItem("theme", t); } catch (e) {} }
let saved = "light"; try { saved = localStorage.getItem("theme") || "light"; } catch (e) {}
setTheme(saved);
$("theme").onclick = () => { setTheme(root.dataset.theme === "dark" ? "light" : "dark"); poll(); };

poll(); setInterval(poll, 1000);
