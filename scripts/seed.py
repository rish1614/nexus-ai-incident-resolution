"""
Seed synthetic services, users, and a first batch of cross-linked
incidents into the database.

Usage:
    make seed
    # or: python scripts/seed.py   (run from backend/, with .env configured)

This connects to `Settings.database_url` — i.e. a real Postgres instance.
It is not run against SQLite; the SQLite fallback in app/models/base.py
exists only for the backend test suite, not for this script.
"""

import asyncio
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from passlib.context import CryptContext  # noqa: E402
from sqlalchemy import select  # noqa: E402

from app.models import (  # noqa: E402
    DeploymentEvent,
    Incident,
    IncidentEvent,
    Service,
    User,
)
from app.models.enums import IncidentSeverity, IncidentStatus, UserRole  # noqa: E402
from app.models.session import async_session_factory  # noqa: E402

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SERVICES = [
    {"name": "payment-api", "owner_team": "payments", "tier": "tier-1",
     "description": "Handles checkout payment authorization and capture.",
     "depends_on": "database,redis-cache,auth-service"},
    {"name": "order-api", "owner_team": "commerce", "tier": "tier-1",
     "description": "Order creation and lifecycle management.",
     "depends_on": "database,payment-api,inventory-api"},
    {"name": "inventory-api", "owner_team": "commerce", "tier": "tier-2",
     "description": "Tracks product stock levels across warehouses.",
     "depends_on": "database"},
    {"name": "auth-service", "owner_team": "platform", "tier": "tier-1",
     "description": "Authentication and session issuance for all services.",
     "depends_on": "database,redis-cache"},
    {"name": "notification-service", "owner_team": "platform", "tier": "tier-3",
     "description": "Sends transactional emails and push notifications.",
     "depends_on": "order-api"},
    {"name": "database", "owner_team": "platform", "tier": "tier-1",
     "description": "Primary PostgreSQL cluster (simulated).", "depends_on": None},
    {"name": "redis-cache", "owner_team": "platform", "tier": "tier-1",
     "description": "Shared Redis cache/session store (simulated).", "depends_on": None},
]

USERS = [
    {"email": "viewer@nexus.local", "display_name": "Vik Viewer", "role": UserRole.VIEWER},
    {"email": "operator@nexus.local", "display_name": "Olive Operator", "role": UserRole.OPERATOR},
    {"email": "manager@nexus.local", "display_name": "Morgan Manager", "role": UserRole.INCIDENT_MANAGER},
    {"email": "admin@nexus.local", "display_name": "Ada Admin", "role": UserRole.ADMIN},
]

DEV_PASSWORD = "nexus-dev-only-not-for-production"


async def seed_services(session) -> dict[str, Service]:
    services: dict[str, Service] = {}
    for spec in SERVICES:
        result = await session.execute(select(Service).where(Service.name == spec["name"]))
        existing = result.scalar_one_or_none()
        if existing:
            services[spec["name"]] = existing
            continue
        service = Service(**spec)
        session.add(service)
        services[spec["name"]] = service
    await session.flush()
    return services


async def seed_users(session) -> None:
    for spec in USERS:
        result = await session.execute(select(User).where(User.email == spec["email"]))
        if result.scalar_one_or_none():
            continue
        session.add(
            User(
                email=spec["email"],
                display_name=spec["display_name"],
                role=spec["role"],
                hashed_password=pwd_context.hash(DEV_PASSWORD),
            )
        )
    await session.flush()


async def seed_incidents(session, services: dict[str, Service]) -> None:
    now = datetime.now(UTC)

    result = await session.execute(select(Incident).where(Incident.human_key == "INC-10001"))
    if result.scalar_one_or_none():
        return  # already seeded

    payment_api = services["payment-api"]

    incident = Incident(
        human_key="INC-10001",
        title="Payment API elevated error rate — database pool exhaustion",
        summary=(
            "payment-api began returning HTTP 500s at ~14:02 UTC. Error rate "
            "climbed from baseline (<0.5%) to 38% within 6 minutes."
        ),
        severity=IncidentSeverity.P1,
        status=IncidentStatus.RESOLVED,
        category="database",
        customer_impact="Checkout failures for a subset of users during the incident window.",
        service=payment_api,
    )
    session.add(incident)
    await session.flush()

    session.add_all(
        [
            IncidentEvent(
                incident_id=incident.id,
                event_type="incident.created",
                source="simulator",
                payload='{"trigger": "database-pool-exhaustion"}',
            ),
            IncidentEvent(
                incident_id=incident.id,
                event_type="incident.triaged",
                source="triage_agent",
                payload='{"severity": "P1", "category": "database"}',
            ),
            IncidentEvent(
                incident_id=incident.id,
                event_type="incident.resolved",
                source="validation_agent",
                payload='{"outcome": "RESOLVED"}',
            ),
        ]
    )

    session.add(
        DeploymentEvent(
            service_id=payment_api.id,
            deployed_at=now - timedelta(hours=2),
            version="v2.14.3",
            deployed_by="ci-pipeline",
            change_summary="Reduced DB connection pool max_size from 50 to 20 in config rollout.",
            is_rollback=False,
        )
    )

    await session.flush()


async def main() -> None:
    async with async_session_factory() as session:
        async with session.begin():
            services = await seed_services(session)
            await seed_users(session)
            await seed_incidents(session, services)
    print(f"Seed complete: {len(SERVICES)} services, {len(USERS)} users, 1 cross-linked incident.")


if __name__ == "__main__":
    asyncio.run(main())
