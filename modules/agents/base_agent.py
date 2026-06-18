from __future__ import annotations
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from .tools import get_all_tools
import time

class BaseAgent:
    """ReAct agent built with LangGraph prebuilt create_react_agent."""

    def __init__(
        self,
        name: str,
        system_prompt: str,
        tools: list | None = None,
        model: str = "claude-sonnet-4-6",
        anthropic_api_key: str = "",
        max_iterations: int = 10,
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.model_name = model
        llm = ChatAnthropic(model=model, api_key=anthropic_api_key, max_tokens=2048)
        agent_tools = tools if tools is not None else get_all_tools()
        self.graph = create_react_agent(llm, tools=agent_tools)

    def run(self, user_message: str) -> dict:
        """Run the agent and return response with metadata."""
        t0 = time.time()
        messages = [SystemMessage(content=self.system_prompt), HumanMessage(content=user_message)]
        result = self.graph.invoke({"messages": messages})
        final = result["messages"][-1].content
        tool_calls = [
            {"tool": m.name, "input": m.content}
            for m in result["messages"]
            if hasattr(m, "name") and m.name
        ]
        return {
            "response": final,
            "agent": self.name,
            "tool_calls": tool_calls,
            "latency_ms": round((time.time() - t0) * 1000, 2),
        }
