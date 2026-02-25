"""Security & compliance contracts — PR-081 to PR-090.

Defines secrets management, key rotation, audit logging, data masking,
GDPR tooling, consent tracking, access review, security scanning,
threat modeling, and compliance reporting contracts.

Most security infrastructure lives outside core; this module provides
**contracts and stubs** for platform integration.

PR-081: Secrets manager
PR-082: Key rotation
PR-083: Audit log
PR-084: Data masking
PR-085: GDPR tools
PR-086: Consent tracking
PR-087: Access review
PR-088: Security scan
PR-089: Threat modeling
PR-090: Compliance report
"""

from __future__ import annotations

import time
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# PR-081 — Secrets manager
# ---------------------------------------------------------------------------


class SecretReference(BaseModel):
    """Opaque reference to a stored secret (never holds the value)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    key: str
    version: int = 1
    created_at: float = Field(default_factory=time.time)
    expires_at: float | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class StubSecretsManager:
    """In-memory secrets manager stub — NOT for production."""

    def __init__(self) -> None:
        self._secrets: dict[str, str] = {}

    def set(self, key: str, value: str) -> SecretReference:
        self._secrets[key] = value
        return SecretReference(key=key)

    def get(self, key: str) -> str | None:
        return self._secrets.get(key)

    def delete(self, key: str) -> bool:
        return self._secrets.pop(key, None) is not None

    def keys(self) -> list[str]:
        return list(self._secrets.keys())

    def clear(self) -> None:
        self._secrets.clear()


# ---------------------------------------------------------------------------
# PR-082 — Key rotation
# ---------------------------------------------------------------------------

RotationStatus = Literal["pending", "in_progress", "completed", "failed"]


class KeyRotationPolicy(BaseModel):
    """Policy for automatic key rotation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    key_name: str
    rotation_interval_days: int = 90
    auto_rotate: bool = True
    notify_before_days: int = 7


class KeyRotationEvent(BaseModel):
    """Event logged when a key rotation occurs."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    key_name: str
    old_version: int
    new_version: int
    status: RotationStatus
    timestamp: float = Field(default_factory=time.time)
    error: str = ""


# ---------------------------------------------------------------------------
# PR-083 — Audit log
# ---------------------------------------------------------------------------

AuditAction = Literal[
    "create",
    "read",
    "update",
    "delete",
    "login",
    "logout",
    "permission_change",
    "config_change",
    "secret_access",
]


class AuditLogEntry(BaseModel):
    """Single audit log entry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    action: AuditAction
    actor: str
    resource: str
    resource_id: str = ""
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)
    ip_address: str = ""
    trace_id: str = ""


class InMemoryAuditLog:
    """In-memory audit log store."""

    def __init__(self) -> None:
        self._entries: list[AuditLogEntry] = []

    def record(self, entry: AuditLogEntry) -> None:
        self._entries.append(entry)

    def entries(self) -> list[AuditLogEntry]:
        return list(self._entries)

    def entries_for_actor(self, actor: str) -> list[AuditLogEntry]:
        return [e for e in self._entries if e.actor == actor]

    def entries_for_resource(self, resource: str) -> list[AuditLogEntry]:
        return [e for e in self._entries if e.resource == resource]

    def clear(self) -> None:
        self._entries.clear()


# ---------------------------------------------------------------------------
# PR-084 — Data masking
# ---------------------------------------------------------------------------

MaskStrategy = Literal["redact", "hash", "partial", "tokenize"]


class MaskingRule(BaseModel):
    """Rule for masking sensitive data in logs/exports."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    field_pattern: str  # regex or glob
    strategy: MaskStrategy = "redact"
    replacement: str = "***"


def apply_mask(value: str, rule: MaskingRule) -> str:
    """Apply masking strategy to a value."""
    if rule.strategy == "redact":
        return rule.replacement
    if rule.strategy == "partial":
        if len(value) <= 4:
            return rule.replacement
        return value[:2] + rule.replacement + value[-2:]
    if rule.strategy == "hash":
        import hashlib

        return hashlib.sha256(value.encode()).hexdigest()[:16]
    # tokenize: return placeholder
    return f"<{rule.field_pattern}>"


# ---------------------------------------------------------------------------
# PR-085 — GDPR tools
# ---------------------------------------------------------------------------

GDPRRequestType = Literal[
    "access", "rectification", "erasure", "portability", "restriction"
]
GDPRRequestStatus = Literal["pending", "processing", "completed", "rejected"]


class GDPRRequest(BaseModel):
    """Data subject request under GDPR."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    request_id: str
    request_type: GDPRRequestType
    subject_id: str
    status: GDPRRequestStatus = "pending"
    submitted_at: float = Field(default_factory=time.time)
    completed_at: float | None = None
    notes: str = ""


class GDPRDataExport(BaseModel):
    """Exported data for a subject access request."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    subject_id: str
    data: dict[str, Any] = Field(default_factory=dict)
    exported_at: float = Field(default_factory=time.time)
    format: str = "json"


# ---------------------------------------------------------------------------
# PR-086 — Consent tracking
# ---------------------------------------------------------------------------

ConsentStatus = Literal["granted", "denied", "withdrawn"]


class ConsentRecord(BaseModel):
    """Record of user consent for a specific purpose."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    subject_id: str
    purpose: str
    status: ConsentStatus
    granted_at: float = Field(default_factory=time.time)
    expires_at: float | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class InMemoryConsentStore:
    """In-memory consent tracking store."""

    def __init__(self) -> None:
        self._records: list[ConsentRecord] = []

    def record(self, consent: ConsentRecord) -> None:
        self._records.append(consent)

    def get_for_subject(self, subject_id: str) -> list[ConsentRecord]:
        return [r for r in self._records if r.subject_id == subject_id]

    def has_consent(self, subject_id: str, purpose: str) -> bool:
        relevant = [
            r
            for r in self._records
            if r.subject_id == subject_id and r.purpose == purpose
        ]
        if not relevant:
            return False
        return relevant[-1].status == "granted"

    def clear(self) -> None:
        self._records.clear()


# ---------------------------------------------------------------------------
# PR-087 — Access review
# ---------------------------------------------------------------------------

ReviewStatus = Literal["pending", "approved", "revoked"]


class AccessReviewEntry(BaseModel):
    """Access review item."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    principal: str
    resource: str
    permission: str
    status: ReviewStatus = "pending"
    reviewer: str = ""
    reviewed_at: float | None = None
    notes: str = ""


class AccessReviewReport(BaseModel):
    """Summary of an access review campaign."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    review_id: str
    entries: tuple[AccessReviewEntry, ...] = ()
    total_reviewed: int = 0
    total_revoked: int = 0
    generated_at: float = Field(default_factory=time.time)


# ---------------------------------------------------------------------------
# PR-088 — Security scan
# ---------------------------------------------------------------------------

ScanSeverity = Literal["info", "low", "medium", "high", "critical"]
ScanStatus = Literal["pending", "running", "completed", "failed"]


class SecurityFinding(BaseModel):
    """Single security scan finding."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    finding_id: str
    title: str
    severity: ScanSeverity
    description: str = ""
    location: str = ""
    remediation: str = ""


class SecurityScanResult(BaseModel):
    """Result of a security scan."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    scan_id: str
    status: ScanStatus = "completed"
    findings: tuple[SecurityFinding, ...] = ()
    scanned_at: float = Field(default_factory=time.time)
    duration_seconds: float = 0.0


# ---------------------------------------------------------------------------
# PR-089 — Threat modeling
# ---------------------------------------------------------------------------

ThreatSeverity = Literal["low", "medium", "high", "critical"]


class ThreatEntry(BaseModel):
    """Identified threat in a threat model."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    threat_id: str
    title: str
    severity: ThreatSeverity
    category: str = ""  # e.g. STRIDE category
    description: str = ""
    mitigation: str = ""
    status: str = "identified"


class ThreatModel(BaseModel):
    """Threat model document."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_id: str
    name: str
    scope: str = ""
    threats: tuple[ThreatEntry, ...] = ()
    created_at: float = Field(default_factory=time.time)


# ---------------------------------------------------------------------------
# PR-090 — Compliance report
# ---------------------------------------------------------------------------

ComplianceStatus = Literal["compliant", "non_compliant", "partial", "not_assessed"]


class ComplianceControl(BaseModel):
    """Single compliance control assessment."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    control_id: str
    name: str
    framework: str = ""  # e.g. SOC2, ISO27001
    status: ComplianceStatus = "not_assessed"
    evidence: str = ""
    notes: str = ""


class ComplianceReport(BaseModel):
    """Compliance report aggregating control assessments."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    report_id: str
    framework: str
    controls: tuple[ComplianceControl, ...] = ()
    overall_status: ComplianceStatus = "not_assessed"
    assessed_at: float = Field(default_factory=time.time)
    assessor: str = ""
