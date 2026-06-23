from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

@dataclass
class BaseAdapter(ABC):
    """Base class for domain-specific hackathon adapters."""
    domain_name: str = ""
    system_prompt: str = ""
    kpi_definitions: dict[str, str] = field(default_factory=dict)
    suggested_tools: list[str] = field(default_factory=list)
    sample_questions: list[str] = field(default_factory=list)

    @abstractmethod
    def get_config(self) -> dict: ...

    def get_sample_context(self) -> str:
        return f"Domain: {self.domain_name}"
