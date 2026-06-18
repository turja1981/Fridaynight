from __future__ import annotations
from .base_agent import BaseAgent
from .tools import ToolRegistry

AGENT_CONFIGS: dict[str, dict] = {
    "research_agent": {
        "system": "You are a research specialist. Find information, search data, and provide comprehensive background analysis.",
        "tools": ["web_search", "data_query", "datetime_tool"],
    },
    "analysis_agent": {
        "system": "You are a data analyst. Analyze numbers, compute statistics, identify patterns and anomalies.",
        "tools": ["calculator", "data_query"],
    },
    "customer_service_agent": {
        "system": "You are a customer service specialist. Respond empathetically, resolve issues, and escalate when needed.",
        "tools": ["data_query", "datetime_tool"],
    },
    "data_agent": {
        "system": "You are a data retrieval specialist. Query records, fetch data, and provide structured information.",
        "tools": ["data_query", "web_search"],
    },
}


def _route_task(task: str) -> str:
    task_lower = task.lower()
    if any(w in task_lower for w in ["claim", "policy", "status", "account", "issue", "complaint"]):
        return "customer_service_agent"
    if any(w in task_lower for w in ["analyze", "analysis", "calculate", "metric", "performance"]):
        return "analysis_agent"
    if any(w in task_lower for w in ["query", "fetch", "data", "record", "lookup"]):
        return "data_agent"
    return "research_agent"


class AgentOrchestrator:
    """Multi-agent supervisor that routes tasks to specialised BaseAgent instances."""

    def __init__(self, model: str = "claude-sonnet-4-6", anthropic_api_key: str = "", mem0_api_key: str = ""):
        self.model = model
        self.api_key = anthropic_api_key
        self._registry = ToolRegistry()
        try:
            from modules.memory import AgentMemoryManager
            self._memory = AgentMemoryManager(anthropic_api_key=anthropic_api_key, mem0_api_key=mem0_api_key)
        except Exception:
            self._memory = None

    def route(self, task: str) -> str:
        return _route_task(task)

    def list_agents(self) -> list[dict]:
        return [{"name": name, "description": cfg["system"][:80]} for name, cfg in AGENT_CONFIGS.items()]

    def run(self, task: str, agent_type: str = "auto", user_id: str = "default") -> dict:
        """Route task to best agent and return response."""
        chosen = agent_type if agent_type != "auto" else _route_task(task)
        if chosen not in AGENT_CONFIGS:
            chosen = "research_agent"

        cfg = AGENT_CONFIGS[chosen]
        tools = self._registry.get_tools_by_name(cfg["tools"])

        system = cfg["system"]
        if self._memory:
            try:
                mem_context = self._memory.build_memory_context(task, user_id)
                if mem_context:
                    system = f"{system}\n\n{mem_context}"
            except Exception:
                pass

        agent = BaseAgent(
            name=chosen,
            system_prompt=system,
            tools=tools,
            model=self.model,
            anthropic_api_key=self.api_key,
        )
        result = agent.run(task)

        if self._memory:
            try:
                self._memory.add(
                    [{"role": "user", "content": task}, {"role": "assistant", "content": result["response"]}],
                    user_id=user_id,
                )
            except Exception:
                pass

        return {
            "response": result["response"],
            "agent_used": chosen,
            "tool_calls": result.get("tool_calls", []),
        }
