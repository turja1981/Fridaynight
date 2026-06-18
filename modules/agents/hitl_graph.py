from __future__ import annotations
import time
import uuid
from typing import TypedDict, Annotated
import operator
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from .tools import get_all_tools


class HITLState(TypedDict):
    task: str
    user_id: str
    response: str
    confidence: float
    decision: str          # "auto_approved" | "pending_review" | "escalated" | "rejected"
    agent_used: str
    tool_calls: list
    system_prompt: str
    messages: Annotated[list, operator.add]


def _compute_confidence(response: str, tool_calls: list) -> float:
    """Heuristic confidence scoring based on response characteristics."""
    score = 0.70
    if tool_calls:
        score += 0.05 * min(len(tool_calls), 3)
    uncertainty = ["i'm not sure", "uncertain", "might be", "possibly", "i don't know", "cannot determine", "unclear"]
    if any(p in response.lower() for p in uncertainty):
        score -= 0.25
    if len(response) > 150 and any(w in response.lower() for w in ["based on", "according to", "analysis shows", "therefore", "assessment:"]):
        score += 0.10
    return round(min(max(score, 0.05), 0.98), 3)


def _assess_node(state: HITLState) -> dict:
    """Run domain agent and compute confidence score."""
    llm = ChatAnthropic(model="claude-sonnet-4-6", max_tokens=1024)
    agent = create_react_agent(llm, tools=get_all_tools())
    messages = [SystemMessage(content=state["system_prompt"]), HumanMessage(content=state["task"])]
    result = agent.invoke({"messages": messages})
    final = result["messages"][-1].content
    tool_calls = [
        {"tool": m.name, "input": m.content}
        for m in result["messages"]
        if hasattr(m, "name") and m.name
    ]
    confidence = _compute_confidence(final, tool_calls)
    return {
        "response": final,
        "confidence": confidence,
        "tool_calls": tool_calls,
        "messages": [AIMessage(content=final)],
    }


def _route_by_confidence(state: HITLState) -> str:
    if state["confidence"] >= 0.85:
        return "auto_complete"
    elif state["confidence"] >= 0.50:
        return "human_review"
    else:
        return "escalate"


def _auto_complete_node(state: HITLState) -> dict:
    return {"decision": "auto_approved", "agent_used": "domain_expert"}


def _escalate_node(state: HITLState) -> dict:
    return {"decision": "escalated", "agent_used": "domain_expert"}


def _human_review_node(state: HITLState) -> dict:
    """LangGraph will interrupt BEFORE this node when configured with interrupt_before."""
    return {"decision": "pending_review", "agent_used": "domain_expert"}


# Build the graph
_builder = StateGraph(HITLState)
_builder.add_node("assess", _assess_node)
_builder.add_node("auto_complete", _auto_complete_node)
_builder.add_node("human_review", _human_review_node)
_builder.add_node("escalate", _escalate_node)
_builder.set_entry_point("assess")
_builder.add_conditional_edges("assess", _route_by_confidence, {
    "auto_complete": "auto_complete",
    "human_review": "human_review",
    "escalate": "escalate",
})
_builder.add_edge("auto_complete", END)
_builder.add_edge("human_review", END)
_builder.add_edge("escalate", END)

_checkpointer = MemorySaver()
HITL_GRAPH = _builder.compile(
    checkpointer=_checkpointer,
    interrupt_before=["human_review"],
)


class HITLOrchestrator:
    """Runs tasks through confidence-gated HITL LangGraph pipeline."""

    def run(
        self,
        task: str,
        user_id: str = "default",
        system_prompt: str = "You are a helpful enterprise AI assistant.",
    ) -> dict:
        task_id = str(uuid.uuid4())[:12]
        config = {"configurable": {"thread_id": task_id}}
        initial_state: HITLState = {
            "task": task,
            "user_id": user_id,
            "response": "",
            "confidence": 0.0,
            "decision": "",
            "agent_used": "",
            "tool_calls": [],
            "system_prompt": system_prompt,
            "messages": [],
        }
        HITL_GRAPH.invoke(initial_state, config=config)
        snapshot = HITL_GRAPH.get_state(config)
        state = snapshot.values

        if snapshot.next:
            # Interrupted before human_review — needs approval
            return {
                "status": "pending_review",
                "task_id": task_id,
                "confidence": state.get("confidence", 0.0),
                "response_preview": state.get("response", "")[:200],
                "tool_calls": state.get("tool_calls", []),
            }
        return {
            "status": "completed",
            "task_id": task_id,
            "response": state.get("response", ""),
            "confidence": state.get("confidence", 0.0),
            "decision": state.get("decision", "auto_approved"),
            "tool_calls": state.get("tool_calls", []),
            "agent_used": state.get("agent_used", ""),
        }

    def approve(self, task_id: str, reviewer_note: str = "") -> dict:
        """Resume a HITL-interrupted graph after human approval."""
        config = {"configurable": {"thread_id": task_id}}
        HITL_GRAPH.invoke(None, config=config)
        snapshot = HITL_GRAPH.get_state(config)
        state = snapshot.values
        return {
            "status": "approved",
            "task_id": task_id,
            "response": state.get("response", ""),
            "decision": "approved_by_human",
            "reviewer_note": reviewer_note,
        }

    def reject(self, task_id: str, reason: str = "") -> dict:
        """Mark a pending task as rejected without resuming graph."""
        return {
            "status": "rejected",
            "task_id": task_id,
            "decision": "rejected_by_human",
            "reason": reason,
        }
