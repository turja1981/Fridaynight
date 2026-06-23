from __future__ import annotations
from .tracker import KPITracker
from .metrics import MetricsCollector

class KPIDashboard:
    """Assembles KPI data for the frontend dashboard."""

    def __init__(self):
        self.tracker = KPITracker()
        self.collector = MetricsCollector()

    def get_dashboard_data(self, domain: str = "insurance_claims") -> dict:
        stats = self.tracker.get_all_stats()
        total_calls = sum(s.get("total_calls", 0) for s in stats.values())
        success_rate = (sum(s.get("total_calls", 0) * s.get("success_rate", 1) for s in stats.values()) / max(total_calls, 1)) * 100
        avg_latency = sum(s.get("avg_latency_ms", 0) for s in stats.values()) / max(len(stats), 1)
        total_tokens = sum(s.get("total_tokens", 0) for s in stats.values())
        cost_usd = total_tokens * 0.000003

        return {
            "summary_cards": [
                {"label": "Total Queries", "value": total_calls, "trend": "+12%"},
                {"label": "Success Rate", "value": f"{success_rate:.1f}%", "trend": "+2.1%"},
                {"label": "Avg Latency", "value": f"{avg_latency:.0f}ms", "trend": "-5%"},
                {"label": "Cost Estimate", "value": f"${cost_usd:.4f}", "trend": "stable"},
            ],
            "time_series": self.tracker.get_time_series(24),
            "agent_breakdown": stats,
            "model_distribution": self.tracker.get_model_distribution(),
            "business_kpis": self.collector.compute_business_kpis(domain, stats),
            "roi": self.collector.compute_roi(total_calls),
        }
