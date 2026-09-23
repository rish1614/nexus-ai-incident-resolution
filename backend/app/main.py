"""
NEXUS backend entrypoint.

Phase 1: exposes health/readiness endpoints and wires up base app
configuration (CORS, structured logging). Business routers (incidents,
knowledge, agents, ...) are added in later phases.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config.settings import get_settings
from app.observability.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("nexus_backend_startup", extra={"app_env": settings.app_env})
    yield
    logger.info("nexus_backend_shutdown")


app = FastAPI(
    title="NEXUS",
    description="Enterprise Multi-Agent Incident Resolution & AI Operations Platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(api_router, prefix=settings.api_v1_prefix)
