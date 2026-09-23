import pytest

from app.models.enums import IncidentSeverity, IncidentStatus
from app.models.incidents import Incident
from app.models.services import Service
from app.repositories.incidents import IncidentRepository
from app.repositories.services import ServiceRepository

pytestmark = pytest.mark.asyncio


async def test_service_repository_get_by_name(db_session):
    repo = ServiceRepository(db_session)
    await repo.add(Service(name="redis-cache", tier="tier-1"))

    found = await repo.get_by_name("redis-cache")
    assert found is not None
    assert found.name == "redis-cache"

    missing = await repo.get_by_name("does-not-exist")
    assert missing is None


async def test_incident_repository_get_by_human_key_and_status(db_session):
    service_repo = ServiceRepository(db_session)
    service = await service_repo.add(Service(name="payment-api"))

    incident_repo = IncidentRepository(db_session)
    incident = await incident_repo.add(
        Incident(
            human_key="INC-77001",
            title="Test incident",
            severity=IncidentSeverity.P2,
            status=IncidentStatus.OPEN,
            service=service,
        )
    )

    found = await incident_repo.get_by_human_key("INC-77001")
    assert found is not None
    assert found.id == incident.id

    open_incidents = await incident_repo.list_by_status(IncidentStatus.OPEN)
    assert any(i.human_key == "INC-77001" for i in open_incidents)

    resolved_incidents = await incident_repo.list_by_status(IncidentStatus.RESOLVED)
    assert all(i.human_key != "INC-77001" for i in resolved_incidents)


async def test_incident_repository_get_with_events_eager_loads(db_session):
    from app.models.incidents import IncidentEvent

    service_repo = ServiceRepository(db_session)
    service = await service_repo.add(Service(name="order-api"))

    incident_repo = IncidentRepository(db_session)
    incident = await incident_repo.add(
        Incident(
            human_key="INC-77002",
            title="Order API incident",
            severity=IncidentSeverity.P3,
            status=IncidentStatus.OPEN,
            service=service,
        )
    )
    db_session.add(
        IncidentEvent(incident_id=incident.id, event_type="incident.created", source="test")
    )
    await db_session.flush()
    # id is app-generated (uuid4 default), so capturing it here needs no DB round trip
    incident_id = incident.id

    fetched = await incident_repo.get_with_events(incident_id)
    assert fetched is not None
    assert len(fetched.events) == 1
    assert fetched.events[0].event_type == "incident.created"


async def test_base_repository_delete(db_session):
    service_repo = ServiceRepository(db_session)
    service = await service_repo.add(Service(name="temp-service"))
    service_id = service.id

    await service_repo.delete(service)

    found = await service_repo.get(service_id)
    assert found is None
