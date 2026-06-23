from __future__ import annotations
from collections import defaultdict

# Per-provider model tiers (low / medium / high complexity)
PROVIDER_MODELS: dict[str, dict[str, str]] = {
    "anthropic": {
        "low":    "claude-haiku-4-5-20251001",
        "medium": "claude-sonnet-4-6",
        "high":   "claude-opus-4-8",
    },
    "openai": {
        "low":    "gpt-4o-mini",
        "medium": "gpt-4o",
        "high":   "gpt-4o",
    },
    "google": {
        "low":    "gemini-1.5-flash",
        "medium": "gemini-1.5-pro",
        "high":   "gemini-1.5-pro",
    },
}

# Backward-compat alias
COMPLEXITY_MAP = PROVIDER_MODELS["anthropic"]

HIGH_COMPLEXITY_KEYWORDS = {
    "synthesize", "compare", "analyze", "evaluate", "critique",
    "comprehensive", "detailed", "research",
}
LOW_COMPLEXITY_KEYWORDS = {"hello", "hi", "thanks", "ok", "yes", "no", "status", "list", "what is"}

# Cost per token (input, approximate)
MODEL_COSTS: dict[str, float] = {
    "claude-haiku-4-5-20251001": 0.00025 / 1000,
    "claude-sonnet-4-6":         0.003   / 1000,
    "claude-opus-4-8":           0.015   / 1000,
    "gpt-4o-mini":               0.00015 / 1000,
    "gpt-4o":                    0.005   / 1000,
    "gemini-1.5-flash":          0.000075 / 1000,
    "gemini-1.5-pro":            0.00125  / 1000,
}


def _keyword_match(task_lower: str, keywords: set[str]) -> bool:
    """Return True if any keyword matches at a word boundary (prevents 'hi' matching 'this')."""
    task_words = set(task_lower.split())
    for kw in keywords:
        if " " in kw:  # multi-word phrase: substring is fine (specific enough)
            if kw in task_lower:
                return True
        else:
            if kw in task_words:
                return True
    return False


def _infer_complexity(task: str) -> str:
    task_lower = task.lower()
    if _keyword_match(task_lower, LOW_COMPLEXITY_KEYWORDS):
        return "low"
    if _keyword_match(task_lower, HIGH_COMPLEXITY_KEYWORDS):
        return "high"
    tokens = len(task.split())
    if tokens > 200:
        return "high"
    if tokens < 20:
        return "low"
    return "medium"


class ModelRouter:
    """Routes LLM requests to the most cost-effective model based on task complexity.

    Supports Anthropic (Claude), OpenAI (GPT-4o), and Google (Gemini).
    """

    def __init__(self):
        self._usage: dict[str, dict] = defaultdict(lambda: {"calls": 0, "tokens": 0, "cost_usd": 0.0})

    # ── single-provider (backward-compatible) ──────────────────────────────

    def route(self, task: str, complexity: str = "auto") -> str:
        """Return a Claude model ID. Kept for backward compatibility."""
        level = complexity if complexity != "auto" else _infer_complexity(task)
        return PROVIDER_MODELS["anthropic"].get(level, PROVIDER_MODELS["anthropic"]["medium"])

    # ── multi-provider ─────────────────────────────────────────────────────

    def route_with_provider(
        self,
        task: str,
        provider: str = "anthropic",
        complexity: str = "auto",
    ) -> tuple[str, str]:
        """Return (provider, model_id) for the given task and preferred provider.

        Unknown providers fall back to Anthropic models.
        """
        level = complexity if complexity != "auto" else _infer_complexity(task)
        models = PROVIDER_MODELS.get(provider, PROVIDER_MODELS["anthropic"])
        return provider, models.get(level, models["medium"])

    # ── usage tracking ─────────────────────────────────────────────────────

    def track_usage(self, model: str, tokens: int) -> None:
        cost = tokens * MODEL_COSTS.get(model, 0.003 / 1000)
        self._usage[model]["calls"] += 1
        self._usage[model]["tokens"] += tokens
        self._usage[model]["cost_usd"] += cost

    def get_cost_report(self) -> dict:
        return dict(self._usage)
