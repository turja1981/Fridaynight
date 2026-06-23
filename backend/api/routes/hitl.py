from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from backend.config import settings
from modules.agents import HITLOrchestrator
from modules.prompts import PromptLibrary

router = APIRouter(tags=["hitl"])
_hitl = HITLOrchestrator()
_prompts = PromptLibrary()


class HITLRunRequest(BaseModel):
    task: str
    user_id: str = "default"
    adapter: str = "insurance_claims"


class HITLApproveRequest(BaseModel):
    reviewer_note: str = ""


class HITLRejectRequest(BaseModel):
    reason: str = ""


@router.post("/hitl/run")
async def run_hitl_task(req: HITLRunRequest):
    """Run a task through the confidence-gated HITL pipeline."""
    system_prompt = _prompts.get_system_prompt(req.adapter)
    return _hitl.run(req.task, user_id=req.user_id, system_prompt=system_prompt)


@router.post("/hitl/{task_id}/approve")
async def approve_hitl_task(task_id: str, req: HITLApproveRequest):
    """Human approves a pending HITL task — resumes the LangGraph checkpoint."""
    return _hitl.approve(task_id, reviewer_note=req.reviewer_note)


@router.post("/hitl/{task_id}/reject")
async def reject_hitl_task(task_id: str, req: HITLRejectRequest):
    """Human rejects a pending HITL task."""
    return _hitl.reject(task_id, reason=req.reason)
