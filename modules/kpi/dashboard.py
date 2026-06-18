from __future__ import annotations
import random
from datetime import datetime, timedelta

from .tracker import KPITracker
from .metrics import MetricsCollector


class KPIDashboard:
    """Generates dashboard data for the frontend."""

    def __init__(self) -> None:
        self._tracker = KPITracker()
        self._metrics = MetricsCollector()

    def get_dashboard_data(self, domain: str = "insurance_claims") -> dict:
        """Return full dashboard data including cards, time series, and KPIs."""
        raw_stats = self._tracker.get_all_stats()
        total_calls = sum(s["total_calls"] for s in raw_stats.values())
        total_tokens = sum(s["total_tokens"] for s in raw_stats.values())
        avg_latency = (
            sum(s["avg_latency_ms"] for s in raw_stats.values()) / len(raw_stats)
            if raw_stats
            else 0
        )
        success_rate = (
            sum(s["success_rate"] for s in raw_stats.values()) / len(raw_stats)
            if raw_stats
            else 0.95
        )

        # Summary cards
        summary_cards = [
            {"label": "Total AI Calls", "value": total_calls, "unit": "calls", "trend": "+12%"},
            {"label": "Avg Latency", "value": round(avg_latency, 1), "unit": "ms", "trend": "-8%"},
            {"label": "Success Rate", "value": round(success_rate * 100, 1), "unit": "%", "trend": "+2%"},
            {"label": "Tokens Used", "value": total_tokens, "unit": "tokens", "trend": "+5%"},
        ]

        # Time series: 24 hourly data points
        now = datetime.utcnow()
        time_series = []
        for i in range(24):
            ts = now - timedelta(hours=23 - i)
            time_series.append(
                {
                    "timestamp": ts.strftime("%H:00"),
                    "calls": random.randint(5, 50) + (total_calls // 24),
                    "latency_ms": round(random.uniform(200, 800), 1),
                    "success_rate": round(random.uniform(0.90, 0.99), 3),
                }
            )

        # Agent breakdown
        agent_breakdown = [
            {
                "agent": name,
                **stats,
            }
            for name, stats in raw_stats.items()
        ]

        # Model distribution
        model_distribution: dict[str, int] = {}
        for stats in raw_stats.values():
            for model, count in stats.get("models_used", {}).items():
                model_distribution[model] = model_distribution.get(model, 0) + count

        # Business KPIs
        business_kpis = self._metrics.compute_business_kpis(domain, raw_stats)
        roi = self._metrics.compute_roi(max(total_calls, 1))

        return {
            "domain": domain,
            "summary_cards": summary_cards,
            "time_series": time_series,
            "agent_breakdown": agent_breakdown,
            "model_distribution": model_distribution,
            "business_kpis": business_kpis,
            "roi": roi,
        }
