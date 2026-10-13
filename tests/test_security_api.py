"""API input validation and audit integrity regressions."""
import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from agents.api import RCRIRequest, api_rcri, api_audit_logs
from agents.base import AuditTrail
from rcri_lee import FACTORS


def test_api_uses_same_domain_score():
    req = RCRIRequest(**{factor: factor in FACTORS[:2] for factor in FACTORS})
    result = api_rcri(req)
    assert result["score"] == 2
    assert result["classification"] == "Class III"
    assert result["validation_event_rate_percent"] == 7.0


def test_api_rejects_missing_invalid_and_extra_factors():
    values = {factor: False for factor in FACTORS}
    with pytest.raises(ValidationError):
        RCRIRequest(**{k: v for k, v in values.items() if k != FACTORS[0]})
    with pytest.raises(ValidationError):
        RCRIRequest(**{**values, "heart_failure": "false"})
    with pytest.raises(ValidationError):
        RCRIRequest(**{**values, "patient_id": "A123"})


def test_audit_hmac_tamper_detection():
    trail = AuditTrail(secret_key="test-only-key")
    trail.log("tester", "internal", "create", {"event": "a"})
    trail.log("tester", "internal", "review", {"event": "b"})
    assert trail.verify_integrity()
    trail.logs[0]["event_type"] = "FORGED"
    assert not trail.verify_integrity()


def test_audit_access_requires_server_key(monkeypatch):
    monkeypatch.delenv("AUDIT_ADMIN_KEY", raising=False)
    with pytest.raises(HTTPException) as error:
        api_audit_logs(None)
    assert error.value.status_code == 503
    monkeypatch.setenv("AUDIT_ADMIN_KEY", "test-only-secret")
    with pytest.raises(HTTPException) as error:
        api_audit_logs("incorrect")
    assert error.value.status_code == 403
    assert api_audit_logs("test-only-secret")["verified"] is True
