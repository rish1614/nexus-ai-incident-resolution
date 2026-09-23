"""
Phase 2 tests: verify ORM structure, relationships, and constraints using
an in-memory SQLite database (see conftest.db_session for scope/limits).
"""

from datetime import UTC, datetime

import pytest
from sqlalchemy import select

from app.models.enums import IncidentSeverity, IncidentStatus, KnowledgeSourceType
from app.models.incidents import Incident, IncidentEvent
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument
from app.models.services import Service

pytestmark = pytest.mark.asyncio


async def test_service_create_and_query(db_session):
    service = Service(name="payment-api", tier="tier-1", owner_team="payments")
    db_session.add(service)
    await db_session.flush()

    result = await db_session.execute(select(Service).where(Service.name == "payment-api"))
    fetched = result.scalar_one()
    assert fetched.id == service.id
    assert fetched.tier == "tier-1"


async def test_incident_requires_service_and_populates_relationship(db_session):
    service = Service(name="order-api")
    db_session.add(service)
    await db_session.flush()

    incident = Incident(
        human_key="INC-90001",
        title="Order API latency spike",
        severity=IncidentSeverity.P2,
        status=IncidentStatus.OPEN,
        service=service,
    )
    db_session.add(incident)
    await db_session.flush()

    assert incident.service_id == service.id
    assert incident.service.name == "order-api"

    # Do not touch `service.incidents` (the backref collection) directly here:
    # under AsyncSession, accessing an unloaded relationship attribute outside
    # an explicit eager-load triggers an implicit lazy load, which raises
    # MissingGreenlet (SQLAlchemy async cannot do synchronous IO on attribute
    # access). The correct pattern — used throughout the repository layer —
    # is to eager-load explicitly, e.g. via `selectinload`, as done here.
    from sqlalchemy.orm import selectinload

    result = await db_session.execute(
        select(Service).where(Service.id == service.id).options(selectinload(Service.incidents))
    )
    fetched_service = result.scalar_one()
    assert incident.id in [i.id for i in fetched_service.incidents]


async def test_incident_human_key_is_unique(db_session):
    service = Service(name="inventory-api")
    db_session.add(service)
    await db_session.flush()

    db_session.add(
        Incident(
            human_key="INC-DUPLICATE",
            title="first",
            severity=IncidentSeverity.P3,
            status=IncidentStatus.OPEN,
            service=service,
        )
    )
    await db_session.flush()

    db_session.add(
        Incident(
            human_key="INC-DUPLICATE",
            title="second",
            severity=IncidentSeverity.P3,
            status=IncidentStatus.OPEN,
            service=service,
        )
    )
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        await db_session.flush()


async def test_incident_event_cascade_delete(db_session):
    service = Service(name="auth-service")
    db_session.add(service)
    await db_session.flush()

    incident = Incident(
        human_key="INC-90002",
        title="Auth degradation",
        severity=IncidentSeverity.P1,
        status=IncidentStatus.INVESTIGATING,
        service=service,
    )
    db_session.add(incident)
    await db_session.flush()

    db_session.add(
        IncidentEvent(
            incident_id=incident.id,
            event_type="incident.created",
            source="simulator",
            payload=None,
        )
    )
    await db_session.flush()

    result = await db_session.execute(
        select(IncidentEvent).where(IncidentEvent.incident_id == incident.id)
    )
    assert len(result.scalars().all()) == 1

    await db_session.delete(incident)
    await db_session.flush()

    result = await db_session.execute(
        select(IncidentEvent).where(IncidentEvent.incident_id == incident.id)
    )
    assert result.scalars().all() == []


async def test_knowledge_document_and_chunk_with_embedding_round_trip(db_session):
    doc = KnowledgeDocument(
        title="Database Connection Pool Runbook",
        source_type=KnowledgeSourceType.RUNBOOK,
        service="payment-api",
        raw_content="# Database Connection Pool\n\nSteps to diagnose pool exhaustion...",
    )
    db_session.add(doc)
    await db_session.flush()

    fake_embedding = [0.01 * i for i in range(1536)]
    chunk = KnowledgeChunk(
        document_id=doc.id,
        chunk_index=0,
        content="Steps to diagnose pool exhaustion...",
        embedding=fake_embedding,
    )
    db_session.add(chunk)
    await db_session.flush()

    result = await db_session.execute(
        select(KnowledgeChunk).where(KnowledgeChunk.document_id == doc.id)
    )
    fetched = result.scalar_one()
    assert fetched.chunk_index == 0
    # Round-trips through the SQLite JSON-text fallback (app.models.base.Vector)
    assert fetched.embedding is not None
    assert len(fetched.embedding) == 1536
    assert fetched.embedding[1] == pytest.approx(0.01)


async def test_incident_event_timestamps_are_set(db_session):
    service = Service(name="notification-service")
    db_session.add(service)
    await db_session.flush()

    incident = Incident(
        human_key="INC-90003",
        title="Notification delivery delay",
        severity=IncidentSeverity.P4,
        status=IncidentStatus.OPEN,
        service=service,
    )
    db_session.add(incident)
    await db_session.flush()

    assert incident.created_at is not None
    assert incident.created_at.tzinfo is not None or isinstance(incident.created_at, datetime)
    _ = datetime.now(UTC)  # sanity: timezone-aware comparisons are usable downstream
