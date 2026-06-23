from __future__ import annotations
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.config import settings
from modules.agents import AgentOrchestrator
from modules.guardrails import GuardrailsPipeline
from modules.kpi import KPITracker
from modules.prompts import PromptLibrary
from modules.multilingual import LanguageDetector
from modules.model_router import ModelRouter
from modules.model_router.llm_factory import create_llm
from modules.audit import AuditLogger
import time, uuid, json

_audit = AuditLogger(db_path="./data/audit.db")

router = APIRouter(tags=["chat"])

_orchestrator: AgentOrchestrator | None = None
_guardrails = GuardrailsPipeline()


def _get_orchestrator() -> AgentOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator(
            model="claude-sonnet-4-6",
            anthropic_api_key=settings.anthropic_api_key,
            mem0_api_key=settings.mem0_api_key,
        )
    return _orchestrator
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
    result = _get_orchestrator().run(guard_result["safe_text"], user_id=user_id)

    output_guard = _guardrails.process_output(result["response"])
    latency_ms = round((time.time() - t0) * 1000, 2)
    _kpi_tracker.track_call(result.get("agent_used", "orchestrator"), latency_ms, 500, True, model)

    _audit.log(
        event_type="chat",
        user_id=user_id,
        input_text=req.message,
        output_text=output_guard["safe_text"],
        model_used=model,
        agent_used=result.get("agent_used", ""),
        confidence_score=0.75,
        decision="auto_approved",
        tool_calls=result.get("tool_calls", []),
        pii_detected=bool(guard_result.get("pii_removed")),
        latency_ms=latency_ms,
        adapter=req.adapter,
    )

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


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """Server-Sent Events streaming chat endpoint."""
    session_id = req.session_id or str(uuid.uuid4())[:8]
    user_id = req.user_id or session_id
    lang = _lang_detector.detect(req.message)
    guard_result = _guardrails.process_input(req.message)

    async def generate():
        t0 = time.time()
        if not guard_result["is_safe"]:
            yield f"data: {json.dumps({'type': 'error', 'message': 'Request blocked by safety filter'})}\n\n"
            return

        provider, model = _model_router.route_with_provider(
            req.message, provider=settings.preferred_provider
        )
        api_key = {
            "openai": settings.openai_api_key,
            "google": settings.google_api_key,
        }.get(provider, settings.anthropic_api_key)
        system_prompt = _prompt_library.get_system_prompt(req.adapter)

        from langchain_core.messages import HumanMessage, SystemMessage
        from modules.agents.tools import get_all_tools
        from langgraph.prebuilt import create_react_agent

        llm = create_llm(provider, model, api_key=api_key, max_tokens=1024, streaming=True)
        agent = create_react_agent(llm, tools=get_all_tools())
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=guard_result["safe_text"])]

        full_response = ""
        tool_calls = []
        agent_used = "domain_expert"

        try:
            async for event in agent.astream_events({"messages": messages}, version="v2"):
                kind = event["event"]
                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"].content
                    if chunk:
                        full_response += chunk
                        yield f"data: {json.dumps({'type': 'token', 'chunk': chunk})}\n\n"
                elif kind == "on_tool_start":
                    tool_name = event.get("name", "tool")
                    tool_calls.append({"tool": tool_name, "input": str(event["data"].get("input", ""))})
                    yield f"data: {json.dumps({'type': 'tool_start', 'tool': tool_name})}\n\n"
                elif kind == "on_tool_end":
                    yield f"data: {json.dumps({'type': 'tool_end', 'tool': event.get('name', '')})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"
            return

        output_guard = _guardrails.process_output(full_response)
        latency_ms = round((time.time() - t0) * 1000, 2)
        _kpi_tracker.track_call(agent_used, latency_ms, len(full_response.split()), True, model)

        # Persist to Mem0
        orch = _get_orchestrator()
        orch._memory and orch._memory.add(
            [{"role": "user", "content": req.message}, {"role": "assistant", "content": full_response}],
            user_id=user_id,
        )

        yield f"data: {json.dumps({'type': 'done', 'metadata': {'agent_used': agent_used, 'provider': provider, 'model_used': model, 'latency_ms': latency_ms, 'tool_calls': tool_calls, 'session_id': session_id, 'language_detected': lang}})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
