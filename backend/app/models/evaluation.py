import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import GUID, Base, TimestampMixin, UUIDPrimaryKeyMixin


class EvaluationRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    One execution of the evaluation suite (Phase 9) — RAG relevance,
    groundedness, agent task success, safety compliance, etc. Stores
    machine-readable metrics per spec; never contains fabricated scores —
    populated only by `evaluation/runners/*` actually executing.
    """

    __tablename__ = "evaluation_runs"

    suite_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    dataset_name: Mapped[str] = mapped_column(String(100), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_cases: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    passed_cases: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    metrics_json: Mapped[str | None] = mapped_column(Text(), nullable=True)  # JSON-encoded


class ModelUsage(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Per-call LLM/embedding usage record, for cost and latency tracking
    (Phase 5/10). Cost is only ever computed from actual configured
    provider pricing — never a placeholder value.
    """

    __tablename__ = "model_usage"

    agent_run_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("agent_runs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    estimated_cost_usd: Mapped[float | None] = mapped_column(Float(), nullable=True)
    latency_ms: Mapped[float | None] = mapped_column(Float(), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
