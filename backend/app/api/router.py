"""
Top-level API router. Individual resource routers (incidents, knowledge,
agents, etc.) are added here in later phases as they're implemented.
"""

from fastapi import APIRouter

from app.api.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router)

# Phase 2+: incidents, knowledge, agents, metrics, evaluations, simulator
# routers will be registered here as they are implemented.
