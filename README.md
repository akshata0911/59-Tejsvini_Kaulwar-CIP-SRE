# CloudScale Lab - Load Balancer and Auto-Scaling Simulator

A live dashboard that shows how cloud infrastructure handles changing traffic:
load balancing, auto-scaling, self-healing and pay-as-you-go cost.

**Honest note:** servers are simulated in Python. No AWS/Azure/GCP account is needed.

## Run on Windows (easy way)
Double-click `run.bat`  (or run `run.bat` in the VS Code terminal).
Then open http://127.0.0.1:5000

## Run manually (cmd / PowerShell)
```
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000  (stop with Ctrl + C)

## Demo flow (2-3 minutes)
1. Start: 2 servers, healthy, low CPU.
2. Click **Traffic spike**: CPU rises, new servers are added automatically.
3. Click **Kill a server**: traffic is rerouted, then the server is replaced (self-healing).
4. Switch **Round robin** to **Least connections**: server CPU bars become more even.
5. Drag the traffic slider down: servers are removed, cost falls.
6. Show the **You are saving** percentage against a fixed 6-server setup.

## How it works
- Every second the backend simulates one tick: traffic is split across healthy servers.
- One server handles 100 req/s, so CPU % = requests / 100.
- Auto-scaler: average CPU above 70% adds a server; below 30% removes one (2 to 8 servers, 2 s cooldown).
- Round robin uses uneven request sizes; least connections balances them.
- Response time rises sharply as CPU approaches 100%.
- Cost = running servers x $0.10 per hour (simulated price).
- SQLite (`cloudscale.db`) stores the event log. The browser polls `/api/state` every second.

## Project structure
```
app.py              Flask backend + simulation engine + REST API
templates/index.html  Dashboard page
static/style.css    Styling
static/app.js       Live updates and charts (no external libraries)
run.bat             One-click setup and start (Windows)
```

## API
GET /api/state | POST /api/traffic, /api/spike, /api/kill, /api/algo, /api/autoscale, /api/reset

## Limitations and future scope
- Simulation only; replace virtual servers with AWS EC2 (boto3) and a real Elastic Load Balancer.
- Add user login, scheduled traffic patterns and CloudWatch-style alarms.

## New in version 2
- **Run demo**: plays the full story automatically with captions (normal, spike, crash, recovery, calm).
- **Real-life scenarios**: Normal day, Flash sale, Exam result day, Night time.
- **With and without auto-scaling**: compares against a fixed 2-server setup (requests lost, waiting time).
- **Total bill**: running cost vs a fixed 6-server setup (1 second = 1 simulated minute).
- **Download report**: CSV with peak traffic, servers used, failures, cost, requests lost and the event log.
- **Plain-English labels, (?) tooltips and dark mode.**
