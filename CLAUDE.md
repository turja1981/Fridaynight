# Enterprise AI Platform — Claude Code Guide

This is a pre-built, pluggable Enterprise AI Platform for TCS Hackathons.
On hackathon day you receive a 500–1000 word problem statement and have 10 hours
to deliver a working, demo-ready AI solution. Every module is already built.
Your job is to configure, customise, and assemble.

---

## Hackathon Day — The 10-Step Playbook

```
/analyze-usecase   ← paste the problem statement here first
/bootstrap-domain  ← configure adapter + env for the domain
/wire-modules      ← enable/extend modules the use case needs
/prep-demo         ← generate sample data, queries, demo script
/validate-solution ← run all tests, check health, report readiness
```

Typical time split: 2h analysis+config → 4h domain code → 2h testing → 2h demo polish.

---

## Architecture At A Glance

```
User Request
    │
    ▼
FastAPI (backend/main.py)
    │   CORS + logging middleware + AppException handler
    │
    ├── /api/v1/auth/       → RBAC JWT (modules/rbac/)
    ├── /api/v1/chat/       → Guardrails → Agent → Audit → SSE stream
    ├── /api/v1/rag/        → Ingest / Query (modules/rag/)
    ├── /api/v1/agents/     → Direct agent execution (modules/agents/)
    ├── /api/v1/hitl/       → LangGraph interrupt-before HITL
    ├── /api/v1/kpi/        → KPI dashboard + metrics
    ├── /api/v1/memory/     → Mem0 persistent memory
    ├── /api/v1/audit/      → SQLite audit log
    ├── /api/v1/multimodal/ → Claude Vision
    └── /api/v1/mcp/        → JSON-RPC 2.0 tool server
```

**AI Stack**: LangChain LCEL · LangGraph · Claude (Haiku/Sonnet) · ChromaDB · HuggingFace Embeddings
**Evaluation**: RAGAS (retrieval quality) · DeepEval (output quality, optional)
**Observability**: LangSmith tracing (zero-code, env vars only) · structlog JSON logs
**Memory**: Mem0 (cloud or local) with in-process dict fallback

---

## Module Reference

### `modules/rag/`
| Class | Import | Purpose |
|---|---|---|
| `DocumentIngester` | `from modules.rag.ingestion import DocumentIngester` | Chunk + embed text/PDF/files into ChromaDB |
| `VectorRetriever` | `from modules.rag.retrieval import VectorRetriever` | Semantic search (top-k + min_score filter) |
| `HybridRetriever` | `from modules.rag.hybrid import HybridRetriever` | Vector + BM25 fused via RRF (better recall) |
| `RagPipeline` | `from modules.rag.pipeline import RagPipeline` | End-to-end RAG chain (ingest + run) |
| `RAGEvaluator` | `from modules.rag.evaluation import RAGEvaluator` | RAGAS metrics (optional, ragas must import cleanly) |

**Ingest text:**
```python
ingester = DocumentIngester()
ids = ingester.ingest_text("policy text...", source_name="policy_v1.txt")
```

**Query:**
```python
retriever = HybridRetriever()
results = retriever.retrieve("What is the deductible?", top_k=5)
# returns: [{"content": "...", "score": 0.9, "metadata": {"source": "..."}}]
```

**Full pipeline:**
```python
pipeline = RagPipeline(anthropic_api_key=settings.anthropic_api_key)
result = pipeline.run("What is the claim status for CLM-001?")
# returns: {"answer", "context", "sources", "retrieval_time_ms"}
```

**ChromaDB location**: `./data/chroma` (env: `CHROMA_PATH`)
**Embedding model**: `all-MiniLM-L6-v2` (lazy-loaded, no download at import time)
**Chunk size**: 512 tokens, overlap 50

---

### `modules/agents/`
| Class | Purpose |
|---|---|
| `AgentOrchestrator` | Keyword-routes task → specialized LangGraph ReAct agent |
| `HITLOrchestrator` | Confidence-gated HITL — interrupt_before human_review |
| `BaseAgent` | Raw agent loop (system prompt + tools + Anthropic API) |
| `ToolRegistry` | calculator, datetime, data_query, web_search |

**Agent routing keywords:**
- `customer_service_agent`: claim, policy, account, status, issue, complaint, help
- `analysis_agent`: analyze, calculate, report, metric, performance, trend, comparison
- `data_agent`: query, fetch, retrieve, lookup, find, get, search, record
- `research_agent`: fallback (everything else)

**Run agent:**
```python
orch = AgentOrchestrator(anthropic_api_key=key, mem0_api_key=mem0_key)
result = orch.run("What is the settlement for CLM-001?", user_id="u123")
# returns: {"response", "agent_used", "tokens_used", "tool_calls"}
```

**HITL flow:**
```python
hitl = HITLOrchestrator(anthropic_api_key=key)
result = hitl.run("Approve settlement of ₹500,000", task_id="t1")
# status "completed" (confidence ≥0.85) or "pending_review" (0.5-0.85)
# if pending_review:
result = hitl.approve("t1")   # resumes graph
result = hitl.reject("t1")    # marks rejected
```

**Add a custom tool** (edit `modules/agents/tools.py`):
```python
# In ToolRegistry.execute(), add new elif branch:
elif tool_name == "my_tool":
    # implement and add schema to get_all_tools()
```

---

### `modules/guardrails/`
| Class | Purpose |
|---|---|
| `PIIDetector` | Regex: EMAIL, PHONE, AADHAAR, PAN, CREDIT_CARD, SSN, IP |
| `SafetyFilter` | Prompt injection (5 patterns) + harmful keywords (10) |
| `GuardrailsPipeline` | Combines both: `process_input()` + `process_output()` |

```python
gp = GuardrailsPipeline()
result = gp.process_input("My Aadhaar is 1234 5678 9012")
# {"safe_text": "My Aadhaar is [REDACTED]", "pii_removed": True, "is_safe": True}
```

---

### `modules/rbac/`
Roles: `ADMIN | ANALYST | VIEWER | AGENT`
Permissions: `READ_DATA | WRITE_DATA | RUN_AGENT | VIEW_KPI | MANAGE_USERS | INGEST_DOCUMENTS`

Demo users (hardcoded for hackathon):
| Username | Password | Role |
|---|---|---|
| admin | admin123 | ADMIN |
| analyst | analyst123 | ANALYST |
| viewer | viewer123 | VIEWER |

```python
# FastAPI dependency injection:
from modules.rbac.permissions import require_permission
from modules.rbac.models import Permission

@router.post("/my-endpoint")
async def endpoint(user=Depends(require_permission(Permission.RUN_AGENT))):
    ...
```

---

### `modules/kpi/`
| Class | Purpose |
|---|---|
| `KPITracker` | In-memory call recorder — track_call(agent, latency, tokens, success, model) |
| `MetricsCollector` | Domain KPIs (insurance/banking/manufacturing/retail) + ROI calc |
| `KPIDashboard` | Assembles summary_cards, time_series, agent_breakdown, business_kpis |

**Domain KPIs** (auto-selected by `ACTIVE_ADAPTER`):
- insurance: auto_approval_rate, fraud_detection_rate, avg_processing_time_hrs
- banking: query_resolution_rate, fraud_alerts_caught, avg_response_time
- manufacturing: defect_detection_rate, quality_score, downtime_reduction
- retail: recommendation_accuracy, cart_conversion, nps_score

---

### `modules/audit/`
```python
from modules.audit import AuditLogger
audit = AuditLogger()
event_id = audit.log(
    user_id="u1", event_type="chat",
    input_text="...", output_text="...",
    model_used="claude-sonnet-4-6", latency_ms=320,
    decision="auto_approved", pii_detected=False,
)
summary = audit.get_summary()
# {"total": 42, "auto_approved": 35, "escalated": 5, "blocked": 2, "pii_events": 3}
```

---

### `modules/memory/`
```python
from modules.memory import AgentMemoryManager
mem = AgentMemoryManager(anthropic_api_key=key, mem0_api_key=m0_key)
mem.add([{"role": "user", "content": "I filed claim CLM-001"}], user_id="u1")
context = mem.build_memory_context("claim status", user_id="u1")
# Returns formatted string injected into agent system prompt
```

---

### `modules/evaluation/`
```python
from modules.evaluation.rag_evaluator import RAGEvaluator
evaluator = RAGEvaluator()
scores = evaluator.evaluate_single(
    question="What is the deductible?",
    answer="The deductible is ₹5000",
    contexts=["Policy clause 3.1: Deductible is ₹5000 for...", "..."],
)
# {"faithfulness": 0.9, "answer_relevancy": 0.85, "context_precision": 0.8, "context_recall": 0.75}
```

---

### `modules/prompts/`
```python
from modules.prompts.library import PromptLibrary
lib = PromptLibrary()
system_prompt = lib.get_system_prompt("insurance_claims")
# Full prompt: role, responsibilities, format, compliance notes
```

Edit `modules/prompts/library.py` to customise system prompts for your domain.

---

### `modules/observability/`
LangSmith tracing — **zero code changes needed**, just set env vars:
```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__your-key
LANGCHAIN_PROJECT=tcs-hackathon-2025
```
All LangChain/LangGraph calls are traced automatically.

---

### `modules/model_router/`
```python
from modules.model_router import ModelRouter
router = ModelRouter()
model = router.route("What is 2+2?")       # → "claude-haiku-4-5"
model = router.route("Analyze fraud trends") # → "claude-sonnet-4-6"
```
Cost: Haiku 12× cheaper than Sonnet, 60× cheaper than Opus.

---

## Domain Adapter System

Adapters live in `adapters/<domain>/adapter.py`. The active adapter is set via:
```
ACTIVE_ADAPTER=insurance_claims   # in .env
```

Available: `insurance_claims | banking | manufacturing | retail`

**To create a new adapter** (copy and edit):
```python
# adapters/healthcare/adapter.py
from adapters.base import BaseAdapter

class HealthcareAdapter(BaseAdapter):
    domain_name = "Healthcare AI Assistant"
    system_prompt = """You are a healthcare AI assistant..."""
    kpi_definitions = {
        "diagnosis_accuracy": "% correct diagnostic suggestions",
        "patient_wait_reduction": "% reduction in wait times",
    }
    suggested_tools = ["data_query_tool", "calculator_tool"]
    sample_questions = [
        "What are the symptoms of Type 2 diabetes?",
        "Summarise patient record PRN-001",
    ]

    def get_config(self) -> dict:
        return {
            "domain": self.domain_name,
            "system_prompt": self.system_prompt,
            "sample_data": {},  # add synthetic patient records
            "context": "Healthcare domain...",
        }
```

Then set `ACTIVE_ADAPTER=healthcare` in `.env`.

---

## Environment Variables

Copy `.env.example` to `.env` and fill:

```
ANTHROPIC_API_KEY=sk-ant-...       # Required — Claude API
JWT_SECRET=change-this             # Required — JWT signing
ACTIVE_ADAPTER=insurance_claims    # Domain: insurance_claims|banking|manufacturing|retail
CHROMA_PATH=./data/chroma          # Vector DB path

# LangSmith tracing (optional but recommended for demo)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=tcs-hackathon-2025

# Mem0 persistent memory (optional)
MEM0_API_KEY=                      # leave empty for local mode
```

---

## FastAPI Routes (all prefixed `/api/v1`)

| Method | Path | Purpose |
|---|---|---|
| POST | `/auth/login` | `{"username","password"}` → `{"access_token","role"}` |
| POST | `/chat` | `{"message","user_id?"}` → response + metadata |
| POST | `/chat/stream` | SSE stream: token, tool_start, tool_end, done events |
| POST | `/rag/ingest` | multipart file upload → `{"chunks_added","filename"}` |
| POST | `/rag/query` | `{"query","top_k?"}` → `{"answer","context","sources"}` |
| POST | `/agents/run` | `{"task","agent_type?","user_id?"}` → response |
| GET | `/agents/list` | all agent types |
| POST | `/hitl/run` | `{"task","task_id?"}` → status + confidence |
| POST | `/hitl/{id}/approve` | resume pending HITL task |
| POST | `/hitl/{id}/reject` | reject pending HITL task |
| GET | `/kpi/dashboard?domain=` | full dashboard JSON |
| GET | `/kpi/metrics` | agent + model stats |
| GET | `/memory/{user_id}` | all stored memories |
| POST | `/memory/search` | `{"query","user_id"}` → context string |
| DELETE | `/memory/{user_id}` | clear user memories |
| GET | `/audit/logs?user_id=&event_type=` | paginated audit log |
| GET | `/audit/summary` | aggregated counts |
| POST | `/multimodal/analyze` | image/doc + task → Claude Vision result |
| POST | `/mcp/tools/list` | JSON-RPC: list tools |
| POST | `/mcp/tools/call` | JSON-RPC: invoke tool |
| GET | `/health` | `{"status":"ok","version","adapter"}` |

---

## Judging Criteria → Module Coverage

| # | Criterion | Primary Module(s) |
|---|---|---|
| 1 | Code Structure & Modularity | All modules (each independently importable) |
| 2 | Optimal AI Usage | `model_router`, `agents/orchestrator` |
| 3 | Enterprise AI KPIs | `kpi/`, `audit/` |
| 4 | Functional Testing | `tests/` in each module, RAGAS eval |
| 5 | Data Synthesis | `rag/ingestion`, domain adapter sample_data |
| 6 | Prompt Engineering | `prompts/library`, adapter system_prompt |
| 7 | RAG Types | `rag/hybrid` (vector + BM25 + RRF) |
| 8 | Agentic Tooling | `agents/tools`, `agents/orchestrator` |
| 9 | Multi-Agent | LangGraph supervisor in `orchestrator.py` |
| 10 | Model Optimization | `model_router` (Haiku/Sonnet/Opus cost routing) |
| 11 | HITL | `agents/hitl_graph` (interrupt_before + confidence gate) |
| 12 | Logs & Exceptions | `logging_obs/`, `audit/` |
| 13 | Agent KPI Dashboard | `kpi/dashboard`, frontend recharts |
| 14 | MCP Protocol | `mcp/server` (JSON-RPC 2.0) |
| 15 | RBAC | `rbac/` (JWT + roles + permissions) |
| 16 | Responsible AI | `guardrails/` (PII + injection + safety) |
| 17 | Feedback Loop | `evaluation/rag_evaluator`, LangSmith feedback |
| 18 | UI Frameworks | `frontend/` (React + Vite + Tailwind + recharts) |
| 19 | Multilingual | `multilingual/` (langdetect + translate + chat) |
| 20 | Voice Interface | `voice/` (Whisper + Web Speech API) |

---

## Code Conventions

- All module classes use lazy `__init__` — never import at module level if it could fail
- `_get_embeddings()` singleton pattern for HuggingFace models
- All public methods return plain dicts (not Pydantic models) for easy JSON serialisation
- Use `from __future__ import annotations` at the top of every file
- Optional heavy dependencies (ragas, deepeval) wrapped in `try/except ImportError`
- No bare `except:` — always catch specific exceptions
- Structlog for all logging: `logger.info("event_name", key=value, ...)`

---

## Running Tests

```bash
pytest modules/rag/tests/ -v
pytest modules/agents/tests/ -v
pytest modules/rbac/tests/ -v
pytest modules/guardrails/tests/ -v
pytest modules/evaluation/tests/ -v   # skips if deepeval not installed
pytest backend/tests/ -v
```

---

## Quick Start (2 minutes)

```bash
cp .env.example .env
# edit .env — set ANTHROPIC_API_KEY and ACTIVE_ADAPTER

pip install -r requirements.txt
uvicorn backend.main:app --reload          # API on :8000
cd frontend && npm install && npm run dev  # UI on :5173

# Verify:
curl http://localhost:8000/health
# POST http://localhost:8000/api/v1/auth/login  {"username":"admin","password":"admin123"}
```

---

## Files You Will Touch on Hackathon Day

| File | Why |
|---|---|
| `.env` | Set domain + API keys |
| `adapters/<domain>/adapter.py` | Domain system prompt + KPIs + sample data |
| `modules/prompts/library.py` | Customise LLM instructions |
| `modules/agents/tools.py` | Add domain-specific tools |
| `modules/kpi/metrics.py` | Add domain KPIs |
| `data/seeds/` | Ingest domain knowledge base documents |

## Files You Should NOT Touch

| File | Why |
|---|---|
| `modules/rag/ingestion.py` | Works; changing breaks tests |
| `modules/rbac/` | Auth fully wired |
| `backend/main.py` | Routers fully registered |
| `modules/audit/audit_logger.py` | SQLite schema is stable |
| `modules/agents/hitl_graph.py` | LangGraph wiring correct |
