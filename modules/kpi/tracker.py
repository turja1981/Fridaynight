from __future__ import annotations
from collections import defaultdict
from typing import Optional


class KPITracker:
    """Singleton KPI tracker storing agent call statistics in memory."""

    _instance: Optional[KPITracker] = None

    def __new__(cls) -> KPITracker:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._data: dict = defaultdict(lambda: {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "total_latency_ms": 0.0,
                "total_tokens": 0,
                "models_used": defaultdict(int),
            })
        return cls._instance

    def track_call(
        self,
        agent_name: str,
        latency_ms: float,
        tokens_used: int,
        success: bool,
        model: str = "claude-sonnet-4-6",
    ) -> None:
        """Record a single agent call."""
        stats = self._data[agent_name]
        stats["total_calls"] += 1
        stats["total_latency_ms"] += latency_ms
        stats["total_tokens"] += tokens_used
        stats["models_used"][model] += 1
        if success:
            stats["successful_calls"] += 1
        else:
            stats["failed_calls"] += 1

    def get_agent_stats(self, agent_name: str) -> dict:
        """Return stats for a single agent."""
        raw = self._data[agent_name]
        total = raw["total_calls"]
        avg_latency = raw["total_latency_ms"] / total if total > 0 else 0.0
        success_rate = raw["successful_calls"] / total if total > 0 else 0.0
        return {
            "agent_name": agent_name,
            "total_calls": total,
            "successful_calls": raw["successful_calls"],
            "failed_calls": raw["failed_calls"],
            "success_rate": round(success_rate, 4),
            "avg_latency_ms": round(avg_latency, 2),
            "total_tokens": raw["total_tokens"],
            "models_used": dict(raw["models_used"]),
        }

    def get_all_stats(self) -> dict:
        """Return stats for all agents."""
        return {
            agent_name: self.get_agent_stats(agent_name)
            for agent_name in self._data
        }

    def reset(self) -> None:
        """Clear all tracked data."""
        self._data.clear()
