from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
import time

@dataclass
class CallRecord:
    agent_name: str
    latency_ms: float
    tokens_used: int
    success: bool
    model: str
    timestamp: float = field(default_factory=time.time)

class KPITracker:
    """In-memory per-agent KPI tracker."""

    _instance: KPITracker | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._records: list[CallRecord] = []
        return cls._instance

    def track_call(self, agent_name: str, latency_ms: float, tokens_used: int, success: bool, model: str = "claude-sonnet-4-6") -> None:
        self._records.append(CallRecord(agent_name, latency_ms, tokens_used, success, model))

    def get_agent_stats(self, agent_name: str) -> dict:
        records = [r for r in self._records if r.agent_name == agent_name]
        if not records:
            return {}
        return {
            "total_calls": len(records),
            "success_rate": sum(1 for r in records if r.success) / len(records),
            "avg_latency_ms": sum(r.latency_ms for r in records) / len(records),
            "total_tokens": sum(r.tokens_used for r in records),
        }

    def get_all_stats(self) -> dict:
        agents = set(r.agent_name for r in self._records)
        return {a: self.get_agent_stats(a) for a in agents}

    def get_time_series(self, hours: int = 24) -> list[dict]:
        cutoff = time.time() - hours * 3600
        hourly: dict[int, int] = defaultdict(int)
        for r in self._records:
            if r.timestamp >= cutoff:
                hour_bucket = int((r.timestamp - cutoff) // 3600)
                hourly[hour_bucket] += 1
        return [{"hour": h, "calls": hourly.get(h, 0)} for h in range(hours)]

    def get_model_distribution(self) -> dict:
        dist: dict[str, int] = defaultdict(int)
        for r in self._records:
            dist[r.model] += 1
        return dict(dist)

    def reset(self) -> None:
        self._records.clear()
