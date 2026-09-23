import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import GUID, Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AgentRunStatus

if TYPE_CHECKING:
    pass


class AgentRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    One execution of a single agent (e.g. one call to the RCA Agent) within
    an incident's investigation. This is the row the Agent Trace UI (Phase
    8) reads to show per-step timing, tokens, and cost.
    """

    __tablename__ = "agent_runs"

    incident_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    prompt_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[AgentRunStatus] = mapped_column(
        Enum(AgentRunStatus, name="agent_run_status").with_variant(String(20), "sqlite"),
        nullable=False,
        default=AgentRunStatus.RUNNING,
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    estimated_cost_usd: Mapped[float | None] = mapped_column(Float(), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text(), nullable=True)

    steps: Mapped[list["AgentStep"]] = relationship(
        back_populates="agent_run", cascade="all, delete-orphan", order_by="AgentStep.created_at"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AgentRun {self.agent_name} ({self.status})>"


class AgentStep(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A discrete step within an agent run (e.g. 'retrieve context', 'call LLM', 'parse output')."""

    __tablename__ = "agent_steps"

    agent_run_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_run: Mapped["AgentRun"] = relationship(back_populates="steps")

    step_name: Mapped[str] = mapped_column(String(150), nullable=False)
    duration_ms: Mapped[float | None] = mapped_column(Float(), nullable=True)
    input_summary: Mapped[str | None] = mapped_column(Text(), nullable=True)
    output_summary: Mapped[str | None] = mapped_column(Text(), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text(), nullable=True)


class ToolCall(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A single tool/function invocation made by an agent (Phase 5+)."""

    __tablename__ = "tool_calls"

    agent_run_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    arguments: Mapped[str | None] = mapped_column(Text(), nullable=True)  # JSON-encoded
    result: Mapped[str | None] = mapped_column(Text(), nullable=True)  # JSON-encoded
    succeeded: Mapped[bool] = mapped_column(default=True, nullable=False)
    duration_ms: Mapped[float | None] = mapped_column(Float(), nullable=True)
