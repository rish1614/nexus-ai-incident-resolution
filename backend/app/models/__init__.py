"""
Import every model module here so `Base.metadata` is fully populated
whenever `app.models` is imported — required for both Alembic
autogenerate and `Base.metadata.create_all()` in tests.
"""

from app.models.agents import AgentRun, AgentStep, ToolCall
from app.models.base import Base
from app.models.evaluation import EvaluationRun, ModelUsage
from app.models.governance import ActionExecution, Approval, RemediationPlan, ValidationResult
from app.models.incidents import Incident, IncidentEvent
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument
from app.models.reports import AuditLog, RCAReport
from app.models.services import Service
from app.models.telemetry import DeploymentEvent, LogRecord, MetricRecord, TraceRecord
from app.models.users import User

__all__ = [
    "Base",
    "User",
    "Service",
    "Incident",
    "IncidentEvent",
    "LogRecord",
    "MetricRecord",
    "TraceRecord",
    "DeploymentEvent",
    "KnowledgeDocument",
    "KnowledgeChunk",
    "AgentRun",
    "AgentStep",
    "ToolCall",
    "RemediationPlan",
    "Approval",
    "ActionExecution",
    "ValidationResult",
    "RCAReport",
    "AuditLog",
    "EvaluationRun",
    "ModelUsage",
]
