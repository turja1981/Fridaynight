from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from backend.config import settings
from modules.agents import AgentOrchestrator

router = APIRouter(tags=["agents"])
_orchestrator = AgentOrchestrator(anthropic_api_key=settings.anthropic_api_key)

class AgentRunRequest(BaseModel):
    task: str
    agent_type: str = "auto"

@router.post("/agents/run")
async def run_agent(req: AgentRunRequest):
    return _orchestrator.run(req.task, req.agent_type)

@router.get("/agents/list")
async def list_agents():
    return {"agents": ["research", "analysis", "customer_service", "domain_expert"]}
