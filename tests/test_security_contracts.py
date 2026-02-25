"""Tests for security & compliance contracts — PR-081 to PR-090."""

from __future__ import annotations

from packages.core.contracts.security import (
    AccessReviewEntry,
    AccessReviewReport,
    AuditLogEntry,
    ComplianceControl,
    ComplianceReport,
    ConsentRecord,
    GDPRDataExport,
    GDPRRequest,
    InMemoryAuditLog,
    InMemoryConsentStore,
    KeyRotationEvent,
    KeyRotationPolicy,
    MaskingRule,
    SecretReference,
    SecurityFinding,
    SecurityScanResult,
    StubSecretsManager,
    ThreatEntry,
    ThreatModel,
    apply_mask,
)


class TestSecretReference:
    def test_schema(self) -> None:
        s = SecretReference(key="api_key")
        assert s.key == "api_key"
        assert s.version == 1
        assert s.expires_at is None


class TestStubSecretsManager:
    def test_set_and_get(self) -> None:
        sm = StubSecretsManager()
        ref = sm.set("key1", "secret_value")
        assert ref.key == "key1"
        assert sm.get("key1") == "secret_value"

    def test_get_missing(self) -> None:
        sm = StubSecretsManager()
        assert sm.get("nope") is None

    def test_delete(self) -> None:
        sm = StubSecretsManager()
        sm.set("key1", "val")
        assert sm.delete("key1") is True
        assert sm.delete("key1") is False

    def test_keys(self) -> None:
        sm = StubSecretsManager()
        sm.set("a", "1")
        sm.set("b", "2")
        assert sorted(sm.keys()) == ["a", "b"]

    def test_clear(self) -> None:
        sm = StubSecretsManager()
        sm.set("a", "1")
        sm.clear()
        assert sm.keys() == []


class TestKeyRotation:
    def test_policy(self) -> None:
        p = KeyRotationPolicy(key_name="api_key")
        assert p.rotation_interval_days == 90
        assert p.auto_rotate is True

    def test_event(self) -> None:
        e = KeyRotationEvent(
            key_name="api_key", old_version=1, new_version=2, status="completed"
        )
        assert e.status == "completed"


class TestAuditLog:
    def test_entry_schema(self) -> None:
        e = AuditLogEntry(action="create", actor="admin", resource="agent")
        assert e.action == "create"

    def test_in_memory_log(self) -> None:
        log = InMemoryAuditLog()
        log.record(AuditLogEntry(action="create", actor="admin", resource="agent"))
        log.record(AuditLogEntry(action="read", actor="user1", resource="agent"))
        assert len(log.entries()) == 2
        assert len(log.entries_for_actor("admin")) == 1
        assert len(log.entries_for_resource("agent")) == 2

    def test_clear(self) -> None:
        log = InMemoryAuditLog()
        log.record(AuditLogEntry(action="create", actor="a", resource="r"))
        log.clear()
        assert log.entries() == []


class TestDataMasking:
    def test_redact(self) -> None:
        rule = MaskingRule(field_pattern="password", strategy="redact")
        assert apply_mask("secret123", rule) == "***"

    def test_partial(self) -> None:
        rule = MaskingRule(field_pattern="email", strategy="partial")
        result = apply_mask("user@example.com", rule)
        assert result.startswith("us")
        assert result.endswith("om")

    def test_partial_short(self) -> None:
        rule = MaskingRule(field_pattern="pin", strategy="partial")
        assert apply_mask("12", rule) == "***"

    def test_hash(self) -> None:
        rule = MaskingRule(field_pattern="ssn", strategy="hash")
        result = apply_mask("123-45-6789", rule)
        assert len(result) == 16

    def test_tokenize(self) -> None:
        rule = MaskingRule(field_pattern="credit_card", strategy="tokenize")
        assert apply_mask("4111111111111111", rule) == "<credit_card>"


class TestGDPR:
    def test_request(self) -> None:
        r = GDPRRequest(request_id="req-1", request_type="access", subject_id="user-1")
        assert r.status == "pending"

    def test_export(self) -> None:
        e = GDPRDataExport(subject_id="user-1", data={"name": "Test"})
        assert e.format == "json"


class TestConsentTracking:
    def test_record(self) -> None:
        r = ConsentRecord(subject_id="u1", purpose="analytics", status="granted")
        assert r.status == "granted"

    def test_store_has_consent(self) -> None:
        store = InMemoryConsentStore()
        store.record(
            ConsentRecord(subject_id="u1", purpose="analytics", status="granted")
        )
        assert store.has_consent("u1", "analytics") is True
        assert store.has_consent("u1", "marketing") is False

    def test_withdrawn_consent(self) -> None:
        store = InMemoryConsentStore()
        store.record(
            ConsentRecord(subject_id="u1", purpose="analytics", status="granted")
        )
        store.record(
            ConsentRecord(subject_id="u1", purpose="analytics", status="withdrawn")
        )
        assert store.has_consent("u1", "analytics") is False


class TestAccessReview:
    def test_entry(self) -> None:
        e = AccessReviewEntry(principal="admin", resource="secrets", permission="read")
        assert e.status == "pending"

    def test_report(self) -> None:
        r = AccessReviewReport(review_id="rev-1", total_reviewed=5, total_revoked=1)
        assert r.total_revoked == 1


class TestSecurityScan:
    def test_finding(self) -> None:
        f = SecurityFinding(finding_id="f1", title="SQL Injection", severity="critical")
        assert f.severity == "critical"

    def test_result(self) -> None:
        r = SecurityScanResult(
            scan_id="s1",
            findings=(SecurityFinding(finding_id="f1", title="XSS", severity="high"),),
        )
        assert len(r.findings) == 1


class TestThreatModeling:
    def test_entry(self) -> None:
        t = ThreatEntry(
            threat_id="t1",
            title="Data exfil",
            severity="high",
            category="Information Disclosure",
        )
        assert t.category == "Information Disclosure"

    def test_model(self) -> None:
        m = ThreatModel(
            model_id="tm-1",
            name="API Threat Model",
            threats=(
                ThreatEntry(threat_id="t1", title="Injection", severity="critical"),
            ),
        )
        assert len(m.threats) == 1


class TestComplianceReport:
    def test_control(self) -> None:
        c = ComplianceControl(
            control_id="CC1.1",
            name="Access Control",
            framework="SOC2",
            status="compliant",
        )
        assert c.status == "compliant"

    def test_report(self) -> None:
        r = ComplianceReport(
            report_id="cr-1",
            framework="SOC2",
            controls=(
                ComplianceControl(control_id="CC1.1", name="AC", status="compliant"),
            ),
            overall_status="compliant",
        )
        assert r.overall_status == "compliant"
        assert len(r.controls) == 1
