"""
Lightweight connectivity checks used by the /ready endpoint.

Phase 1 has no ORM models yet (those arrive in Phase 2), so these checks
open a raw connection/ping rather than going through SQLAlchemy sessions
or repositories.
"""

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config.settings import get_settings

logger = logging.getLogger(__name__)


async def check_database() -> tuple[bool, str]:
    """Attempt a raw SELECT 1 against the configured database."""
    settings = get_settings()
    try:
        engine = create_async_engine(settings.database_url, pool_pre_ping=True)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
        return True, "connected"
    except Exception as exc:  # noqa: BLE001 - we want to report any failure reason
        logger.warning("database_connectivity_check_failed", extra={"error": str(exc)})
        return False, str(exc)


async def check_redis() -> tuple[bool, str]:
    """Attempt a PING against the configured Redis instance."""
    settings = get_settings()
    try:
        import redis.asyncio as redis_asyncio

        client = redis_asyncio.from_url(settings.redis_url, socket_connect_timeout=2)
        pong = await client.ping()
        await client.aclose()
        return bool(pong), "connected"
    except Exception as exc:  # noqa: BLE001
        logger.warning("redis_connectivity_check_failed", extra={"error": str(exc)})
        return False, str(exc)
