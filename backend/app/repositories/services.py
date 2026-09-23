from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.services import Service
from app.repositories.base import BaseRepository


class ServiceRepository(BaseRepository[Service]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Service)

    async def get_by_name(self, name: str) -> Service | None:
        result = await self.session.execute(select(Service).where(Service.name == name))
        return result.scalar_one_or_none()
