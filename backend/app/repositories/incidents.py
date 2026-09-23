from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import IncidentStatus
from app.models.incidents import Incident
from app.repositories.base import BaseRepository


class IncidentRepository(BaseRepository[Incident]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Incident)

    async def get_by_human_key(self, human_key: str) -> Incident | None:
        result = await self.session.execute(
            select(Incident).where(Incident.human_key == human_key)
        )
        return result.scalar_one_or_none()

    async def list_by_status(self, status: IncidentStatus, limit: int = 50) -> list[Incident]:
        result = await self.session.execute(
            select(Incident).where(Incident.status == status).limit(limit)
        )
        return list(result.scalars().all())

    async def get_with_events(self, id_) -> Incident | None:
        result = await self.session.execute(
            select(Incident).where(Incident.id == id_).options(selectinload(Incident.events))
        )
        return result.scalar_one_or_none()
