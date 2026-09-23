# NEXUS — Project Plan

## What this is

NEXUS is a portfolio-grade, enterprise-style AI Operations platform. It
simulates an incident-response pipeline where AI agents triage a production
incident, retrieve grounded knowledge (RAG), determine probable root cause,
propose remediation, route risky actions through human approval, execute
safe simulated actions, validate recovery, and produce an auditable RCA
report.

All infrastructure and data are synthetic. The system never touches real
production systems, real credentials, or real company data.

## Why this architecture

| Decision | Reason |
|---|---|
| FastAPI | Async-native, typed, automatic OpenAPI docs — good fit for an API serving both a UI and agent orchestration. |
| PostgreSQL + pgvector | One database for both relational incident/audit data and vector search, instead of running a separate vector DB. Fewer moving parts for a project of this scope. |
| LangGraph | Incident resolution is a stateful, conditionally-branching workflow (parallel evidence gathering, human-approval interrupt/resume, rollback paths) — a plain prompt chain can't express that; LangGraph's explicit graph + state model can. |
| Redis | Caching, short-lived workflow state, and rate limiting — documented per use, not added speculatively. |
| React + TypeScript + Vite + Tailwind | Fast dev loop, typed UI, utility-first styling for a dense operational dashboard. |
| Docker Compose (local) → AWS ECS/Fargate (cloud) | Compose first so the system is fully runnable without any cloud account; ECS/Fargate later because it's simpler to operate and reason about than standing up Kubernetes for a project of this scope. |

Full trade-off writeups live in `docs/system-design.md` (Phase 0) as those
components are implemented.

## Phase index

| Phase | Scope | Status |
|---|---|---|
| 0 | Product & architecture docs | Pending |
| 1 | Repository bootstrap (this phase) | **Complete** |
| 2 | Database models, migrations, pgvector, seed data | Implemented — offline-verified, live-DB run pending |
| 3 | Knowledge ingestion + RAG pipeline | Not started |
| 4 | Incident simulator | Not started |
| 5 | Core agents (triage, log, RAG, RCA, remediation, risk, validation, reporter) | Not started |
| 6 | LangGraph orchestration | Not started |
| 7 | Guardrails & governance | Not started |
| 8 | Frontend dashboard | Partial (landing page only) |
| 9 | Evaluation framework | Not started |
| 10 | Observability (OpenTelemetry) | Partial (structured logging only) |
| 11 | CI/CD | Partial (lint/test/build gates only) |
| 12 | Cloud deployment (AWS) | Not started |
| 13 | Final hardening | Not started |
| 14 | Portfolio packaging | Not started |

See `IMPLEMENTATION_STATUS.md` for granular, per-task status and known
issues, updated after every phase.

## How this project is built

Each phase is implemented, tested, and reviewed before the next begins.
Nothing is left as a placeholder or fabricated — if a component can't be
verified in the current environment (e.g. no Docker daemon available for
`docker compose up`), that limitation is stated explicitly rather than
claimed as tested.
