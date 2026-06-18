from __future__ import annotations
from collections import defaultdict

_HIGH_COMPLEXITY_KEYWORDS = {
    "analyze", "analyse", "compare", "synthesize", "synthesise",
    "comprehensive", "evaluate", "assess", "research", "investigate",
    "multi-step", "complex", "detailed", "in-depth",
}

_MODEL_COSTS: dict[str, float] = {
    "claude-haiku-4-5-20251001": 0.00025,   # per 1K tokens (approx)
    "claude-sonnet-4-6": 0.003,
    "claude-opus-4-8": 0.015,
}


class ModelRouter:
    """Routes tasks to the appropriate Claude model based on complexity."""

    def __init__(self) -> None:
        self._usage: dict[str, dict] = defaultdict(lambda: {"calls": 0, "tokens": 0, "cost_usd": 0.0})

    def _estimate_complexity(self, task: str) -> str:
        """Estimate task complexity as LOW, MEDIUM, or HIGH."""
        word_count = len(task.split())
        task_lower = task.lower()

        # High complexity: long text or complex keywords
        if word_count > 200 or any(kw in task_lower for kw in _HIGH_COMPLEXITY_KEYWORDS):
            return "HIGH"

        # Low complexity: short, simple tasks
        if word_count < 30:
            return "LOW"

        return "MEDIUM"

    def route(self, task: str, complexity: str = "auto") -> str:
        """Return model name for task based on complexity."""
        if complexity == "auto":
            complexity = self._estimate_complexity(task)

        if complexity == "LOW":
            return "claude-haiku-4-5-20251001"
        if complexity == "HIGH":
            return "claude-opus-4-8"
        return "claude-sonnet-4-6"

    def track_usage(self, model: str, tokens: int, cost_usd: float) -> None:
        """Track model usage statistics."""
        self._usage[model]["calls"] += 1
        self._usage[model]["tokens"] += tokens
        self._usage[model]["cost_usd"] += cost_usd

    def get_cost_report(self) -> dict:
        """Return cost report grouped by model."""
        total_cost = sum(v["cost_usd"] for v in self._usage.values())
        total_tokens = sum(v["tokens"] for v in self._usage.values())
        return {
            "total_cost_usd": round(total_cost, 4),
            "total_tokens": total_tokens,
            "by_model": {
                model: {
                    "calls": data["calls"],
                    "tokens": data["tokens"],
                    "cost_usd": round(data["cost_usd"], 4),
                    "cost_per_call": round(data["cost_usd"] / data["calls"], 6) if data["calls"] > 0 else 0,
                }
                for model, data in self._usage.items()
            },
        }
