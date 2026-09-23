import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import GUID, Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ApprovalDecision, RiskLevel, ValidationOutcome

if TYPE_CHECKING:
    pass


class RemediationPlan(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    A proposed remediation action for an incident (Remediation Agent output,
    Phase 5). Every plan carries its own risk level, rollback action, and
    validation criteria — no plan executes without going through
    `Approval` first if its risk level requires it (Phase 7 governance).
    """

    __tablename__ = "remediation_plans"

    incident_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    target_service: Mapped[str] = mapped_column(String(100), nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, name="risk_level").with_variant(String(10), "sqlite"), nullable=False
    )
    expected_effect: Mapped[str | None] = mapped_column(Text(), nullable=True)
    rollback_action: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # JSON-encoded list
    validation_criteria: Mapped[str | None] = mapped_column(Text(), nullable=True)

    approvals: Mapped[list["Approval"]] = relationship(
        back_populates="remediation_plan", cascade="all, delete-orphan"
    )
    executions: Mapped[list["ActionExecution"]] = relationship(
        back_populates="remediation_plan", cascade="all, delete-orphan"
    )


class Approval(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    A human decision on a RemediationPlan. Every field required by the
    spec's human-in-the-loop section is captured: who, when, what action,
    what reason, and — once execution completes — the outcome.
    """

    __tablename__ = "approvals"

    remediation_plan_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("remediation_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    remediation_plan: Mapped["RemediationPlan"] = relationship(back_populates="approvals")

    approver_user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    decision: Mapped[ApprovalDecision] = mapped_column(
        Enum(ApprovalDecision, name="approval_decision").with_variant(String(30), "sqlite"),
        nullable=False,
    )
    reason: Mapped[str | None] = mapped_column(Text(), nullable=True)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ActionExecution(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    A record of the simulated Action Executor (Phase 4/7) actually running
    an approved remediation action. Never records arbitrary shell commands
    — `action` must correspond to an allowlisted operation.
    """

    __tablename__ = "action_executions"

    remediation_plan_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("remediation_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    remediation_plan: Mapped["RemediationPlan"] = relationship(back_populates="executions")

    executed_action: Mapped[str] = mapped_column(String(100), nullable=False)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    succeeded: Mapped[bool] = mapped_column(nullable=False)
    output_summary: Mapped[str | None] = mapped_column(Text(), nullable=True)

    validation_result: Mapped["ValidationResult | None"] = relationship(
        back_populates="action_execution", uselist=False, cascade="all, delete-orphan"
    )


class ValidationResult(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Before/after comparison produced by the Validation Agent (Phase 5).
    A remediation is never considered successful merely because the action
    executed without error — this table is where actual before/after
    health is recorded and the final outcome decided.
    """

    __tablename__ = "validation_results"

    action_execution_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("action_executions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    action_execution: Mapped["ActionExecution"] = relationship(back_populates="validation_result")

    outcome: Mapped[ValidationOutcome] = mapped_column(
        Enum(ValidationOutcome, name="validation_outcome").with_variant(String(30), "sqlite"),
        nullable=False,
    )
    before_metrics: Mapped[str | None] = mapped_column(Text(), nullable=True)  # JSON-encoded
    after_metrics: Mapped[str | None] = mapped_column(Text(), nullable=True)  # JSON-encoded
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
