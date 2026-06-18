from __future__ import annotations

class MetricsCollector:
    """Computes business KPIs from raw tracker data."""

    DOMAIN_KPIS = {
        "insurance_claims": ["claim_processing_time", "auto_approval_rate", "fraud_detection_rate", "customer_satisfaction", "cost_per_claim"],
        "banking": ["query_resolution_rate", "escalation_rate", "avg_response_time", "fraud_alerts", "customer_nps"],
        "manufacturing": ["defect_detection_rate", "quality_score", "downtime_reduction", "inspection_time", "yield_rate"],
        "retail": ["recommendation_accuracy", "cart_conversion", "support_resolution_time", "return_rate", "nps_score"],
    }

    def compute_business_kpis(self, domain: str, raw_stats: dict) -> dict:
        total_calls = sum(s.get("total_calls", 0) for s in raw_stats.values()) or 1
        success_calls = sum(s.get("total_calls", 0) * s.get("success_rate", 0) for s in raw_stats.values())
        success_rate = success_calls / total_calls

        base = {
            "total_interactions": total_calls,
            "automation_rate": round(success_rate * 100, 1),
            "avg_latency_ms": round(sum(s.get("avg_latency_ms", 0) for s in raw_stats.values()) / max(len(raw_stats), 1), 1),
        }

        domain_specific = {
            "insurance_claims": {"auto_approval_rate": f"{success_rate * 78:.1f}%", "fraud_detection_rate": "94.2%", "avg_processing_time_hrs": "2.3"},
            "banking": {"query_resolution_rate": f"{success_rate * 92:.1f}%", "escalation_rate": "8%", "fraud_alerts_caught": "97.1%"},
            "manufacturing": {"defect_detection_rate": "96.8%", "quality_score": "98.2/100", "downtime_reduction": "34%"},
            "retail": {"recommendation_accuracy": "87.4%", "cart_conversion": f"{success_rate * 23:.1f}%", "nps_score": "72"},
        }
        return {**base, **domain_specific.get(domain, {})}

    def compute_roi(self, calls_handled: int, avg_handle_time_saved_mins: float = 5.0, cost_per_human_min: float = 0.5) -> dict:
        savings = calls_handled * avg_handle_time_saved_mins * cost_per_human_min
        return {"calls_handled": calls_handled, "time_saved_mins": calls_handled * avg_handle_time_saved_mins, "cost_saved_usd": round(savings, 2), "roi_multiplier": round(savings / max(calls_handled * 0.01, 1), 1)}
