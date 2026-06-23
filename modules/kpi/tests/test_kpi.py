from __future__ import annotations
import pytest
from modules.kpi.tracker import KPITracker
from modules.kpi.metrics import MetricsCollector
from modules.kpi.dashboard import KPIDashboard


@pytest.fixture(autouse=True)
def reset_tracker():
    """Reset singleton KPITracker before each test."""
    KPITracker().reset()
    yield
    KPITracker().reset()


class TestKPITracker:
    def test_track_call_increments_count(self):
        tracker = KPITracker()
        tracker.track_call("research_agent", 250.0, 500, True)
        stats = tracker.get_agent_stats("research_agent")
        assert stats["total_calls"] == 1
        assert stats["total_tokens"] == 500

    def test_success_rate_calculation(self):
        tracker = KPITracker()
        tracker.track_call("analysis_agent", 100.0, 200, True)
        tracker.track_call("analysis_agent", 150.0, 300, False)
        stats = tracker.get_agent_stats("analysis_agent")
        assert stats["success_rate"] == 0.5

    def test_get_all_stats_includes_all_agents(self):
        tracker = KPITracker()
        tracker.track_call("research_agent", 100.0, 100, True)
        tracker.track_call("data_agent", 200.0, 200, True)
        all_stats = tracker.get_all_stats()
        assert "research_agent" in all_stats
        assert "data_agent" in all_stats

    def test_get_time_series_length(self):
        tracker = KPITracker()
        series = tracker.get_time_series(24)
        assert len(series) == 24
        for entry in series:
            assert "hour" in entry
            assert "calls" in entry

    def test_get_model_distribution(self):
        tracker = KPITracker()
        tracker.track_call("agent", 100.0, 100, True, model="claude-haiku-4-5-20251001")
        tracker.track_call("agent", 200.0, 200, True, model="claude-sonnet-4-6")
        dist = tracker.get_model_distribution()
        assert dist.get("claude-haiku-4-5-20251001", 0) == 1
        assert dist.get("claude-sonnet-4-6", 0) == 1

    def test_empty_agent_stats_returns_empty_dict(self):
        tracker = KPITracker()
        assert tracker.get_agent_stats("nonexistent") == {}


class TestMetricsCollector:
    def test_compute_business_kpis_insurance(self):
        collector = MetricsCollector()
        raw = {"agent": {"total_calls": 10, "success_rate": 0.9, "avg_latency_ms": 200}}
        result = collector.compute_business_kpis("insurance_claims", raw)
        assert "auto_approval_rate" in result
        assert "fraud_detection_rate" in result
        assert "total_interactions" in result

    def test_compute_business_kpis_banking(self):
        collector = MetricsCollector()
        result = collector.compute_business_kpis("banking", {})
        assert "query_resolution_rate" in result

    def test_compute_roi_positive(self):
        collector = MetricsCollector()
        roi = collector.compute_roi(100)
        assert roi["roi_multiplier"] > 0
        assert roi["cost_saved_usd"] > 0
        assert roi["calls_handled"] == 100
        assert roi["time_saved_mins"] == 500  # 100 * 5.0


class TestKPIDashboard:
    def test_dashboard_summary_cards_count(self):
        dashboard = KPIDashboard()
        data = dashboard.get_dashboard_data("insurance_claims")
        assert "summary_cards" in data
        assert len(data["summary_cards"]) == 4

    def test_dashboard_time_series_length(self):
        dashboard = KPIDashboard()
        data = dashboard.get_dashboard_data()
        assert len(data["time_series"]) == 24

    def test_dashboard_has_all_required_keys(self):
        dashboard = KPIDashboard()
        data = dashboard.get_dashboard_data("banking")
        for key in ("summary_cards", "time_series", "agent_breakdown", "model_distribution", "business_kpis", "roi"):
            assert key in data, f"Missing key: {key}"
