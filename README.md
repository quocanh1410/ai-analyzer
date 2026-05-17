# Kubernetes AIOps Mini Platform

AI-powered Kubernetes incident monitoring and alerting system using logs, Kubernetes events, and LLM-based analysis.

---

# 🚀 Features

- Collect container logs from Grafana Loki
- Collect Kubernetes events in realtime
- Detect common Kubernetes incidents
- AI-powered incident analysis
- Telegram realtime alerting
- Multi-source observability
- Lightweight local LLM support

---

# 🧠 Supported Incident Types

| Incident | Source |
|---|---|
| DNS failure | Container logs |
| Exception / Crash | Container logs |
| Timeout | Container logs |
| ImagePullBackOff | Kubernetes events |
| CrashLoopBackOff | Kubernetes events |
| FailedScheduling | Kubernetes events |
| etcd slow request | Container logs |

---

# ⚙️ Architecture

```text
+---------------------+
|   Container Logs    |
|      (Loki)         |
+---------------------+
           |
           v
+---------------------+
|   Log Collector     |
+---------------------+

+---------------------+
| Kubernetes Events   |
| kubectl get events  |
+---------------------+
           |
           v
+---------------------+
|  Event Collector    |
+---------------------+

           |
           v

+---------------------+
|     AI Analyzer     |
|      FastAPI        |
+---------------------+

           |
           v

+---------------------+
| Telegram Alerting   |
+---------------------+
```
---

# 🔧 Components

## 1️⃣ AI Service

`ai_service.py`

FastAPI service responsible for:

- receiving logs/events
- sending prompts to LLM
- returning incident analysis

Example output:

```text
Severity: High

Root Cause:
Kubernetes failed to pull container image.

Recommendations:
- Verify image name
- Check registry access
```

---

## 2️⃣ Container Log Collector

`collector.py`

Features:

- query Loki API
- filter error logs
- deduplicate logs
- send logs to AI analyzer

Example detected logs:

```text
wget: bad address 'fake-service:8080'
Exception: database connection failed
```

---

## 3️⃣ Kubernetes Event Collector

`collector_events.py`

Features:

- collect events using:

```bash
kubectl get events -A -o json
```

- detect:
  - ImagePullBackOff
  - CrashLoopBackOff
  - FailedScheduling
  - Back-off restarting failed container

- send incidents to AI analyzer

---

## 4️⃣ Telegram Alerting

Realtime alerting using Telegram Bot API.

Example alert:

```text
🚨 Kubernetes Event Alert

[Namespace:default]
[Pod:image-fail]
[Reason:BackOff]

Back-off pulling image "abc/notexist"
```

---

# 🛠️ Installation

## Clone repository

```bash
git clone <your-repo>
cd ai-analyzer
```

---

## Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run Services

## Start AI service

```bash
uvicorn ai_service:app --host 0.0.0.0 --port 8001
```

---

## Run log collector

```bash
python3 collector.py
```

---

## Run realtime collector

```bash
python3 collector_realtime.py
```

---

## Run Kubernetes event collector

```bash
python3 collector_events.py
```

---

# 🧪 Test Scenarios

## DNS Failure

```bash
kubectl run dns-fail \
--image=busybox \
-- sh -c 'while true; do wget http://fake-service:8080; sleep 2; done'
```

---

## ImagePullBackOff

```bash
kubectl run image-fail \
--image=abc/notexist
```

---

## CrashLoopBackOff

```bash
kubectl run python-error \
--image=python \
-- python -c "raise Exception('database connection failed')"
```

---

# 🤖 AI Model

Currently tested with:

- Qwen
- Tiny local LLMs

Known limitations:

- small models may hallucinate
- Kubernetes reasoning is limited
- recommendations may be inaccurate

---

# 🚀 Future Improvements

- Kubernetes Deployment support
- RBAC integration
- Incident correlation engine
- Prometheus metrics integration
- Grafana dashboard
- Better LLM models
- Rule-based remediation engine

---

# 📌 Tech Stack

| Technology | Purpose |
|---|---|
| Python | Main language |
| FastAPI | AI API service |
| Loki | Log aggregation |
| Kubernetes | Orchestration |
| Telegram Bot API | Alerting |
| LLM | Incident analysis |

---

# 📖 Example Workflow

```text
Container Crash
        ↓
Loki detects error log
        ↓
Collector filters log
        ↓
Send to AI
        ↓
AI generates root cause
        ↓
Telegram alert sent
```

---

# 🧠 Project Goal

This project aims to demonstrate a lightweight AIOps pipeline for Kubernetes environments using:

- observability
- realtime incident detection
- AI-assisted troubleshooting
- automated alerting

---

# 👨‍💻 Author

Kubernetes AIOps Research Project

Built for learning and experimentation in cloud-native observability and AI operations.
