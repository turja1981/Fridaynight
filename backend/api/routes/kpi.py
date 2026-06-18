from __future__ import annotations
from fastapi import APIRouter
from backend.config import settings
from modules.kpi import KPIDashboard, KPITracker

router = APIRouter(tags=["kpi"])
_dashboard = KPIDashboard()
_tracker = KPITracker()

@router.get("/kpi/dashboard")
async def get_dashboard():
    return _dashboard.get_dashboard_data(settings.active_adapter)

@router.get("/kpi/metrics")
async def get_metrics():
    return _tracker.get_all_stats()
