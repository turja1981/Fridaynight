from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from backend.config import settings
from modules.agents import AgentOrchestrator
from modules.guardrails import GuardrailsPipeline
from modules.kpi import KPITracker
from modules.prompts import PromptLibrary
from modules.multilingual import LanguageDetector
from modules.model_router import ModelRouter
import time, uuid

router = APIRouter(tags=["chat"])

_orchestrator = AgentOrchestrator(
    model="claude-sonnet-4-6",
    anthropic_api_key=settings.anthropic_api_key,
    mem0_api_key=settings.mem0_api_key,
)
_guardrails = GuardrailsPipeline()
_kpi_tracker = KPITracker()
_prompt_library = PromptLibrary()
_lang_detector = LanguageDetector()
_model_router = ModelRouter()

class ChatRequest(BaseModel):
    message: str
    adapter: str = "insurance_claims"
    session_id: str | None = None
    user_id: str | None = None

@router.post("/chat")
async def chat(req: ChatRequest):
    t0 = time.time()
    session_id = req.session_id or str(uuid.uuid4())[:8]
    lang = _lang_detector.detect(req.message)
    guard_result = _guardrails.process_input(req.message)
    if not guard_result["is_safe"]:
        return {"response": "I cannot process this request.", "blocked": True, "reason": guard_result.get("blocked_reason"), "session_id": session_id}

    system_prompt = _prompt_library.get_system_prompt(req.adapter)
    model = _model_router.route(req.message)
    user_id = req.user_id or session_id
    result = _orchestrator.run(guard_result["safe_text"], user_id=user_id)

    output_guard = _guardrails.process_output(result["response"])
    latency_ms = round((time.time() - t0) * 1000, 2)
    _kpi_tracker.track_call(result.get("agent_used", "orchestrator"), latency_ms, 500, True, model)

    return {
        "response": output_guard["safe_text"],
        "agent_used": result.get("agent_used"),
        "model_used": model,
        "latency_ms": latency_ms,
        "tokens_used": 500,
        "tool_calls": result.get("tool_calls", []),
        "session_id": session_id,
        "language_detected": lang,
    }
