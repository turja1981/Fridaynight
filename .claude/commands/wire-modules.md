Wire the required modules together for the hackathon use case.

$ARGUMENTS

If arguments are provided, treat them as additional requirements.
Otherwise, read `HACKATHON_PLAN.md` for the full requirements list.

## Your Task

### Step 1 — Read Requirements

Read `HACKATHON_PLAN.md`. Extract:
- Which modules are marked REQUIRED
- What custom tools are needed
- What domain KPIs are listed
- Whether HITL, multimodal, multilingual, or voice are needed

### Step 2 — Wire the Agent Tool Registry

Read `modules/agents/tools.py` fully. Then add any domain-specific tools the use case needs.

Common patterns:
```python
# Domain data lookup tool
elif tool_name == "domain_lookup":
    key = tool_input.get("key", "")
    # Load from adapter sample_data or a local JSON file
    from adapters.<domain>.adapter import <Domain>Adapter
    data = <Domain>Adapter().get_config()["sample_data"]
    return str(data.get(key, "No record found for: " + key))
```

Add the tool schema to `get_all_tools()` and the execution to `execute()`.

### Step 3 — Configure Agent Routing

Read `modules/agents/orchestrator.py`. Update the routing keywords if needed:
- If the use case has a domain-specific primary workflow (e.g., "approve", "reject", "escalate",
  "inspect", "diagnose"), add those keywords to the appropriate agent bucket.
- If a new agent type is needed, add it to `self._agents` dict in `__init__`.

### Step 4 — Set HITL Confidence Threshold

Read `modules/agents/hitl_graph.py`. Adjust `_compute_confidence()` if the use case needs:
- Lower threshold for high-stakes decisions (medical, legal, fraud > ₹100k): set approve threshold to 0.90
- Standard threshold (claims < ₹50k, routine queries): keep at 0.85
- Add domain keywords to the confidence scorer:
  ```python
  # High-stakes keywords that lower confidence (force human review):
  high_stakes = ["fraud", "suspicious", "criminal", "reject", "terminate", "legal"]
  ```

### Step 5 — Add Domain KPI Metrics

Read `modules/kpi/metrics.py`. Add domain-specific KPI computation:
```python
elif domain == "<domain>":
    kpis["<kpi_name>"] = round(random.uniform(0.80, 0.95), 3)
    # Replace random with real computation based on tracker data
```

Map the KPIs from `HACKATHON_PLAN.md` to actual formulas where possible.

### Step 6 — Configure RAG for Domain

If domain documents exist in `data/seeds/<domain>/`:
```python
# Create a one-time ingestion script at scripts/ingest_<domain>.py
from modules.rag.ingestion import DocumentIngester

ingester = DocumentIngester(collection_name="<domain>_docs")
with open("data/seeds/<domain>/sample_faq.txt") as f:
    ingester.ingest_text(f.read(), source_name="domain_faq")
print("Ingestion complete")
```

Also update the RAG route collection_name if the use case requires domain-isolated collections.

### Step 7 — Wire Multimodal (if required)

If the use case needs image analysis (damage photos, document scans, defect images):
Read `modules/multimodal/processor.py`. Verify the `analyze()` method handles the
file types in the use case. Add domain-specific task prompts:
```python
DOMAIN_TASKS = {
    "damage_assessment": "Assess the damage in this image. Rate severity 1-10. List affected parts.",
    "document_verification": "Verify this document. Check for completeness and authenticity markers.",
    "defect_detection": "Identify manufacturing defects. Classify defect type and severity.",
}
```

### Step 8 — Wire Multilingual (if required)

If the use case mentions regional languages (Hindi, Tamil, Telugu, Marathi, etc.):
Read `modules/multilingual/language.py`. The `LanguageDetector` and `Translator` are 
pre-built. Verify the chat route already calls `language_detection` (it does, in chat.py).
Add the target languages to the translator config if needed.

### Step 9 — Run a Smoke Test

```bash
python -c "
from modules.agents.orchestrator import AgentOrchestrator
orch = AgentOrchestrator()
print('Agents:', [a['name'] for a in orch.list_agents()])
print('Routing test:', orch.route('check claim status'))
"
```

Also run:
```bash
python -c "
from modules.rag.hybrid import HybridRetriever
r = HybridRetriever()
print('RAG vectorstore initialised OK')
"
```

### Step 10 — Report

List every file changed and what was changed. Confirm:
- Tools registry updated: ✓/✗
- Agent routing correct: ✓/✗
- HITL threshold set: ✓/✗
- KPI metrics added: ✓/✗
- RAG ingestion script ready: ✓/✗
- Smoke tests pass: ✓/✗

Next command: `/prep-demo`
