"""
Declarative base and shared mixins for all ORM models.

Design notes:
- UUID primary keys everywhere (per project spec), generated app-side with
  `uuid4` so inserts don't depend on a database-specific default function.
- `TimestampMixin` gives every table `created_at` / `updated_at`.
- `Vector` below wraps pgvector's native column type for Postgres, with a
  JSON-text fallback for any other dialect. That fallback exists solely so
  this project's test suite can run against SQLite in environments without
  a live Postgres+pgvector instance — production always runs on Postgres
  and always uses the real `pgvector.sqlalchemy.Vector` type. It is not a
  simulation of vector search; SQLite-backed tests never assert on
  similarity ordering, only on round-trip storage of model relationships.
"""

import json
import uuid
from datetime import UTC, datetime

from pgvector.sqlalchemy import Vector as PgVector
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import Text, TypeDecorator, TypeEngine


class Base(AsyncAttrs, DeclarativeBase):
    """
    Inherits `AsyncAttrs` so any relationship can be safely lazy-loaded from
    async code via `await obj.awaitable_attrs.some_relationship` — plain
    attribute access on an unloaded relationship raises `MissingGreenlet`
    under `AsyncSession`. Prefer eager-loading (`selectinload`) in
    repository queries where the access pattern is known in advance;
    reach for `awaitable_attrs` only for the ad-hoc cases.
    """

    pass


def new_uuid() -> uuid.UUID:
    return uuid.uuid4()


class GUID(TypeDecorator):
    """
    Cross-dialect UUID column.

    Postgres: native UUID type, Python-side `uuid.UUID` objects in and out.
    Any other dialect (SQLite, used only by this project's test suite):
    stored as a 36-character string, with explicit str<->UUID conversion
    on bind/result — `.with_variant(Text(), "sqlite")` alone is not enough
    here, since the sqlite3 DBAPI cannot bind a raw `uuid.UUID` object.
    """

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect) -> TypeEngine:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(Text(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        if not isinstance(value, uuid.UUID):
            return str(uuid.UUID(str(value)))
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None or dialect.name == "postgresql":
            return value
        return uuid.UUID(value)


class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class Vector(TypeDecorator):
    """Postgres: native pgvector column. Other dialects (tests only): JSON text."""

    impl = Text
    cache_ok = True

    def __init__(self, dim: int, *args, **kwargs) -> None:
        self.dim = dim
        super().__init__(*args, **kwargs)

    def load_dialect_impl(self, dialect) -> TypeEngine:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PgVector(self.dim))
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None or dialect.name == "postgresql":
            return value
        return json.dumps(list(value))

    def process_result_value(self, value, dialect):
        if value is None or dialect.name == "postgresql":
            return value
        return json.loads(value)
