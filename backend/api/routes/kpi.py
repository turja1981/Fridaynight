from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/v1/kpi", tags=["kpi"])


@router.get("/dashboard")
async def get_dashboard(
    domain: str = Query(default="insurance_claims"),
) -> dict:
    """Return full KPI dashboard data for the specified domain."""
    from modules.kpi.dashboard import KPIDashboard
    dashboard = KPIDashboard()
    return dashboard.get_dashboard_data(domain=domain)


@router.get("/metrics")
async def get_metrics() -> dict:
    """Return raw KPI metrics for all agents."""
    from modules.kpi.tracker import KPITracker
    tracker = KPITracker()
    return {"metrics": tracker.get_all_stats()}
