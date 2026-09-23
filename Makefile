.PHONY: help up up-d down build logs backend-shell frontend-shell \
        backend-install backend-test backend-lint backend-run \
        frontend-install frontend-test frontend-build frontend-run \
        migrate seed ingest test lint

help:
	@echo "NEXUS — common developer commands"
	@echo ""
	@echo "  make up                 Start full stack via Docker Compose (foreground)"
	@echo "  make up-d               Start full stack detached (recommended — keeps your terminal free)"
	@echo "  make down               Stop the stack"
	@echo "  make build              Rebuild all Docker images"
	@echo "  make logs               Tail logs from all services"
	@echo ""
	@echo "  make backend-install    Install backend deps locally (no Docker)"
	@echo "  make backend-run        Run backend with uvicorn locally"
	@echo "  make backend-test       Run backend pytest suite"
	@echo "  make backend-lint       Run ruff + mypy on backend"
	@echo ""
	@echo "  make frontend-install   Install frontend deps locally (no Docker)"
	@echo "  make frontend-run       Run frontend with vite dev server"
	@echo "  make frontend-test      Run frontend vitest suite"
	@echo "  make frontend-build     Type-check + production build frontend"
	@echo ""
	@echo "  make migrate            Run Alembic migrations (Phase 2+)"
	@echo "  make seed               Seed synthetic data (Phase 2+)"
	@echo "  make ingest             Ingest knowledge base into pgvector (Phase 3+)"
	@echo ""
	@echo "  make test               Run backend + frontend test suites"
	@echo "  make lint               Run backend + frontend linters"

# --- Docker Compose ---
up:
	docker compose up --build

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

backend-shell:
	docker compose exec backend /bin/bash

frontend-shell:
	docker compose exec frontend /bin/sh

# --- Backend (local, no Docker) ---
backend-install:
	cd backend && pip install -e ".[dev]"

backend-run:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

backend-test:
	cd backend && python -m pytest tests/ -v

backend-lint:
	cd backend && ruff check app tests && mypy app

# --- Frontend (local, no Docker) ---
frontend-install:
	cd frontend && npm install

frontend-run:
	cd frontend && npm run dev

frontend-test:
	cd frontend && npx vitest run

frontend-build:
	cd frontend && npx tsc -b && npx vite build

# --- Data (Phase 2+) ---
# Run inside the backend container (it already has alembic/python/all deps
# installed) rather than on the host — the host machine may not have any
# Python backend environment set up at all if it's only ever been used via
# Docker. Requires the stack to already be up (`make up` in another
# terminal, or `docker compose up -d`).
migrate:
	docker compose exec backend alembic upgrade head

seed:
	docker compose exec backend python scripts/seed.py

# Detached start — use this instead of `make up` when you want your
# terminal back afterward (e.g. before running `make migrate`/`make seed`).
# `make up` runs attached/in the foreground; Ctrl+C there stops the whole
# stack, which is a common trip-up.
up-d:
	docker compose up -d --build

ingest:
	python scripts/ingest_knowledge.py

# --- Combined ---
test: backend-test frontend-test

lint: backend-lint
	cd frontend && npm run lint
