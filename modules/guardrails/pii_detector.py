from __future__ import annotations
import re


class PIIDetector:
    """Detects and redacts PII from text using regex patterns."""

    _PATTERNS: dict[str, str] = {
        "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "PHONE_IN": r"(?:\+91[\s\-]?)?[6-9]\d{9}\b",
        "PHONE_INTL": r"\+?[1-9]\d{1,14}\b",
        "AADHAAR": r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b",
        "PAN": r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
        "CREDIT_CARD": r"\b(?:\d{4}[\s\-]?){3}\d{4}\b",
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
        "IP_ADDRESS": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    }

    def __init__(self) -> None:
        self._compiled: dict[str, re.Pattern] = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self._PATTERNS.items()
        }

    def detect(self, text: str) -> list[dict]:
        """Detect PII entities in text, return list of found entities."""
        entities: list[dict] = []
        for entity_type, pattern in self._compiled.items():
            for match in pattern.finditer(text):
                entities.append(
                    {
                        "entity_type": entity_type,
                        "value": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                    }
                )
        # Sort by start position
        entities.sort(key=lambda e: e["start"])
        return entities

    def redact(self, text: str, replacement: str = "[REDACTED]") -> str:
        """Replace all detected PII with the replacement string."""
        result = text
        for entity_type, pattern in self._compiled.items():
            result = pattern.sub(replacement, result)
        return result

    def scan(self, text: str) -> dict:
        """Scan text and return has_pii flag, entities, and redacted text."""
        entities = self.detect(text)
        redacted = self.redact(text) if entities else text
        return {
            "has_pii": len(entities) > 0,
            "entities": entities,
            "redacted_text": redacted,
        }
