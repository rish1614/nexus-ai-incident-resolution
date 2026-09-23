from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app
from app.models import Base


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    In-memory SQLite session for model/repository tests (Phase 2+).

    Validates ORM structure, relationships, and constraints without a live
    Postgres+pgvector instance. Does NOT validate actual pgvector similarity
    search, Postgres-native ENUM enforcement, or the hand-written Alembic
    migration itself — those require a real Postgres, per
    IMPLEMENTATION_STATUS.md.
    """
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session

    await engine.dispose()
