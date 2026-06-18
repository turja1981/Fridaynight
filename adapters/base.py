from __future__ import annotations
from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    """Abstract base class for domain adapters."""

    domain_name: str = ""
    system_prompt: str = ""
    kpi_definitions: dict[str, str] = {}
    suggested_tools: list[str] = []
    sample_questions: list[str] = []

    @abstractmethod
    def get_config(self) -> dict:
        """Return adapter configuration dict."""
        ...

    def get_sample_context(self) -> str:
        """Return domain-specific context text for demo purposes."""
        return f"Domain: {self.domain_name}\nThis adapter provides {self.domain_name} capabilities."
