from __future__ import annotations
from collections import defaultdict
import time

COMPLEXITY_MAP = {
    "low": "claude-haiku-4-5-20251001",
    "medium": "claude-sonnet-4-6",
    "high": "claude-opus-4-8",
}

HIGH_COMPLEXITY_KEYWORDS = {"synthesize", "compare", "analyze", "evaluate", "critique", "comprehensive", "detailed", "research"}
LOW_COMPLEXITY_KEYWORDS = {"hello", "hi", "thanks", "ok", "yes", "no", "status", "list", "what is"}

class ModelRouter:
    """Routes LLM requests to the most cost-effective model based on task complexity."""

    MODEL_COSTS = {
        "claude-haiku-4-5-20251001": 0.00025 / 1000,
        "claude-sonnet-4-6": 0.003 / 1000,
        "claude-opus-4-8": 0.015 / 1000,
    }

    def __init__(self):
        self._usage: dict[str, dict] = defaultdict(lambda: {"calls": 0, "tokens": 0, "cost_usd": 0.0})

    def route(self, task: str, complexity: str = "auto") -> str:
        if complexity != "auto":
            return COMPLEXITY_MAP.get(complexity, COMPLEXITY_MAP["medium"])
        task_lower = task.lower()
        if any(w in task_lower for w in LOW_COMPLEXITY_KEYWORDS):
            return COMPLEXITY_MAP["low"]
        if any(w in task_lower for w in HIGH_COMPLEXITY_KEYWORDS):
            return COMPLEXITY_MAP["high"]
        token_estimate = len(task.split())
        if token_estimate > 200:
            return COMPLEXITY_MAP["high"]
        if token_estimate < 20:
            return COMPLEXITY_MAP["low"]
        return COMPLEXITY_MAP["medium"]

    def track_usage(self, model: str, tokens: int) -> None:
        cost = tokens * self.MODEL_COSTS.get(model, 0.003 / 1000)
        self._usage[model]["calls"] += 1
        self._usage[model]["tokens"] += tokens
        self._usage[model]["cost_usd"] += cost

    def get_cost_report(self) -> dict:
        return dict(self._usage)
