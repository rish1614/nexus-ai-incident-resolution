"""
Async SQLAlchemy engine/session setup used by the FastAPI app and
repositories. Separate from `app.services.connectivity` (Phase 1), which
does a raw one-off ping for the /ready endpoint — this module is the real
session factory used for actual queries.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config.settings import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, pool_pre_ping=True, future=True)

async_session_factory = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields a session, always closed after the request."""
    async with async_session_factory() as session:
        yield session
