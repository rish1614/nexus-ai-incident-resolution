"""
Health and readiness endpoints.

/health -> liveness: process is up. Never depends on external services.
/ready  -> readiness: process is up AND its critical dependencies
           (database, redis) are reachable. Used by orchestrators / compose
           healthchecks to gate traffic.
"""

from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from app.services.connectivity import check_database, check_redis

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    service: str = "nexus-backend"


class DependencyStatus(BaseModel):
    healthy: bool
    detail: str


class ReadyResponse(BaseModel):
    status: str
    dependencies: dict[str, DependencyStatus]


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Liveness probe — always returns healthy if the process can respond."""
    return HealthResponse(status="healthy")


@router.get("/ready", response_model=ReadyResponse)
async def ready(response: Response) -> ReadyResponse:
    """Readiness probe — checks database and redis connectivity."""
    db_ok, db_detail = await check_database()
    redis_ok, redis_detail = await check_redis()

    all_healthy = db_ok and redis_ok
    response.status_code = (
        status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return ReadyResponse(
        status="ready" if all_healthy else "not_ready",
        dependencies={
            "database": DependencyStatus(healthy=db_ok, detail=db_detail),
            "redis": DependencyStatus(healthy=redis_ok, detail=redis_detail),
        },
    )
