Analyze the following hackathon problem statement and produce a complete, actionable implementation plan. The problem statement is:

$ARGUMENTS

## Your Task

Read the problem statement carefully, then do ALL of the following steps in order:

### Step 1 — Extract Key Facts

Identify and state clearly:
- **Domain**: Which of these fits best? `insurance_claims | banking | manufacturing | retail | healthcare | other`
- **Primary User**: Who uses this system? (claims officer, customer, factory manager, etc.)
- **Core Workflow**: The main 3–5 step process the AI must support
- **Key Entities**: The data objects (claims, policies, accounts, products, defects, etc.)
- **Pain Points**: What manual/slow/error-prone task is being automated?
- **Compliance Requirements**: Any regulations mentioned (IRDAI, RBI, ISO, GDPR, etc.)
- **Volume/Scale Hints**: Any numbers (transactions per day, documents, response time SLAs)

### Step 2 — Map to Technical Competencies

Go through ALL 20 technical competencies. For each one, state whether it is REQUIRED, NICE-TO-HAVE, or NOT-APPLICABLE for this use case, and why in one sentence.

T01 Data Synthesis (RAG ingestion) | T02 Prompt Engineering | T03 RAG Types (hybrid search)
T04 Agentic Tooling | T05 Model Optimization (cost routing) | T06 Multi-Agent Orchestration
T07 MCP Protocol | T08 RBAC | T09 Streaming | T10 HITL
T11 Logs & Exceptions | T12 Agent KPI Dashboard | T13 UI Frameworks
T14 MCP Protocol (server) | T15 RBAC Enforcement | T16 Guardrails & PII
T17 Multilingual | T18 Multimodal | T19 Small Language Models | T20 Voice Interface

### Step 3 — Select Modules

Based on the use case, list which pre-built modules to ACTIVATE (all exist already):
- Which domain adapter: `adapters/<domain>/adapter.py`
- Whether to ingest documents: yes/no, what type (PDF policies, manuals, contracts)
- Which agent tools are needed: calculator, data_query, web_search, datetime, or custom
- Whether HITL is needed and what confidence threshold makes sense for this domain
- Whether multimodal is needed (document images, photos)
- Whether multilingual is needed and which languages
- Whether voice input matters for the demo

### Step 4 — Identify What Must Be Custom-Built

List the exact code changes needed (be specific about file paths):
1. What to change in `adapters/<domain>/adapter.py` (system prompt, KPIs, sample data)
2. What to add to `modules/prompts/library.py` (domain prompt text)
3. What to add to `modules/agents/tools.py` (any domain-specific tool)
4. What to add to `modules/kpi/metrics.py` (domain-specific KPI formulas)
5. What sample data/documents to create in `data/seeds/`

### Step 5 — Demo Storyboard

Design the 5-minute demo story that hits the maximum judging criteria:
1. Show login (RBAC)
2. Show a key user workflow end-to-end (RAG + Agent + HITL if applicable)
3. Show the KPI dashboard updating in real-time
4. Show guardrails blocking a bad input or redacting PII
5. Show audit log for compliance
6. Show streaming chat (if time)

### Step 6 — Write HACKATHON_PLAN.md

Create the file `HACKATHON_PLAN.md` in the project root with:
- Summary of the use case (2 sentences)
- Selected domain adapter
- Modules to activate (checklist)
- Custom code needed (file + what to change)
- Sample questions for demo (at least 8)
- Demo script (step-by-step, ~5 minutes)
- Judging criteria coverage map

### Step 7 — Tell the User What to Run Next

End with:
```
Next steps:
1. Run: /bootstrap-domain <domain_name>
2. Run: /wire-modules
3. Run: /prep-demo
```
