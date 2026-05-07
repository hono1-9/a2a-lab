# A2A Lab — CS4680



## Project Structure

```
a2a-lab/
├── server/
│   ├── agent_card.py          # Agent Card definition and validation
│   ├── handlers.py            # Task handling logic (echo, summarise)
│   ├── main.py                # FastAPI A2A server
│   ├── agent_engine_wrapper.py# Vertex AI Agent Engine wrapper
│   ├── Dockerfile             # Container image for Cloud Run
│   └── requirements.txt       # Python dependencies
├── client/
│   ├── client.py              # A2A client implementation
│   └── demo.py                # Demo script
├── cloud/
│   ├── deploy_cloud_run.sh    # Cloud Run deployment script
│   └── deploy_agent_engine.py # Vertex AI Agent Engine deployment script
├── report.md                  # Written answers for all parts
└── README.md                  # This file
```

---

## Setup

### Prerequisites

- Python 3.10+
- Docker Desktop
- Google Cloud CLI (`gcloud`)

### 1. Clone and create virtual environment

```bash
git clone <your-repo-url>
cd a2a-lab
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn httpx pydantic
```

---

## Part 1 & 2: Run the server and client locally

### Start the server

```bash
cd server
uvicorn main:app --reload --port 8000
```

### Test with curl

```bash
# Agent Card
curl http://localhost:8000/.well-known/agent.json

# Health check
curl http://localhost:8000/health

# Send a task
curl -X POST http://localhost:8000/tasks/send \
  -H "Content-Type: application/json" \
  -d '{"id":"t1","message":{"role":"user","parts":[{"type":"text","text":"Hello A2A"}]}}'
```

### Run the demo client

```bash
cd client
python demo.py
```

---

## Part 4: Cloud Run Deployment

### Deploy

```bash
chmod +x cloud/deploy_cloud_run.sh
./cloud/deploy_cloud_run.sh
```

### Cloud Run Service URL

```
https://echo-a2a-agent-525803800713.us-central1.run.app
```

### Test the deployed service

```bash
# Agent Card
curl https://echo-a2a-agent-525803800713.us-central1.run.app/.well-known/agent.json

# Health check
curl https://echo-a2a-agent-525803800713.us-central1.run.app/health

# Send a task
curl -X POST https://echo-a2a-agent-525803800713.us-central1.run.app/tasks/send \
  -H "Content-Type: application/json" \
  -d '{"id":"t1","message":{"role":"user","parts":[{"type":"text","text":"Hello from Cloud Run"}]}}'
```

### Run demo client against Cloud Run

```bash
cd client
# Edit demo.py: change "http://localhost:8000" to the Cloud Run URL
python demo.py
```

---

## GCP Project Info

| Field | Value |
|-------|-------|
| Project ID | `a2a-lab-nhonoka` |
| Region | `us-central1` |
| Cloud Run Service | `echo-a2a-agent` |
| Artifact Registry | `a2a-lab` |