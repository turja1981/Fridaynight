Bootstrap the domain adapter for the hackathon. The domain is: $ARGUMENTS

If $ARGUMENTS is empty, read `HACKATHON_PLAN.md` to determine the domain.

## Your Task

Do ALL of the following in order:

### Step 1 — Read Current State

- Read `HACKATHON_PLAN.md` (if it exists) for domain and requirements
- Read `.env.example` to understand all available env vars
- Read `adapters/<domain>/adapter.py` for the selected domain (or the closest match)
- Read `modules/prompts/library.py` to see current system prompts

### Step 2 — Configure .env

Check if `.env` exists. If not, copy from `.env.example`.
Update `.env` with:
- `ACTIVE_ADAPTER=<domain>`  (e.g., `insurance_claims`)
- Keep `ANTHROPIC_API_KEY` placeholder if not set
- Set `LANGCHAIN_PROJECT=tcs-hackathon-<domain>-2025`

### Step 3 — Update the Domain Adapter

Edit `adapters/<domain>/adapter.py`:

1. **system_prompt**: Rewrite to match the exact use case from `HACKATHON_PLAN.md`. Include:
   - The AI's role (who it is, what organisation it serves)
   - Primary responsibilities (3–5 bullet points)
   - What it must NEVER do (compliance guardrails)
   - Required response format (e.g., "Always include: Assessment, Recommendation, Confidence Score")
   - Any regulatory framework to follow (IRDAI / RBI / ISO / GDPR)

2. **kpi_definitions**: Update to match the domain KPIs from `HACKATHON_PLAN.md`

3. **sample_questions**: Replace with 8–10 realistic questions from the actual use case

4. **get_config() → sample_data**: Add 5–10 realistic synthetic data records.
   Use realistic Indian names (Rahul Sharma, Priya Patel), Indian amounts (₹ not $),
   and domain-appropriate IDs (CLM-2024-001, ACC-789, MFG-BATCH-42, etc.)

### Step 4 — Update Prompt Library

Edit `modules/prompts/library.py`:
- Add or update the entry for `<domain>` in `get_system_prompt()`
- The prompt should be detailed (150–300 words), covering:
  - Role statement
  - Core tasks
  - Response format instruction
  - Compliance/safety note

### Step 5 — Create Seed Data Directory

```
mkdir -p data/seeds/<domain>
```

Create `data/seeds/<domain>/README.md` listing what documents should be ingested
(policy documents, manuals, regulatory guidelines, product catalogues, etc.).
Also create `data/seeds/<domain>/sample_faq.txt` with 10 Q&A pairs in the domain
that can be immediately ingested into the RAG pipeline.

### Step 6 — Verify Configuration

Run these checks and report results:
```bash
python -c "from backend.config import settings; print('ACTIVE_ADAPTER:', settings.active_adapter)"
python -c "from modules.prompts.library import PromptLibrary; p = PromptLibrary(); print(p.get_system_prompt('<domain>')[:100])"
```

### Step 7 — Report

Print a summary:
- ✓ or ✗ for each step
- The first 3 lines of the new system prompt
- The list of KPIs now configured
- The sample questions added
- Next command to run: `/wire-modules`
