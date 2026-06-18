from __future__ import annotations
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from typing import TypedDict, Annotated
import operator
from .tools import get_all_tools, data_query_tool, calculator_tool, web_search_tool, datetime_tool

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    next_agent: str
    task: str

AGENT_CONFIGS = {
    "research": {
        "system": "You are a research specialist. Find information, search data, and provide comprehensive background analysis.",
        "tools": [web_search_tool, data_query_tool, datetime_tool],
    },
    "analysis": {
        "system": "You are a data analyst. Analyze numbers, compute statistics, identify patterns and anomalies.",
        "tools": [calculator_tool, data_query_tool],
    },
    "customer_service": {
        "system": "You are a customer service specialist. Respond empathetically, resolve issues, and escalate when needed.",
        "tools": [data_query_tool, datetime_tool],
    },
    "domain_expert": {
        "system": "You are a domain expert for enterprise business processes including insurance, banking, and manufacturing.",
        "tools": get_all_tools(),
    },
}

def _route_task(task: str) -> str:
    task_lower = task.lower()
    if any(w in task_lower for w in ["calculate", "compute", "analyze", "statistics", "number"]):
        return "analysis"
    if any(w in task_lower for w in ["customer", "complaint", "help", "support", "issue"]):
        return "customer_service"
    if any(w in task_lower for w in ["search", "find", "research", "what is", "who is"]):
        return "research"
    return "domain_expert"

class AgentOrchestrator:
    """Multi-agent supervisor that routes tasks to specialized LangGraph agents."""

    def __init__(self, model: str = "claude-sonnet-4-6", anthropic_api_key: str = "", mem0_api_key: str = ""):
        self.model = model
        self.api_key = anthropic_api_key
        self._agents: dict = {}
        # Lazy import to avoid hard dependency at module load time
        try:
            from modules.memory import AgentMemoryManager
            self._memory = AgentMemoryManager(anthropic_api_key=anthropic_api_key, mem0_api_key=mem0_api_key)
        except Exception:
            self._memory = None

    def _get_agent(self, name: str):
        if name not in self._agents:
            cfg = AGENT_CONFIGS[name]
            llm = ChatAnthropic(model=self.model, api_key=self.api_key, max_tokens=2048)
            self._agents[name] = create_react_agent(llm, tools=cfg["tools"])
        return self._agents[name]

    def route(self, task: str) -> str:
        return _route_task(task)

    def run(self, task: str, agent_type: str = "auto", user_id: str = "default") -> dict:
        """Route task to best agent, inject Mem0 memory context, store result."""
        chosen = agent_type if agent_type != "auto" else _route_task(task)
        if chosen not in AGENT_CONFIGS:
            chosen = "domain_expert"

        cfg = AGENT_CONFIGS[chosen]
        agent = self._get_agent(chosen)

        # Inject relevant memories from Mem0 into the system prompt
        system = cfg["system"]
        if self._memory:
            mem_context = self._memory.build_memory_context(task, user_id)
            if mem_context:
                system = f"{system}\n\n{mem_context}"

        messages = [SystemMessage(content=system), HumanMessage(content=task)]
        result = agent.invoke({"messages": messages})
        final = result["messages"][-1].content

        # Persist this turn to Mem0
        if self._memory:
            self._memory.add(
                [{"role": "user", "content": task}, {"role": "assistant", "content": final}],
                user_id=user_id,
            )

        tool_calls = [
            {"tool": m.name, "input": m.content}
            for m in result["messages"]
            if hasattr(m, "name") and m.name
        ]
        return {"response": final, "agent_used": chosen, "tool_calls": tool_calls}
