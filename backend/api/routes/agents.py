from __future__ import annotations
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


class AgentRunRequest(BaseModel):
    """Agent run request body."""
    task: str
    agent_type: str = "auto"


@router.post("/run")
async def run_agent(body: AgentRunRequest) -> dict:
    """Run an agent on the given task."""
    from modules.agents.orchestrator import AgentOrchestrator

    orchestrator = AgentOrchestrator()
    result = orchestrator.run(body.task, agent_type=body.agent_type)
    return result


@router.get("/list")
async def list_agents() -> dict:
    """List available agents and their capabilities."""
    from modules.agents.orchestrator import AgentOrchestrator

    orchestrator = AgentOrchestrator()
    return {"agents": orchestrator.list_agents()}
