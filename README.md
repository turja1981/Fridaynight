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

## Hackathon Day — Automated Use Case Bootstrap

When you receive the problem statement (Word doc / PDF), the platform can configure itself automatically:

### Step 1 — Paste the use case

Open `data/usecase.md` and replace the placeholder with the problem statement text (copy-paste from Word).

```
data/usecase.md   ← paste 500-1000 words here
```

### Step 2 — Run one command

```bash
python scripts/bootstrap_from_usecase.py
```

Claude reads the use case and **generates all required files automatically**:

| Generated file | What it contains |
|---|---|
| `adapters/<domain>/adapter.py` | System prompt, KPI definitions, 5 synthetic sample records, 8-10 sample questions |
| `data/seeds/<domain>/sample_faq.txt` | 400-word domain FAQ for RAG knowledge base |
| `modules/kpi/metrics.py` | New domain KPI entry added automatically |
| `.env` | `ACTIVE_ADAPTER` updated to the new domain |

The script also ingests the FAQ into Qdrant so RAG returns real results immediately.

### Step 3 — Review and verify

```bash
# Check generated adapter
cat adapters/<domain>/adapter.py

# Run all tests
pytest modules/ backend/ -v --tb=short

# Start server and test a question
uvicorn backend.main:app --reload
curl -s -X POST http://localhost:8000/api/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "What is the status of record DOMAIN-2024-001?"}' | python -m json.tool
```

### Options

```bash
# Preview what will be generated without writing files
python scripts/bootstrap_from_usecase.py --dry-run

# Use a different input file
python scripts/bootstrap_from_usecase.py --usecase path/to/problem.md
```

> **Total time from Word doc to running demo: under 15 minutes.**

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

The adapter is the only file you need to touch to re-purpose this platform for any use case. Swapping adapters is a single env-var change — no framework code is modified.

### Built-in adapters

| `ACTIVE_ADAPTER` | Domain | Primary KPIs |
|---|---|---|
| `insurance_claims` | Insurance Claims Processing | auto_approval_rate, fraud_detection_rate, avg_processing_time_hrs |
| `banking` | Banking Customer Service | query_resolution_rate, fraud_alerts_caught, avg_response_time |
| `manufacturing` | Manufacturing Quality Control | defect_detection_rate, quality_score, downtime_reduction |
| `retail` | Retail & E-Commerce | recommendation_accuracy, cart_conversion, nps_score |

Set the active adapter in `.env`:

```bash
ACTIVE_ADAPTER=insurance_claims
```

---

### Configuring a New Adapter (Step-by-Step)

#### Step 1 — Create the adapter file

```bash
mkdir -p adapters/<your_domain>
touch adapters/<your_domain>/__init__.py
```

#### Step 2 — Write the adapter class

```python
# adapters/healthcare/adapter.py
from __future__ import annotations
from adapters.base import BaseAdapter

SAMPLE_RECORDS = [
    {
        "patient_id": "PRN-2024-001",
        "name": "Meera Iyer",
        "age": 45,
        "diagnosis": "Type 2 Diabetes",
        "risk_score": "Medium",
    },
]

class HealthcareAdapter(BaseAdapter):
    domain_name = "Healthcare Patient Management"

    system_prompt = """You are a clinical AI assistant for TCS HealthAI Platform.

Responsibilities:
- Retrieve and summarise patient records
- Flag high-risk patients needing urgent follow-up
- Answer clinical protocol questions

You must NEVER prescribe medications or make a definitive diagnosis.

Response format:
  Patient Summary: <2-sentence overview>
  Risk Level: Low / Medium / High
  Recommended Action: <next step>
  Confidence: <percentage>

Regulatory framework: DISHA, ABDM data standards."""

    kpi_definitions = {
        "diagnosis_accuracy":       "% AI-suggested diagnoses confirmed by physician",
        "high_risk_recall":         "% high-risk patients flagged before deterioration",
        "avg_summary_time_sec":     "Seconds to generate a discharge summary",
        "patient_wait_reduction":   "% reduction in outpatient wait time",
        "medication_error_reduction": "% drop in medication errors after AI reconciliation",
    }

    suggested_tools = ["data_query", "calculator", "datetime_tool", "web_search"]

    sample_questions = [
        "Show summary for patient PRN-2024-001",
        "Which patients are high-risk and due for follow-up this week?",
        "What is the hospital protocol for CKD Stage 2 management?",
        "मेरे मरीज़ PRN-2024-001 की रिपोर्ट दिखाओ",   # Hindi demo
    ]

    def get_config(self) -> dict:
        return {
            "domain": self.domain_name,
            "system_prompt": self.system_prompt,
            "sample_data": {r["patient_id"]: r for r in SAMPLE_RECORDS},
            "context": "\n".join(
                f"Patient {r['patient_id']}: {r['name']}, {r['age']}y, risk={r['risk_score']}"
                for r in SAMPLE_RECORDS
            ),
        }
```

#### Step 3 — Activate it

```bash
# .env
ACTIVE_ADAPTER=healthcare
```

#### Step 4 — Add domain KPIs to the metrics module

```python
# modules/kpi/metrics.py — inside MetricsCollector.get_domain_kpis()
elif domain == "healthcare":
    kpis["diagnosis_accuracy"]         = round(random.uniform(0.88, 0.96), 3)
    kpis["high_risk_recall"]           = round(random.uniform(0.82, 0.94), 3)
    kpis["avg_summary_time_sec"]       = round(random.uniform(4.0, 8.5), 1)
    kpis["patient_wait_reduction"]     = round(random.uniform(0.25, 0.45), 3)
    kpis["medication_error_reduction"] = round(random.uniform(0.30, 0.55), 3)
```

#### Step 5 — Seed the RAG knowledge base

Create `data/seeds/healthcare/sample_faq.txt` with 300–500 words of domain FAQ (policy rules, procedures, KPI definitions), then ingest:

```bash
python scripts/ingest_all_seeds.py
```

#### Step 6 — Register the adapter (dynamic loading)

```python
# backend/adapters_registry.py
ADAPTER_MAP = {
    ...
    "healthcare": "adapters.healthcare.adapter.HealthcareAdapter",
}
```

#### Step 7 — Verify

```bash
python -c "
from adapters.healthcare.adapter import HealthcareAdapter
a = HealthcareAdapter()
cfg = a.get_config()
print('Domain:', cfg['domain'])
print('Records:', len(cfg['sample_data']))
print('KPIs:', list(a.kpi_definitions.keys()))
"
```

### Adapter Checklist

```
[ ] adapters/<domain>/__init__.py created
[ ] adapters/<domain>/adapter.py created with domain_name, system_prompt, kpi_definitions
[ ] sample_data has 5–10 realistic synthetic records (Indian names, ₹ amounts, local IDs)
[ ] sample_questions has 8–10 queries covering all agent types (include one in Hindi)
[ ] get_config() returns: domain, system_prompt, sample_data (dict), context (str)
[ ] ACTIVE_ADAPTER=<domain> set in .env
[ ] KPI branch added to modules/kpi/metrics.py
[ ] data/seeds/<domain>/sample_faq.txt created and ingested
[ ] pytest passes — all green
```

See [ADAPTER_GUIDE.md](ADAPTER_GUIDE.md) for the complete reference including domain-specific tools.

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
