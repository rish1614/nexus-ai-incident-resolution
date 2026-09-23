from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.incidents import Incident


class Service(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    A service in the simulated infrastructure inventory (e.g. payment-api,
    order-api). Incidents, logs, metrics, and deployments all reference a
    service by id. Populated by the seed script (Phase 2) and the incident
    simulator (Phase 4).
    """

    __tablename__ = "services"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    owner_team: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tier: Mapped[str] = mapped_column(String(20), nullable=False, default="tier-2")
    # Comma-separated service names this service depends on. A proper
    # many-to-many edge table is a reasonable future improvement once the
    # simulator (Phase 4) needs to traverse dependency graphs programmatically.
    depends_on: Mapped[str | None] = mapped_column(Text(), nullable=True)

    incidents: Mapped[list["Incident"]] = relationship(
        back_populates="service", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Service {self.name}>"
