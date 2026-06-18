from __future__ import annotations

from .pii_detector import PIIDetector
from .safety_filter import SafetyFilter


class GuardrailsPipeline:
    """End-to-end guardrails pipeline for input/output safety."""

    def __init__(self) -> None:
        self._pii = PIIDetector()
        self._safety = SafetyFilter()

    def process_input(self, text: str) -> dict:
        """Process user input through safety and PII checks."""
        # Safety check first
        safety_result = self._safety.check_input(text)
        if not safety_result["is_safe"]:
            return {
                "safe_text": "",
                "pii_removed": False,
                "is_safe": False,
                "blocked_reason": safety_result["reason"],
            }

        # PII detection and redaction
        pii_result = self._pii.scan(text)
        safe_text = pii_result["redacted_text"]
        pii_removed = pii_result["has_pii"]

        return {
            "safe_text": safe_text,
            "pii_removed": pii_removed,
            "is_safe": True,
            "blocked_reason": None,
        }

    def process_output(self, text: str) -> dict:
        """Process LLM output through safety and PII checks."""
        safety_result = self._safety.check_output(text)
        if not safety_result["is_safe"]:
            return {
                "safe_text": "I'm unable to provide that response.",
                "is_safe": False,
            }

        # Redact any PII that leaked into output
        pii_result = self._pii.scan(text)
        return {
            "safe_text": pii_result["redacted_text"],
            "is_safe": True,
        }
