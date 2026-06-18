from __future__ import annotations
import time
import uuid
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Chat request body."""
    message: str
    adapter: str = "insurance_claims"
    session_id: Optional[str] = None


@router.post("")
async def chat(body: ChatRequest) -> dict:
    """Process a chat message through guardrails, agents, and return response."""
    from modules.guardrails.pipeline import GuardrailsPipeline
    from modules.agents.orchestrator import AgentOrchestrator
    from modules.multilingual.language import LanguageDetector, Translator
    from modules.kpi.tracker import KPITracker
    from modules.prompts.library import PromptLibrary
    from backend.config import settings

    session_id = body.session_id or str(uuid.uuid4())
    start_time = time.perf_counter()

    guardrails = GuardrailsPipeline()
    input_result = guardrails.process_input(body.message)
    if not input_result["is_safe"]:
        return {
            "response": f"Message blocked: {input_result['blocked_reason']}",
            "agent_used": "guardrails",
            "model_used": None,
            "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
            "tokens_used": 0,
            "tool_calls": [],
            "session_id": session_id,
            "language_detected": "en",
            "blocked": True,
        }

    safe_message = input_result["safe_text"]

    # Language detection
    detector = LanguageDetector()
    detected_lang = detector.detect(safe_message)

    # Translate to English if needed
    if detected_lang != "en":
        translator = Translator()
        safe_message = translator.translate(safe_message, "en")

    # Get domain system prompt
    library = PromptLibrary()
    system_prompt = library.get_system_prompt(body.adapter)

    # Run orchestrator
    orchestrator = AgentOrchestrator()
    # Override the routing with domain context
    agent_result = orchestrator.run(safe_message)

    # Process output through guardrails
    output_result = guardrails.process_output(agent_result.get("response", ""))
    final_response = output_result["safe_text"]

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # Track KPIs
    tracker = KPITracker()
    tracker.track_call(
        agent_name=agent_result.get("agent_used", "unknown"),
        latency_ms=latency_ms,
        tokens_used=agent_result.get("tokens_used", 0),
        success=True,
        model="claude-sonnet-4-6",
    )

    return {
        "response": final_response,
        "agent_used": agent_result.get("agent_used", "unknown"),
        "model_used": "claude-sonnet-4-6",
        "latency_ms": latency_ms,
        "tokens_used": agent_result.get("tokens_used", 0),
        "tool_calls": agent_result.get("tool_calls", []),
        "session_id": session_id,
        "language_detected": detected_lang,
        "blocked": False,
    }
