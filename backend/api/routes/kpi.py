from __future__ import annotations
from fastapi import APIRouter
from backend.config import settings
from modules.kpi import KPIDashboard, KPITracker

router = APIRouter(tags=["kpi"])
_dashboard = KPIDashboard()
_tracker = KPITracker()


@router.get("/kpi/dashboard")
async def get_dashboard(domain: str = settings.active_adapter):
    data = _dashboard.get_dashboard_data(domain)
    return {"domain": domain, **data}


@router.get("/kpi/metrics")
async def get_metrics():
    return {"metrics": _tracker.get_all_stats()}
