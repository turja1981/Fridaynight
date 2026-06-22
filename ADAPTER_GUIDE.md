# Adapter Pattern Guide — Plugging Any Use Case into the Enterprise AI Platform

This guide explains how the adapter pattern works in this platform and walks you through
creating a new domain adapter from scratch so you can plug in any business use case
without touching the core framework code.

---

## Why an Adapter Pattern?

The platform core (RAG pipeline, agents, guardrails, RBAC, audit, KPI) is domain-agnostic.
An adapter is a thin configuration layer that tells the platform:

- **Who the AI is** — its role, responsibilities, tone, compliance rules (the system prompt)
- **What it knows** — domain-specific KPI names and formulas
- **What data it works with** — synthetic sample records for demos and tool lookups
- **What questions it answers** — representative sample queries

Swapping adapters is a single env-var change. No framework code is modified.

```
┌─────────────────────────────────────────────┐
│              Your Use Case                   │
│  adapters/<domain>/adapter.py               │
│  • system_prompt                             │
│  • kpi_definitions                           │
│  • sample_data                               │
│  • sample_questions                          │
└────────────────┬────────────────────────────┘
                 │  ACTIVE_ADAPTER=<domain>
                 ▼
┌─────────────────────────────────────────────┐
│           Platform Core (unchanged)          │
│  RAG · Agents · Guardrails · RBAC · Audit   │
└─────────────────────────────────────────────┘
```

---

## Directory Structure

```
adapters/
├── base.py                         # BaseAdapter — the contract every adapter must fulfil
├── insurance_claims/
│   ├── __init__.py
│   └── adapter.py                  # InsuranceClaimsAdapter
├── banking/
│   ├── __init__.py
│   └── adapter.py                  # BankingAdapter
├── manufacturing/
│   ├── __init__.py
│   └── adapter.py                  # ManufacturingAdapter
├── retail/
│   ├── __init__.py
│   └── adapter.py                  # RetailAdapter
└── <your_domain>/                  # ← you create this
    ├── __init__.py
    └── adapter.py
```

---

## The Base Contract

Every adapter inherits from `BaseAdapter`:

```python
# adapters/base.py
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

@dataclass
class BaseAdapter(ABC):
    domain_name: str = ""
    system_prompt: str = ""
    kpi_definitions: dict[str, str] = field(default_factory=dict)
    suggested_tools: list[str] = field(default_factory=list)
    sample_questions: list[str] = field(default_factory=list)

    @abstractmethod
    def get_config(self) -> dict: ...         # must return domain, sample_data, context

    def get_sample_context(self) -> str:
        return f"Domain: {self.domain_name}"  # override for richer context
```

You must implement `get_config()`. Everything else is filled in by setting class attributes.

---

## Step-by-Step: Create a New Adapter

### Step 1 — Create the directory

```bash
mkdir -p adapters/<your_domain>
touch adapters/<your_domain>/__init__.py
```

Example: `adapters/healthcare/`

---

### Step 2 — Write the adapter class

```python
# adapters/healthcare/adapter.py
from __future__ import annotations
from adapters.base import BaseAdapter

# Synthetic domain data — used by data_query tool and RAG ingestion
SAMPLE_PATIENTS = [
    {
        "patient_id": "PRN-2024-001",
        "name": "Meera Iyer",
        "age": 45,
        "diagnosis": "Type 2 Diabetes",
        "last_visit": "2024-06-10",
        "medications": ["Metformin 500mg", "Glipizide 5mg"],
        "next_appointment": "2024-07-15",
        "risk_score": "Medium",
    },
    {
        "patient_id": "PRN-2024-002",
        "name": "Suresh Nair",
        "age": 62,
        "diagnosis": "Hypertension + CKD Stage 2",
        "last_visit": "2024-06-12",
        "medications": ["Amlodipine 5mg", "Telmisartan 40mg"],
        "next_appointment": "2024-06-25",
        "risk_score": "High",
    },
]


class HealthcareAdapter(BaseAdapter):
    # ── 1. Identity ────────────────────────────────────────────────────────
    domain_name = "Healthcare Patient Management"

    # ── 2. System Prompt ───────────────────────────────────────────────────
    # Write 150–300 words. Cover: role, tasks, format, compliance.
    system_prompt = """You are a clinical AI assistant for TCS HealthAI Platform,
supporting doctors and care coordinators at a multi-specialty hospital network.

Responsibilities:
- Retrieve and summarise patient records (vitals, medications, diagnosis history)
- Flag high-risk patients who need urgent follow-up
- Answer clinical protocol questions using the hospital knowledge base
- Generate discharge summaries and referral notes in structured format
- Support medication reconciliation and drug interaction checks

You must NEVER:
- Prescribe medications or change dosage without doctor confirmation
- Share patient records with unauthorised roles (RBAC enforced)
- Make a definitive diagnosis — always say "recommend consultation"

Response format:
  Patient Summary: <2-sentence overview>
  Key Findings: <bullet points>
  Risk Level: Low / Medium / High
  Recommended Action: <specific next step>
  Confidence: <percentage>

Regulatory framework: DISHA (Digital Information Security in Healthcare Act),
ABDM (Ayushman Bharat Digital Mission) data standards."""

    # ── 3. KPIs ────────────────────────────────────────────────────────────
    # Match the metrics your stakeholders care about.
    kpi_definitions = {
        "diagnosis_accuracy": "% AI-suggested diagnoses confirmed by physician",
        "high_risk_recall": "% high-risk patients correctly flagged before deterioration",
        "avg_summary_time_sec": "Seconds to generate a discharge summary vs manual baseline",
        "patient_wait_reduction": "% reduction in average outpatient wait time",
        "medication_error_reduction": "% drop in medication errors after AI reconciliation",
    }

    # ── 4. Tools the agents should prefer ─────────────────────────────────
    suggested_tools = ["data_query", "calculator", "datetime_tool", "web_search"]

    # ── 5. Sample questions for the UI and demo ────────────────────────────
    sample_questions = [
        "Show me the summary for patient PRN-2024-001",
        "Which patients are high-risk and due for follow-up this week?",
        "Check drug interactions between Metformin and Glipizide",
        "Generate a discharge note for PRN-2024-002",
        "What is the hospital protocol for CKD Stage 2 management?",
        "Calculate eGFR for a 62-year-old male with creatinine 1.8 mg/dL",
        "मेरे मरीज़ PRN-2024-001 की रिपोर्ट दिखाओ",  # Hindi — multilingual demo
    ]

    # ── 6. Config returned to the platform ────────────────────────────────
    def get_config(self) -> dict:
        return {
            "domain": self.domain_name,
            "system_prompt": self.system_prompt,
            # sample_data is keyed so the data_query tool can look up by ID
            "sample_data": {p["patient_id"]: p for p in SAMPLE_PATIENTS},
            # context is injected into the RAG pipeline as background knowledge
            "context": "\n".join(
                f"Patient {p['patient_id']}: {p['name']}, {p['age']}y, "
                f"{p['diagnosis']}, risk={p['risk_score']}"
                for p in SAMPLE_PATIENTS
            ),
        }
```

---

### Step 3 — Activate the adapter

Set one environment variable in `.env`:

```bash
ACTIVE_ADAPTER=healthcare
```

No code changes required anywhere else.

---

### Step 4 — Register the adapter in the loader (if using dynamic loading)

The platform loads adapters by name convention. If you add a new domain, register it in
the adapter factory so the backend can resolve it:

```python
# backend/adapters_registry.py  (or wherever your loader lives)
ADAPTER_MAP = {
    "insurance_claims": "adapters.insurance_claims.adapter.InsuranceClaimsAdapter",
    "banking":          "adapters.banking.adapter.BankingAdapter",
    "manufacturing":    "adapters.manufacturing.adapter.ManufacturingAdapter",
    "retail":           "adapters.retail.adapter.RetailAdapter",
    "healthcare":       "adapters.healthcare.adapter.HealthcareAdapter",   # ← add this
}
```

---

### Step 5 — Add domain KPIs to the metrics module

```python
# modules/kpi/metrics.py  — inside MetricsCollector.get_domain_kpis()
elif domain == "healthcare":
    kpis["diagnosis_accuracy"]      = round(random.uniform(0.88, 0.96), 3)
    kpis["high_risk_recall"]        = round(random.uniform(0.82, 0.94), 3)
    kpis["avg_summary_time_sec"]    = round(random.uniform(4.0, 8.5), 1)
    kpis["patient_wait_reduction"]  = round(random.uniform(0.25, 0.45), 3)
    kpis["medication_error_reduction"] = round(random.uniform(0.30, 0.55), 3)
```

Replace `random.uniform` with real computation once you have actual audit log data.

---

### Step 6 — Seed the RAG knowledge base

```python
# scripts/ingest_healthcare.py
import sys
sys.path.insert(0, ".")

from modules.rag.ingestion import DocumentIngester

ingester = DocumentIngester(collection_name="healthcare_docs")

# Ingest FAQ / protocol documents
with open("data/seeds/healthcare/sample_faq.txt") as f:
    ids = ingester.ingest_text(f.read(), source_name="clinical_protocols")

print(f"Ingested {len(ids)} chunks into healthcare_docs collection")
```

Run once before your demo:

```bash
python scripts/ingest_healthcare.py
```

---

### Step 7 — Add domain-specific tools (optional)

For lookups against your synthetic data, add a branch in `modules/agents/tools.py`:

```python
# Inside ToolRegistry.execute()
if tool_name == "patient_lookup":
    patient_id = tool_input.get("patient_id", "")
    from adapters.healthcare.adapter import HealthcareAdapter
    data = HealthcareAdapter().get_config()["sample_data"]
    result = data.get(patient_id)
    return str(result) if result else f"No patient found: {patient_id}"
```

And add the schema to `ToolRegistry._TOOL_DEFS`:

```python
{
    "name": "patient_lookup",
    "description": "Look up a patient record by ID (e.g. PRN-2024-001).",
    "input_schema": {
        "type": "object",
        "properties": {
            "patient_id": {"type": "string", "description": "Patient record number"},
        },
        "required": ["patient_id"],
    },
},
```

---

## Existing Adapters at a Glance

| Adapter | `ACTIVE_ADAPTER` value | Primary KPIs | Suggested tools |
|---|---|---|---|
| Insurance Claims | `insurance_claims` | auto_approval_rate, fraud_detection_rate, avg_processing_time_hrs | data_query, calculator, document_lookup |
| Banking | `banking` | query_resolution_rate, fraud_alerts_caught, avg_response_time | data_query, datetime_tool |
| Manufacturing | `manufacturing` | defect_detection_rate, quality_score, downtime_reduction | data_query, calculator |
| Retail | `retail` | recommendation_accuracy, cart_conversion, nps_score | data_query, web_search |

---

## Adapter Checklist

```
[ ] adapters/<domain>/__init__.py created
[ ] adapters/<domain>/adapter.py created
[ ] domain_name set (shown in UI header and health endpoint)
[ ] system_prompt written: role + tasks + NEVER rules + response format + compliance
[ ] kpi_definitions matches the business metrics in HACKATHON_PLAN.md
[ ] sample_data has 5–10 realistic synthetic records (Indian names, ₹ amounts, local IDs)
[ ] sample_questions has 8–10 representative queries covering all agent types
[ ] get_config() returns: domain, system_prompt, sample_data (dict), context (str)
[ ] ACTIVE_ADAPTER=<domain> set in .env
[ ] KPI branch added to modules/kpi/metrics.py
[ ] data/seeds/<domain>/sample_faq.txt created and ingested
[ ] Domain-specific tools added to ToolRegistry (if needed)
```

---

## Verifying Your Adapter

```bash
# Confirm the platform loaded your adapter
python -c "
from backend.config import settings
print('Active adapter:', settings.active_adapter)
"

# Confirm the system prompt is correct
python -c "
from modules.prompts.library import PromptLibrary
lib = PromptLibrary()
print(lib.get_system_prompt('healthcare')[:200])
"

# Quick smoke test
python -c "
from adapters.healthcare.adapter import HealthcareAdapter
a = HealthcareAdapter()
cfg = a.get_config()
print('Domain:', cfg['domain'])
print('Records:', len(cfg['sample_data']))
print('KPIs:', list(a.kpi_definitions.keys()))
"
```

Expected output:
```
Active adapter: healthcare
Domain: Healthcare Patient Management
Records: 2
KPIs: ['diagnosis_accuracy', 'high_risk_recall', 'avg_summary_time_sec', ...]
```

---

## Design Principles

**Only the adapter changes, never the framework.**
The RAG pipeline, guardrails, RBAC, audit log, and HITL graph are domain-agnostic.
If you find yourself editing `backend/main.py` or `modules/agents/orchestrator.py` to
add domain logic, that logic belongs in the adapter or in a domain-specific tool, not the core.

**System prompts are the primary lever for AI behaviour.**
A well-written system prompt (role, boundaries, format, compliance) will outperform
adding custom code in most cases. Write the prompt first; add code only when the prompt
is insufficient.

**Sample data must be realistic.**
The demo lives or dies on data quality. Use realistic Indian names, ₹ amounts, proper
domain IDs (CLM-2024-001, PRN-2024-002, BATCH-MFG-42), and plausible values.
Evaluators notice when sample data is lorem ipsum.

**One collection per domain in ChromaDB.**
Pass `collection_name="<domain>_docs"` to `DocumentIngester` and `HybridRetriever`
so domains don't share vector space and retrieve each other's documents.
