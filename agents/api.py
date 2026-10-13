"""
FastAPI REST API Server for Rcri Lee Cardiac Risk.
"""
from typing import Dict, Any, List
import os
import hmac
from fastapi import FastAPI, HTTPException, Header, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, ConfigDict, StrictBool
from .base import AuditLogger, PHIGuard, SecurityException
from rcri_lee import calculate_metrics
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Rcri Lee Cardiac Risk API",
    description="RCRI scoring and legacy generic audit endpoints",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


class RCRIRequest(BaseModel):
    """All six risk criteria must be explicitly supplied."""
    model_config = ConfigDict(extra="forbid")
    high_risk_surgery: StrictBool
    ischemic_heart_disease: StrictBool
    heart_failure: StrictBool
    cerebrovascular_disease: StrictBool
    insulin_treatment: StrictBool
    creatinine_ge_2: StrictBool


@app.post("/api/rcri")
def api_rcri(payload: RCRIRequest):
    """Calculate the Lee Index using the same algorithm as the offline CLI."""
    return calculate_metrics(**payload.model_dump())


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "rcri-lee-cardiac-risk", "domain": "Clinical & Biomedical AI", "standard": "CAP / CLSI / ISO Standards", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    from .metrics import GLOBAL_METRICS
    return GLOBAL_METRICS.export_prometheus_text()


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audit/logs")
def api_audit_logs(x_audit_access_key: str | None = Header(default=None)):
    """Administrative audit data is unavailable without a configured secret."""
    configured = os.getenv("AUDIT_ADMIN_KEY")
    if not configured:
        raise HTTPException(status_code=503, detail="Audit log access is not configured")
    if not x_audit_access_key or not hmac.compare_digest(x_audit_access_key, configured):
        raise HTTPException(status_code=403, detail="Audit log access denied")
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
