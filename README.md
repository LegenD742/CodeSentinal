# CodeSentinel

Autonomous, AI-powered GitHub Pull Request review system. Combines
static analysis (Tree-sitter, Semgrep, Bandit, ESLint) with a LangGraph
multi-agent LLM reasoning layer — specialist agents for bugs, security,
performance and code quality, verified by a Critic Agent — and posts
structured, evidence-backed findings back to the PR as inline GitHub
comments plus an overall risk assessment.

Runs almost entirely locally: Postgres and Redis in two small Docker
containers (nothing else is containerized), everything else — backend,
worker, frontend, static analyzers — runs natively on your machine, with
Ollama (`llama3.2:3b` + `nomic-embed-text`) for the LLM, no cloud API
keys. CodeSentinel reviews pull requests; it never merges them.

## What to install

| Tool | Why | Check |
|---|---|---|
| Python 3.11+ | Backend + worker | `python3 --version` |
| Node.js 20+ | Frontend + ESLint analyzer | `node --version` |
| Docker Desktop (or Docker Engine + Compose) | Runs Postgres+pgvector and Redis only — nothing else is containerized | `docker --version` |
| Ollama | Already installed with `llama3.2:3b` + `nomic-embed-text` | `ollama list` |

Install links:
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/
- Docker: https://www.docker.com/products/docker-desktop/

## One-time setup

**1. Start Postgres + Redis** (leave running — this is the only Docker involved)

```bash
docker compose -f infra/docker-compose.yml up -d
```

This starts a `pgvector/pgvector:pg16` container (auto-creates the
`codesentinel` user/database and loads `infra/postgres/init_pgvector.sql`
on first run — no manual `psql` commands needed) and a plain `redis:7`
container. Check both are healthy:
```bash
docker compose -f infra/docker-compose.yml ps
```
Both should show `healthy`. To stop them later: `docker compose -f infra/docker-compose.yml down` (add `-v` to also wipe the database volume).

**2. Start Ollama** (skip if it's already running)

```bash
ollama serve
```

**3. Backend: create a virtual environment and install dependencies**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

`.env` already points at `localhost` for Postgres/Redis/Ollama and
`llama3.2:3b` / `nomic-embed-text` — no edits needed to just try it out.

**4. Install the static analyzers the backend shells out to**

```bash
pip install semgrep bandit
npm install -g eslint@8
```

**5. Frontend: install dependencies**

```bash
cd ../frontend
npm install
```

## Running it (3 terminals, no scripts)

**Terminal 1 — backend API**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```
→ http://localhost:8000/docs

**Terminal 2 — Celery worker** (runs the actual review pipeline)
```bash
cd backend
source venv/bin/activate
celery -A app.workers.celery_app worker --loglevel=info
```

**Terminal 3 — frontend**
```bash
cd frontend
npm run dev
```
→ http://localhost:5173

(Postgres and Redis are already running in the background via Docker
from step 1 — no dedicated terminal needed for them. Ollama also
typically runs as a background service/app. So 3 terminals is really
all you need.)

## See it working without GitHub

```bash
cd backend
source venv/bin/activate
PYTHONPATH=. python ../scripts/seed_data.py
```
Refresh http://localhost:5173 — you'll see a fake repo/PR/review run
with findings, confirming the DB, API and frontend are wired correctly.

## Wiring up a real GitHub repo
See the GitHub App setup steps (App creation, webhook URL via a tunnel
like `ngrok http 8000`, permissions, private key) — ask if you want
these written out again; they're unchanged from before and don't depend
on Docker.

## Running tests
```bash
cd backend
source venv/bin/activate
pytest tests/unit -v
```

## Repository layout
- `backend/app/graph/` — LangGraph wiring (specialist agents → critic → aggregator → commenter)
- `backend/app/agents/` — the four specialist agents + critic agent + prompts
- `backend/app/analyzers/` — Semgrep/Bandit/ESLint/Tree-sitter wrappers
- `backend/app/rag/` — pgvector chunking/embedding/retrieval
- `backend/app/github_integration/` — GitHub App auth, diff parsing, comment posting
- `backend/app/core/llm_client.py` — the one place that talks to Ollama
- `frontend/src/` — React dashboard (repos → PRs → review runs → findings)
- `infra/postgres/init_pgvector.sql` — database schema
- `infra/github-actions/ci.yml` — optional CI (tests + frontend build)
