from __future__ import annotations
from fastapi import APIRouter, Query
from backend.config import settings
from modules.audit import AuditLogger

router = APIRouter(tags=["audit"])
_audit = AuditLogger(db_path="./data/audit.db")


@router.get("/audit/logs")
async def get_audit_logs(
    user_id: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
):
    logs = _audit.query(user_id=user_id, event_type=event_type, limit=limit, offset=offset)
    return {"logs": logs, "count": len(logs)}


@router.get("/audit/summary")
async def get_audit_summary():
    return _audit.get_summary()


@router.get("/audit/logs/{user_id}")
async def get_user_audit_logs(user_id: str, limit: int = Query(default=20)):
    logs = _audit.query(user_id=user_id, limit=limit)
    return {"user_id": user_id, "logs": logs, "count": len(logs)}
