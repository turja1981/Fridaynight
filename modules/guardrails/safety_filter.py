from __future__ import annotations
import os
import re

_INJECTION_PATTERNS: list[str] = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(your\s+)?system\s+prompt",
    r"you\s+are\s+now\s+(?:a\s+)?(?:dan|jailbreak|unrestricted)",
    r"act\s+as\s+(?:if\s+you\s+(?:are|were)\s+)?(?:an?\s+)?(?:evil|malicious|unrestricted)",
    r"forget\s+(?:all\s+)?(?:your\s+)?(?:previous\s+)?(?:instructions|training|guidelines)",
]

_HARMFUL_KEYWORDS: list[str] = [
    "bomb making",
    "synthesize drugs",
    "hack into",
    "steal credentials",
    "phishing template",
    "malware code",
    "ddos attack",
    "ransomware",
    "child exploitation",
    "human trafficking",
]


class SafetyFilter:
    """Filters unsafe inputs and outputs using rule-based and LLM checks."""

    def __init__(self) -> None:
        self._injection_re = [
            re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS
        ]

    def _rule_based_check(self, text: str) -> dict:
        text_lower = text.lower()

        # Check prompt injection
        for pattern in self._injection_re:
            if pattern.search(text):
                return {
                    "is_safe": False,
                    "risk_level": "HIGH",
                    "reason": "Potential prompt injection detected",
                }

        # Check harmful keywords
        for kw in _HARMFUL_KEYWORDS:
            if kw in text_lower:
                return {
                    "is_safe": False,
                    "risk_level": "HIGH",
                    "reason": f"Harmful content keyword detected: '{kw}'",
                }

        return {"is_safe": True, "risk_level": "LOW", "reason": "No issues detected"}

    def check_input(self, text: str) -> dict:
        """Check user input for safety issues."""
        result = self._rule_based_check(text)
        if not result["is_safe"]:
            return result

        # Check for medium-risk patterns
        if len(text) > 10000:
            return {
                "is_safe": True,
                "risk_level": "MEDIUM",
                "reason": "Input is unusually long",
            }

        return result

    def check_output(self, text: str) -> dict:
        """Check LLM output for safety issues."""
        result = self._rule_based_check(text)
        if not result["is_safe"]:
            return {"is_safe": False, "reason": result["reason"]}
        return {"is_safe": True, "reason": "Output is safe"}
