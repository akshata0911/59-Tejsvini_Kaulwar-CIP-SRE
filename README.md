# Cloud-Computing-Pedagogical-Initiatives-2026-2027
# ☁️ CloudScale Lab – Load Balancer and Auto-Scaling Simulator

A Cloud Computing Simulation Platform demonstrating Load Balancing, Auto-Scaling, Self-Healing, Performance Monitoring, and Cost Optimization.

**Cloud Computing Mini Project | Academic Year 2026–2027**

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Flask](https://img.shields.io/badge/Backend-Flask-black)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue)
![HTML](https://img.shields.io/badge/Frontend-HTML-orange)
![CSS](https://img.shields.io/badge/Styling-CSS-blue)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow)

**Features • Technology Stack • Project Structure • Setup • Workflow • Future Scope**

---

## 👥 Created By

| Roll No. | Name |
|---|---|
| 121 | Kasralikar Mrudula |
| 138 | Bhagyashri Sontakke |
| 144 | Shaikh Sidra Sareen |
| 154 | Ketaki Gundewar |
| 159 | Tejsvini Kaulwar |

**Project Guide:** Dr. S. Y. Gaikwad

## 📑 Table of Contents

- About the Project
- Objectives
- Key Features
- Load Balancing Algorithms
- Auto-Scaling Mechanism
- Technology Stack
- Directory Structure
- System Workflow
- Project Setup
- Benefits
- Limitations
- Future Scope
- Project Team

## 📖 About the Project

CloudScale Lab is a Cloud Computing simulation project designed to demonstrate how cloud infrastructure manages dynamic workloads through intelligent resource management.

The project provides an interactive dashboard that simulates incoming traffic, distributes requests across multiple virtual servers, monitors CPU utilization, automatically adjusts server capacity, and demonstrates server failure recovery.

It also compares Auto-Scaling infrastructure with fixed-server infrastructure to demonstrate resource utilization and cost optimization.

**Note:** CloudScale Lab is a simulation-based project. It demonstrates cloud computing concepts using virtual server simulations rather than deploying actual cloud infrastructure.

## 🎯 Objectives

- Understand the working of cloud load balancing.
- Demonstrate automatic server scaling based on workload.
- Simulate server failure detection and self-healing.
- Monitor server performance and traffic distribution.
- Analyze infrastructure resource utilization.
- Compare auto-scaling and fixed-server costs.

## 🌟 Key Features

### ⚖️ Load Balancing

- Round Robin Algorithm: Distributes incoming requests sequentially among available servers.
- Least Connections Algorithm: Assigns requests to the server with the lowest number of active connections.
- Distributes simulated traffic across virtual servers.

### 📈 Auto-Scaling

- Automatic Scale-Out: Adds servers when CPU utilization exceeds the configured threshold.
- Automatic Scale-In: Removes extra servers when workload decreases.
- Configurable minimum and maximum server limits.
- Cooldown mechanism to control scaling frequency.

### 🛡️ Self-Healing

- Simulates virtual server failures.
- Detects failed server conditions.
- Demonstrates automatic server replacement and recovery.

### 📊 Performance Monitoring Dashboard

- CPU utilization monitoring.
- Server status and availability.
- Traffic distribution visualization.
- Response latency monitoring.
- Live dashboard updates.

### 🚦 Traffic Simulation

Supports different traffic scenarios:

- Normal Day
- Flash Sale
- Exam Result Day
- Night Time

### 💰 Cost Comparison

- Compares auto-scaling and fixed-server configurations.
- Displays infrastructure cost estimates.
- Demonstrates potential resource savings through dynamic scaling.

### 📁 Reporting

- CSV report generation.
- Simulation performance data.
- Cost comparison information.

## 🧠 Load Balancing Algorithms

| Algorithm | Description |
|---|---|
| Round Robin | Distributes requests sequentially among servers. |
| Least Connections | Selects the server with the fewest active connections. |

## ⚙️ Auto-Scaling Mechanism

The simulator uses CPU utilization thresholds to demonstrate automatic resource management.

| Parameter | Configuration |
|---|---|
| Scale-Out Threshold | Above 70% CPU |
| Scale-In Threshold | Below 30% CPU |
| Minimum Servers | 2 |
| Maximum Servers | 8 |
| Cooldown Period | 2 seconds (simulated) |

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| Database | SQLite |
| Server Framework | Flask |
| Simulation | Python-based server and traffic simulation |

## 📁 Directory Structure

```text
CloudScaleLab/
│
├── app.py
│
├── requirements.txt
│
├── run.bat
│
├── templates/
│   └── index.html
│
└── static/
    ├── app.js
    └── style.css
```

## 🔄 System Workflow

1. User selects a traffic simulation scenario.
2. Incoming requests are generated.
3. The load balancer distributes requests among available virtual servers.
4. CPU utilization and server workload are monitored.
5. The auto-scaling mechanism checks predefined CPU thresholds.
6. Servers are added or removed according to workload.
7. Server failure and self-healing are demonstrated.
8. Dashboard displays performance metrics and cost comparisons.

## 🚀 Project Setup

### Prerequisites

- Python 3.x
- pip
- Visual Studio Code (recommended)
- Web Browser

### 1. Extract the Project

Download and extract the `CloudScaleLab` project ZIP file.

### 2. Open in VS Code

Open the extracted project folder in Visual Studio Code.

### 3. Install Dependencies

Open the terminal and execute:

```bash
pip install -r requirements.txt
```

### 4. Run the Application

Execute the following command:

```bash
python app.py
```

Alternatively, run the `run.bat` file on Windows.

### 5. Open the Dashboard

Open your browser and visit:

```text
http://127.0.0.1:5000
```

The CloudScale Lab dashboard will be accessible locally.

## 💡 Benefits

- Provides practical understanding of cloud computing concepts.
- Demonstrates efficient traffic distribution.
- Explains dynamic resource allocation.
- Demonstrates server failure recovery concepts.
- Helps understand infrastructure cost optimization.
- Provides an interactive learning environment.

## ⚠️ Limitations

- Uses simulated virtual servers instead of actual cloud servers.
- Does not directly deploy infrastructure on AWS, Azure, or Google Cloud.
- Performance metrics are simulation-based.
- Actual cloud networking, billing, and production security are outside the current implementation scope.

## 🔮 Future Scope

- Integration with AWS EC2 instances.
- Implementation of actual cloud load balancers.
- Integration with cloud monitoring services.
- Advanced workload prediction.
- Real cloud deployment and resource management.
- Enhanced monitoring and analytics.

## 🎓 Academic Information

**Project Title:** CloudScale Lab – Load Balancer and Auto-Scaling Simulator

**Project Type:** Cloud Computing Mini Project

**Academic Year:** 2026–2027

**Institution:** MGM's College of Engineering, Nanded

**Project Guide:** Dr. S. Y. Gaikwad

---

**CloudScale Lab – Simulating Intelligent Cloud Resource Management.**
