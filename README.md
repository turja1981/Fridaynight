# Enterprise AI Platform — TCS Hackathon 2025

A plug-and-play enterprise AI platform built for TCS Hackathons. Receive a problem statement, configure the domain adapter, and demo a production-grade AI solution — all in under 10 hours.

---

## Live Demo Flow (10 minutes)

| Step | What to show | Criterion |
|---|---|---|
| 1 | Login as admin / analyst / viewer | RBAC (15) |
| 2 | Chat → agent routing badge + tool calls | Agentic AI (8, 9) |
| 3 | Type Aadhaar number → PII redacted | Responsible AI (16) |
| 4 | Ask in Hindi → language detected | Multilingual (19) |
| 5 | Click mic → voice transcript → response | Voice Interface (20) |
| 6 | Upload PDF → ask about its contents | RAG (5, 7) |
| 7 | HITL flow → pending → approve | Human-in-the-Loop (11) |
| 8 | KPI Dashboard tab → recharts + ROI | KPI Dashboard (13) |
| 9 | `GET /audit/logs` → append-only trail | Logs & Audit (12) |
| 10 | Show `modules/` tree | Modularity (1) |

---

## Quick Start

```bash
cp .env.example .env
# Set ANTHROPIC_API_KEY and ACTIVE_ADAPTER in .env

pip install -r requirements.txt
uvicorn backend.main:app --reload        # API → http://localhost:8000

cd frontend && npm install && npm run dev # UI  → http://localhost:5173
```

Verify:
```bash
curl http://localhost:8000/health
# {"status":"ok","version":"1.0.0","adapter":"insurance_claims"}
```

---

## Architecture

```
User Request
     │
     ▼
FastAPI (backend/main.py)
     │
     ├─ /api/v1/auth/        JWT login + RBAC roles
     ├─ /api/v1/chat/        Guardrails → Model Router → Agent Orchestrator → Audit
     ├─ /api/v1/chat/stream  SSE streaming with LangGraph ReAct agent
     ├─ /api/v1/rag/         Hybrid retrieval (vector + BM25 + RRF)
     ├─ /api/v1/agents/      Direct agent execution
     ├─ /api/v1/hitl/        LangGraph interrupt-before HITL
     ├─ /api/v1/kpi/         KPI dashboard + metrics
     ├─ /api/v1/voice/       Whisper transcription + synthesis
     ├─ /api/v1/memory/      Mem0 persistent memory
     ├─ /api/v1/audit/       SQLite append-only audit log
     ├─ /api/v1/multimodal/  Claude Vision
     └─ /api/v1/mcp/         JSON-RPC 2.0 tool server
```

**AI Stack**: LangChain LCEL · LangGraph · Claude (Haiku / Sonnet / Opus) · OpenAI · Gemini  
**Retrieval**: Qdrant vector store · HuggingFace `all-MiniLM-L6-v2` · BM25 · RRF hybrid fusion  
**Evaluation**: RAGAS (retrieval quality) · DeepEval (output quality)  
**Observability**: LangSmith tracing · structlog JSON logs

---

## Multi-Provider LLM Support

The platform routes tasks to the most cost-effective model across **three providers**:

| Complexity | Anthropic | OpenAI | Google |
|---|---|---|---|
| Low | `claude-haiku-4-5` | `gpt-4o-mini` | `gemini-1.5-flash` |
| Medium | `claude-sonnet-4-6` | `gpt-4o` | `gemini-1.5-pro` |
| High | `claude-opus-4-8` | `gpt-4o` | `gemini-1.5-pro` |

Set `PREFERRED_PROVIDER=openai` or `PREFERRED_PROVIDER=google` in `.env` to switch providers for the streaming endpoint. The non-streaming endpoint and agent orchestrator default to Anthropic.

---

## Domain Adapter System

Switch the entire AI persona with one environment variable:

```bash
ACTIVE_ADAPTER=insurance_claims   # or: banking | manufacturing | retail
```

Each adapter defines the system prompt, KPIs, sample data, and suggested tools.  
See [ADAPTER_GUIDE.md](ADAPTER_GUIDE.md) to create a new domain adapter in minutes.

---

## Module Reference

| Module | Purpose |
|---|---|
| `modules/rag/` | `DocumentIngester`, `HybridRetriever`, `RagPipeline` |
| `modules/agents/` | `AgentOrchestrator`, `HITLOrchestrator`, `ToolRegistry` |
| `modules/guardrails/` | PII detection, prompt injection filter, safety pipeline |
| `modules/rbac/` | JWT auth, role-based permissions (ADMIN / ANALYST / VIEWER) |
| `modules/kpi/` | `KPITracker`, `KPIDashboard`, domain metrics, ROI calculator |
| `modules/audit/` | SQLite audit logger with structured event querying |
| `modules/model_router/` | Complexity-based routing across Anthropic / OpenAI / Google |
| `modules/memory/` | Mem0 persistent memory with in-process fallback |
| `modules/prompts/` | Few-shot prompt library, adapter-specific system prompts |
| `modules/multilingual/` | Language detection + translation (langdetect + Claude) |
| `modules/voice/` | Whisper transcription, text-to-speech synthesis |
| `modules/evaluation/` | RAGAS + DeepEval quality metrics |
| `modules/mcp/` | JSON-RPC 2.0 MCP tool server |
| `modules/observability/` | LangSmith tracing, structlog JSON |

---

## Demo Users (hardcoded)

| Username | Password | Role |
|---|---|---|
| admin | admin123 | ADMIN |
| analyst | analyst123 | ANALYST |
| viewer | viewer123 | VIEWER |

---

## Environment Variables

```env
ANTHROPIC_API_KEY=sk-ant-...        # Required
JWT_SECRET=change-this              # Required
ACTIVE_ADAPTER=insurance_claims     # Domain adapter
QDRANT_PATH=./data/qdrant           # Vector DB path

# Multi-provider LLM (optional)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
PREFERRED_PROVIDER=anthropic        # anthropic | openai | google

# LangSmith tracing (optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=tcs-hackathon-2025

# Mem0 persistent memory (optional)
MEM0_API_KEY=
```

---

## Running Tests

```bash
pytest modules/rag/tests/          -v   # RAG pipeline
pytest modules/agents/tests/       -v   # Agent orchestrator + HITL
pytest modules/rbac/tests/         -v   # Auth + permissions
pytest modules/guardrails/tests/   -v   # PII + safety filters
pytest modules/model_router/tests/ -v   # Multi-provider routing (19 tests)
pytest modules/kpi/tests/          -v   # KPI tracker + dashboard
pytest modules/audit/tests/        -v   # Audit logger
pytest modules/mcp/tests/          -v   # JSON-RPC MCP server
pytest backend/tests/              -v   # API integration tests
```

---

## Hackathon Day Playbook

```
/analyze-usecase   ← paste the problem statement
/bootstrap-domain  ← configure adapter for the domain
/wire-modules      ← enable modules the use case needs
/prep-demo         ← generate sample data + demo script
/validate-solution ← run all tests, check health, report readiness
```

See [CLAUDE.md](CLAUDE.md) for the full 10-step guide and module API reference.

---

## Docker

```bash
docker-compose up --build
# API: http://localhost:8000
# UI:  http://localhost:5173
```
