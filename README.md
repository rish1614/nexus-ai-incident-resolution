# NEXUS

**Enterprise Multi-Agent Incident Resolution & AI Operations Platform**

> From production alert to validated resolution using grounded, governed
> and observable AI agents.

> **Status:** Phase 1 of 14 complete (repository bootstrap). See
> [`PROJECT_PLAN.md`](./PROJECT_PLAN.md) and
> [`IMPLEMENTATION_STATUS.md`](./IMPLEMENTATION_STATUS.md) for exact,
> up-to-date progress — including what has and hasn't been verified.

## Business problem

During a production incident, engineers manually correlate logs, metrics,
traces, deployment history, and prior incidents — then decide on and
execute a fix. NEXUS automates that investigation loop with a governed,
auditable multi-agent system: triage → evidence gathering → grounded
root-cause analysis (RAG) → remediation proposal → risk-scored human
approval → simulated execution → validation → RCA report.

All data and infrastructure in this project are **synthetic**. NEXUS never
connects to a real production environment.

## Architecture (target — being built phase by phase)

```
React UI → FastAPI → LangGraph Orchestrator
                          │
        ┌─────────────────┼──────────────────┐
   Triage Agent      RAG Agent          Log Analysis Agent
        └─────────────────┼──────────────────┘
                       RCA Agent
                          │
                      Risk Agent
                          │
                    Human Approval
                     ┌────┴────┐
                 Remediation  Escalation
                     │
                Action Executor
                     │
               Validation Agent
                ┌────┴────┐
             Resolve   Rollback/Escalate
                     │
               RCA Reporter
```

Knowledge layer: runbooks, past incidents, service docs, architecture docs,
and policies are chunked, embedded, and stored in PostgreSQL + pgvector,
then retrieved with metadata filtering and citation tracking.

## Tech stack

- **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy, Alembic
- **AI:** LangChain, LangGraph, pluggable LLM/embedding providers *(Phase 5+)*
- **Frontend:** React, TypeScript, Vite, Tailwind CSS
- **Data:** PostgreSQL + pgvector, Redis
- **Infra:** Docker, Docker Compose, GitHub Actions
- **Observability:** OpenTelemetry, structured JSON logging *(expanded in Phase 10)*
- **Cloud target:** AWS (ECS/Fargate, RDS, ElastiCache) *(Phase 12)*

## Repository structure

```
nexus/
├── backend/          FastAPI app, agents, RAG, graph orchestration
├── frontend/          React + TypeScript dashboard
├── data/              Synthetic knowledge base, incidents, simulator data
├── evaluation/        RAG/agent/safety evaluation datasets & runners
├── infrastructure/    Docker, AWS IaC, monitoring config
├── scripts/           Seed, ingestion, smoke-test scripts
├── docs/              Architecture, security, evaluation, deployment docs
└── .github/workflows/ CI/CD pipelines
```

## Running locally

**Prerequisites:** Docker + Docker Compose, or Python 3.12 + Node 20 for
running backend/frontend without containers.

### Option A — Docker Compose (recommended once Docker is available)

```bash
git clone <this-repo>
cd nexus
cp .env.example .env
make up-d
```

`make up-d` starts the stack **detached** (keeps your terminal free for
the next commands). If you use plain `make up` instead, it runs attached —
pressing Ctrl+C there stops the entire stack, which is easy to trip over.

Once the containers are healthy, initialize the database (`migrate`/`seed`
run *inside* the backend container, which already has all Python deps
installed — no local Python setup needed on your machine):

```bash
make migrate   # applies backend/alembic/versions/0001_initial_schema.py
make seed      # inserts synthetic services, users, and a linked incident
```

- Backend: http://localhost:8000 (docs at `/docs`)
- Frontend: http://localhost:5173
- Postgres: localhost:5433 (container-internal port stays 5432; host mapping is offset to avoid clashing with a locally-installed Postgres — override via `POSTGRES_HOST_PORT` in `.env` if needed)
- Redis: localhost:6380 (same reasoning; override via `REDIS_HOST_PORT`)

> **Verified:** `make up` was run end-to-end on a real machine — all 4
> containers built and reported healthy, `/ready` returned `200` against
> live Postgres+Redis. `make migrate` / `make seed` are written and
> reviewed (the migration's SQL was verified via Alembic's offline `--sql`
> render) but not yet run against a live database — see
> `IMPLEMENTATION_STATUS.md`. If `docker compose up` fails with "port is
> already allocated," another process is using that port — stop it or
> change `POSTGRES_HOST_PORT` / `REDIS_HOST_PORT` in `.env`.

### Option B — Run backend/frontend directly (verified in development)

```bash
# Backend
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload
# -> http://localhost:8000/health

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
# -> http://localhost:5173
```

This path was actually run and verified during development: backend
`/health` returns `200`, `/ready` correctly reports `503` with a structured
payload when Postgres/Redis aren't running, and the frontend builds and
type-checks cleanly.

## Environment variables

See [`.env.example`](./.env.example) for the full list. Copy it to `.env`
before running. Never commit a real `.env` file.

## API

Once the backend is running:

- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI schema: `http://localhost:8000/openapi.json`

Current endpoints (Phase 1): `GET /health`, `GET /ready`. Incident,
knowledge, agent, and evaluation endpoints are added in later phases per
`PROJECT_PLAN.md`.

## Testing

```bash
make test           # backend + frontend
make backend-test    # pytest, backend/tests/
make frontend-test   # vitest, frontend/tests/
```

## Security

No secrets are committed to this repository. All API keys and credentials
are loaded from environment variables (`.env`, gitignored). A full threat
model and security review land in Phase 7 / `docs/security.md` and
`docs/threat-model.md`.

## Limitations (current)

- Phases 1–2 are implemented (repository bootstrap; database models,
  migrations, and seed data). There are no agents, no RAG pipeline, and no
  incident workflow yet — those start at Phase 3.
- The Alembic migration's SQL was verified via Alembic's offline `--sql`
  render (confirms valid Postgres DDL) but has not yet been applied
  (`alembic upgrade head`) against a live Postgres+pgvector instance. Run
  `make migrate && make seed` after `make up` and confirm — see
  `IMPLEMENTATION_STATUS.md` for exactly what's verified.

## Roadmap

See [`PROJECT_PLAN.md`](./PROJECT_PLAN.md) for the full 14-phase plan.

## License

See [`LICENSE`](./LICENSE).
