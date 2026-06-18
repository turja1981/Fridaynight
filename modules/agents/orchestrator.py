from __future__ import annotations

from .base_agent import BaseAgent
from .tools import ToolRegistry


def _make_research_agent() -> BaseAgent:
    registry = ToolRegistry()
    tools = registry.get_tools_by_name(["web_search", "document_lookup", "datetime_tool"])
    return BaseAgent(
        name="research_agent",
        system_prompt=(
            "You are an expert research agent. Your job is to find accurate, comprehensive information "
            "on any topic. Use web_search and document_lookup tools to gather evidence before responding. "
            "Always cite your sources and provide structured, well-organized answers."
        ),
        tools=tools,
    )


def _make_analysis_agent() -> BaseAgent:
    registry = ToolRegistry()
    tools = registry.get_tools_by_name(["calculator", "data_query", "document_lookup"])
    return BaseAgent(
        name="analysis_agent",
        system_prompt=(
            "You are a data analysis expert. Analyze data, compute statistics, identify trends, "
            "and provide actionable insights. Use the calculator for precise computations and "
            "data_query to retrieve business data. Present findings clearly with numbers and percentages."
        ),
        tools=tools,
    )


def _make_customer_service_agent() -> BaseAgent:
    registry = ToolRegistry()
    tools = registry.get_tools_by_name(["data_query", "document_lookup", "datetime_tool"])
    return BaseAgent(
        name="customer_service_agent",
        system_prompt=(
            "You are a friendly and professional customer service representative. "
            "Help customers with their queries about claims, policies, accounts, or orders. "
            "Use data_query to look up customer records. Always be empathetic, clear, and solution-focused. "
            "Escalate complex issues appropriately."
        ),
        tools=tools,
    )


def _make_data_agent() -> BaseAgent:
    registry = ToolRegistry()
    tools = registry.get_tools_by_name(["data_query", "calculator"])
    return BaseAgent(
        name="data_agent",
        system_prompt=(
            "You are a data retrieval and processing agent. Efficiently query databases, "
            "compute aggregates, and return structured data. Focus on accuracy and speed. "
            "Return data in JSON-friendly formats when possible."
        ),
        tools=tools,
    )


class AgentOrchestrator:
    """Routes tasks to specialized agents and manages their execution."""

    _ROUTING_KEYWORDS: dict[str, list[str]] = {
        "research_agent": ["research", "find", "search", "what is", "explain", "define", "history", "news"],
        "analysis_agent": ["analyze", "calculate", "compare", "statistics", "trend", "metrics", "kpi", "performance"],
        "customer_service_agent": ["claim", "policy", "account", "customer", "help", "support", "status", "complaint"],
        "data_agent": ["data", "query", "fetch", "retrieve", "lookup", "get", "show", "list"],
    }

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {
            "research_agent": _make_research_agent(),
            "analysis_agent": _make_analysis_agent(),
            "customer_service_agent": _make_customer_service_agent(),
            "data_agent": _make_data_agent(),
        }

    def route(self, task: str) -> str:
        """Pick best agent for task using keyword routing."""
        task_lower = task.lower()
        scores: dict[str, int] = {name: 0 for name in self._agents}
        for agent_name, keywords in self._ROUTING_KEYWORDS.items():
            for kw in keywords:
                if kw in task_lower:
                    scores[agent_name] += 1
        best = max(scores, key=lambda k: scores[k])
        # Default to research_agent if no match
        if scores[best] == 0:
            return "research_agent"
        return best

    def run(self, task: str, agent_type: str = "auto") -> dict:
        """Run appropriate agent and return result with agent_used field."""
        if agent_type == "auto":
            agent_name = self.route(task)
        elif agent_type in self._agents:
            agent_name = agent_type
        else:
            agent_name = "research_agent"

        agent = self._agents[agent_name]
        result = agent.run(task)
        result["agent_used"] = agent_name
        return result

    def list_agents(self) -> list[dict]:
        """Return info about available agents."""
        return [
            {"name": name, "model": agent.model}
            for name, agent in self._agents.items()
        ]
