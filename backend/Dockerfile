# syntax=docker/dockerfile:1
#
# Build context for this Dockerfile is the REPO ROOT (see docker-compose.yml:
# `build.context: .`, `build.dockerfile: backend/Dockerfile`), not ./backend.
# This lets the image also include the top-level `scripts/` directory
# (seed.py etc.) alongside the backend app, without a Docker `COPY ../`
# (which Docker does not allow — build contexts cannot reach outside
# themselves) forcing scripts into a separate, harder-to-run image.

# ---------- Stage 1: builder ----------
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/pyproject.toml ./
# Install into an isolated prefix so it can be copied into the runtime stage
RUN pip install --no-cache-dir --prefix=/install .

# ---------- Stage 2: runtime ----------
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r nexus && useradd -r -g nexus nexus

WORKDIR /app

COPY --from=builder /install /usr/local
COPY backend/app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini ./alembic.ini
COPY scripts ./scripts

# scripts/seed.py imports `app.*` — with WORKDIR /app, plain `python
# scripts/seed.py` only puts scripts/ on sys.path[0], not /app itself, so
# the top-level `app` package wouldn't resolve without this.
ENV PYTHONPATH=/app

RUN chown -R nexus:nexus /app
USER nexus

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
