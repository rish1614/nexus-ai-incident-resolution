import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import GUID, Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import IncidentSeverity, IncidentStatus

if TYPE_CHECKING:
    from app.models.services import Service


class Incident(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    The central record an investigation revolves around. `human_key` is the
    display id (e.g. "INC-10042") shown in the UI and RCA reports; `id` is
    the internal UUID used for all foreign keys.
    """

    __tablename__ = "incidents"

    human_key: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text(), nullable=True)
    severity: Mapped[IncidentSeverity] = mapped_column(
        Enum(IncidentSeverity, name="incident_severity").with_variant(String(10), "sqlite"),
        nullable=False,
    )
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus, name="incident_status").with_variant(String(30), "sqlite"),
        nullable=False,
        default=IncidentStatus.OPEN,
    )
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    customer_impact: Mapped[str | None] = mapped_column(Text(), nullable=True)

    service_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    service: Mapped["Service"] = relationship(back_populates="incidents")

    events: Mapped[list["IncidentEvent"]] = relationship(
        back_populates="incident", cascade="all, delete-orphan", order_by="IncidentEvent.created_at"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Incident {self.human_key} ({self.severity}/{self.status})>"


class IncidentEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Auditable timeline entry for an incident — e.g. `incident.triaged`,
    `approval.granted`. This is the event log described in the event-driven
    flow section of the spec; it is intentionally a simple append-only
    table rather than a message broker, since the workflow so far is
    single-process (LangGraph, Phase 6) rather than distributed.
    """

    __tablename__ = "incident_events"

    incident_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    incident: Mapped["Incident"] = relationship(back_populates="events")

    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[str | None] = mapped_column(Text(), nullable=True)  # JSON-encoded

    def __repr__(self) -> str:  # pragma: no cover
        return f"<IncidentEvent {self.event_type} @ {self.incident_id}>"
