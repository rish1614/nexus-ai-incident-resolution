"""
Shared enums. Stored as native Postgres ENUM types where practical, with
plain string columns as the SQLite fallback (handled per-column via
`.with_variant`) so the same model code works in both the test suite and
production.
"""

import enum


class UserRole(enum.StrEnum):
    VIEWER = "VIEWER"
    OPERATOR = "OPERATOR"
    INCIDENT_MANAGER = "INCIDENT_MANAGER"
    ADMIN = "ADMIN"


class IncidentSeverity(enum.StrEnum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class IncidentStatus(enum.StrEnum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    REMEDIATING = "REMEDIATING"
    VALIDATING = "VALIDATING"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"
    ROLLED_BACK = "ROLLED_BACK"


class RiskLevel(enum.StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    BLOCKED = "BLOCKED"


class ApprovalDecision(enum.StrEnum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MORE_EVIDENCE_REQUESTED = "MORE_EVIDENCE_REQUESTED"


class ValidationOutcome(enum.StrEnum):
    RESOLVED = "RESOLVED"
    PARTIALLY_RESOLVED = "PARTIALLY_RESOLVED"
    FAILED = "FAILED"
    ROLLBACK_REQUIRED = "ROLLBACK_REQUIRED"
    ESCALATE = "ESCALATE"


class AgentRunStatus(enum.StrEnum):
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"


class KnowledgeSourceType(enum.StrEnum):
    RUNBOOK = "RUNBOOK"
    SERVICE_DOC = "SERVICE_DOC"
    ARCHITECTURE = "ARCHITECTURE"
    INCIDENT_HISTORY = "INCIDENT_HISTORY"
    POLICY = "POLICY"
