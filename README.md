# Forge — Distributed Job Platform

A distributed task processing engine: accept jobs over an API, queue them, and
have a pool of background workers process them reliably — with retries,
fault tolerance, and horizontal scaling.

> Status: **Week 1 — foundation.** API + PostgreSQL job store. Queue and workers
> arrive in Week 2.

## Architecture (target)

```
POST /jobs ──▶ FastAPI ──▶ PostgreSQL (source of truth: job state)
                  │
                  └──▶ Redis (queue) ──▶ Worker pool ──▶ writes result back
                                          (one worker type calls an LLM)
                  Prometheus + Grafana ◀── metrics
```

- **FastAPI** — accepts jobs, returns a job id instantly (never does slow work).
- **PostgreSQL** — permanent record of every job and its status.
- **Redis** — fast to-do list that coordinates which worker does what.
- **Workers** — generic task executors; scale horizontally; survive crashes.

## Tech

Python · FastAPI · PostgreSQL · (Week 2+) Redis · Docker · Kafka · AWS · Kubernetes

## Run (Week 1)

```bash
# 1. Start PostgreSQL
docker run --name jobdb -e POSTGRES_PASSWORD=dev -p 5432:5432 -d postgres

# 2. Install deps
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Run the API
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` for the interactive API.

## Try it

```bash
curl -X POST localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"payload": {"text": "summarize this document"}}'

curl localhost:8000/jobs        # list recent jobs
```

## Roadmap

- [x] Week 1 — API + PostgreSQL job store (state machine: pending/processing/done/failed)
- [ ] Week 2 — Redis queue + worker loop
- [ ] Week 4 — Retries, idempotency, fault tolerance (no job lost on worker crash)
- [ ] Week 6 — Observability (Prometheus + Grafana)
- [ ] Later — Docker Compose, load-test benchmarks, Kubernetes scaling
