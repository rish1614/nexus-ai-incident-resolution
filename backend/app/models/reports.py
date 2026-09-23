import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import GUID, Base, TimestampMixin, UUIDPrimaryKeyMixin


class RCAReport(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Final root-cause-analysis report for an incident (RCA Reporter agent,
    Phase 5). Stores both the human-readable narrative and a structured
    JSON representation, per spec.
    """

    __tablename__ = "rca_reports"

    incident_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    narrative_markdown: Mapped[str] = mapped_column(Text(), nullable=False)
    structured_json: Mapped[str] = mapped_column(Text(), nullable=False)  # JSON-encoded
    preventive_recommendations: Mapped[str | None] = mapped_column(Text(), nullable=True)


class AuditLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Append-only audit trail for security-relevant actions: approvals,
    executions, policy blocks, prompt-injection detections, etc.
    Deliberately separate from `IncidentEvent` (which is the investigation
    timeline) — this table exists specifically for the security/compliance
    read path described in Phase 7.
    """

    __tablename__ = "audit_logs"

    incident_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("incidents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    # user email, or "system:<agent_name>" for agent-originated audit entries
    actor: Mapped[str] = mapped_column(String(150), nullable=False)
    action: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    detail: Mapped[str | None] = mapped_column(Text(), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
