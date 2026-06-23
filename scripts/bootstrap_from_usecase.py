#!/usr/bin/env python3
"""
bootstrap_from_usecase.py
=========================
Reads data/usecase.md, calls Claude to extract domain configuration,
then generates ALL required files automatically:

  adapters/<domain>/__init__.py
  adapters/<domain>/adapter.py
  data/seeds/<domain>/sample_faq.txt
  modules/kpi/metrics.py          (patched — new domain entry added)
  .env                             (ACTIVE_ADAPTER updated)

Then seeds the Qdrant RAG collection so the demo returns real results.

Usage:
    python scripts/bootstrap_from_usecase.py
    python scripts/bootstrap_from_usecase.py --usecase path/to/doc.md
    python scripts/bootstrap_from_usecase.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

# ── Extraction prompt ──────────────────────────────────────────────────────────

EXTRACTION_PROMPT = """\
You are an expert at configuring Enterprise AI Platforms for hackathon use cases.

Given the following use case description, extract all required configuration.
Return ONLY a single valid JSON object — no markdown fences, no explanation.

USE CASE DESCRIPTION:
{use_case}

Return this exact JSON structure (fill every field completely):

{{
  "domain_key": "snake_case identifier, 1-3 words (e.g. insurance_claims, healthcare, supply_chain)",
  "domain_name": "Human-readable name shown in the UI (e.g. Healthcare Patient Management)",
  "class_name": "PascalCase Python class name (e.g. HealthcareAdapter)",

  "system_prompt": "Complete system prompt, 150-300 words. Must cover:\\n- AI role and platform name\\n- 4-6 specific responsibilities\\n- 2-3 explicit NEVER rules\\n- Response format with labelled fields (e.g. Assessment: / Decision: / Confidence:)\\n- Applicable Indian regulatory framework (IRDAI, RBI, BIS, SEBI, MoHFW, ABDM, etc.)",

  "kpi_definitions": {{
    "kpi_snake_case": "Plain English: what this KPI measures",
    "...": "5-7 KPIs that directly reflect the business outcomes in the use case"
  }},

  "kpi_values": {{
    "kpi_snake_case": "Realistic static value string, e.g. '94.2%' or '2.3' or '72'",
    "...": "Same keys as kpi_definitions"
  }},

  "sample_data": [
    {{
      "id": "DOMAIN-2024-001",
      "name": "Indian full name",
      "field_3": "domain-specific field with realistic Indian value",
      "field_4": "₹ amounts where monetary, Indian city names, local IDs",
      "field_5": "...",
      "field_6": "...",
      "status": "realistic status value"
    }},
    {{ "id": "DOMAIN-2024-002", "name": "Second Indian name", "...": "..." }},
    {{ "id": "DOMAIN-2024-003", "name": "Third Indian name",  "...": "..." }},
    {{ "id": "DOMAIN-2024-004", "name": "Fourth Indian name", "...": "..." }},
    {{ "id": "DOMAIN-2024-005", "name": "Fifth Indian name",  "...": "..." }}
  ],

  "sample_questions": [
    "Question covering record lookup by ID",
    "Question covering status or summary",
    "Question covering analysis or calculation",
    "Question covering trend or comparison",
    "Question covering compliance or policy",
    "Question covering a specific record detail",
    "Question covering risk or flag detection",
    "Question in Hindi script (mandatory)"
  ],

  "faq_content": "400-500 word FAQ document. Write as realistic domain knowledge. Cover: how the AI works, key business rules and policies, example KPI thresholds, compliance notes, 5-6 common Q&A pairs. Use Indian context throughout: ₹ amounts, Indian regulations, Indian city/company examples. This will be the RAG knowledge base for the demo.",

  "suggested_tools": ["list only tools needed from: calculator", "data_query", "datetime_tool", "web_search"]
}}"""

# ── File templates ─────────────────────────────────────────────────────────────

ADAPTER_TEMPLATE = '''from __future__ import annotations
from adapters.base import BaseAdapter

SAMPLE_DATA = {sample_data_json}


class {class_name}(BaseAdapter):
    domain_name = {domain_name_repr}

    system_prompt = {system_prompt_repr}

    kpi_definitions = {kpi_definitions_json}

    suggested_tools = {suggested_tools_repr}

    sample_questions = {sample_questions_json}

    def get_config(self) -> dict:
        return {{
            "domain": self.domain_name,
            "system_prompt": self.system_prompt,
            "sample_data": {{r["id"]: r for r in SAMPLE_DATA}},
            "context": "\\n".join(
                f"{{r['id']}}: {{r.get('name', '')}} | "
                + ", ".join(f"{{k}}={{v}}" for k, v in r.items() if k not in ("id", "name"))
                for r in SAMPLE_DATA
            ),
        }}
'''


# ── Core helpers ───────────────────────────────────────────────────────────────

def read_usecase(path: Path) -> str:
    if not path.exists():
        sys.exit(
            f"\nERROR: Use case file not found: {path}\n"
            "  1. Create the file:  data/usecase.md\n"
            "  2. Paste the hackathon problem statement into it\n"
            "  3. Re-run this script\n"
        )
    text = path.read_text(encoding="utf-8").strip()
    if "[PASTE USE CASE TEXT HERE]" in text:
        sys.exit(
            "\nERROR: data/usecase.md still contains the placeholder.\n"
            "Open the file, delete the instructions, and paste the hackathon\n"
            "problem statement text, then re-run this script.\n"
        )
    if len(text) < 150:
        sys.exit(
            f"\nERROR: Use case file is too short ({len(text)} chars).\n"
            "Paste the full problem statement (300+ words recommended).\n"
        )
    return text


def call_claude(use_case_text: str, api_key: str) -> dict:
    try:
        import anthropic
    except ImportError:
        sys.exit("ERROR: anthropic package not installed. Run: pip install anthropic")

    client = anthropic.Anthropic(api_key=api_key)
    print("  Calling Claude to extract domain configuration...")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": EXTRACTION_PROMPT.format(use_case=use_case_text)}],
    )
    raw = response.content[0].text.strip()

    # Strip markdown fences if the model wrapped the JSON
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\s*```\s*$", "", raw, flags=re.MULTILINE)
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.exit(
            f"\nERROR: Claude returned invalid JSON ({exc})\n"
            f"Raw output (first 600 chars):\n{raw[:600]}\n"
        )


# ── File writers ───────────────────────────────────────────────────────────────

def write_adapter(config: dict, dry_run: bool) -> None:
    domain_key = config["domain_key"]
    adapter_dir = ROOT / "adapters" / domain_key
    out_path = adapter_dir / "adapter.py"

    content = ADAPTER_TEMPLATE.format(
        class_name=config["class_name"],
        domain_name_repr=repr(config["domain_name"]),
        system_prompt_repr=repr(config["system_prompt"]),
        kpi_definitions_json=json.dumps(config["kpi_definitions"], indent=4, ensure_ascii=False),
        suggested_tools_repr=repr(config.get("suggested_tools", ["data_query", "calculator"])),
        sample_questions_json=json.dumps(config["sample_questions"], indent=4, ensure_ascii=False),
        sample_data_json=json.dumps(config["sample_data"], indent=4, ensure_ascii=False),
    )

    if dry_run:
        print(f"  [DRY RUN] would write  {out_path.relative_to(ROOT)}")
        return

    adapter_dir.mkdir(parents=True, exist_ok=True)
    (adapter_dir / "__init__.py").write_text("from __future__ import annotations\n", encoding="utf-8")
    out_path.write_text(content, encoding="utf-8")
    print(f"  created  {out_path.relative_to(ROOT)}")


def write_seed_faq(config: dict, dry_run: bool) -> None:
    domain_key = config["domain_key"]
    seed_dir = ROOT / "data" / "seeds" / domain_key
    out_path = seed_dir / "sample_faq.txt"

    if dry_run:
        print(f"  [DRY RUN] would write  {out_path.relative_to(ROOT)}")
        return

    seed_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(config["faq_content"], encoding="utf-8")
    print(f"  created  {out_path.relative_to(ROOT)}")


def patch_metrics(config: dict, dry_run: bool) -> None:
    metrics_path = ROOT / "modules" / "kpi" / "metrics.py"
    if not metrics_path.exists():
        print(f"  SKIP  metrics.py not found at {metrics_path}")
        return

    domain_key = config["domain_key"]
    text = metrics_path.read_text(encoding="utf-8")

    if f'"{domain_key}"' in text:
        print(f"  SKIP  KPI entry for '{domain_key}' already exists in metrics.py")
        return

    kpi_dict_str = json.dumps(config["kpi_values"], ensure_ascii=False)
    new_entry = f'            "{domain_key}": {kpi_dict_str},\n'

    # Insert before the closing brace of domain_specific dict
    # The dict ends with "        }" immediately before "        return {**base"
    marker = "        }\n        return {**base"
    if marker in text:
        patched = text.replace(marker, new_entry + marker, 1)
    else:
        # Fallback: append a comment pointing the developer to add it manually
        patched = text
        print(
            f"  WARNING  Could not auto-patch metrics.py — add this entry manually:\n"
            f'           "{domain_key}": {kpi_dict_str}'
        )

    if dry_run:
        print(f"  [DRY RUN] would patch  modules/kpi/metrics.py  (+{domain_key} KPIs)")
        return

    metrics_path.write_text(patched, encoding="utf-8")
    print(f"  patched  modules/kpi/metrics.py")


def patch_env(config: dict, dry_run: bool) -> None:
    env_path = ROOT / ".env"
    domain_key = config["domain_key"]

    if not env_path.exists():
        print("  SKIP  .env not found — copy .env.example first, then re-run")
        return

    text = env_path.read_text(encoding="utf-8")
    if re.search(r"^ACTIVE_ADAPTER=", text, re.MULTILINE):
        patched = re.sub(r"^ACTIVE_ADAPTER=.*$", f"ACTIVE_ADAPTER={domain_key}", text, flags=re.MULTILINE)
    else:
        patched = text.rstrip() + f"\nACTIVE_ADAPTER={domain_key}\n"

    if dry_run:
        print(f"  [DRY RUN] would set   .env  ACTIVE_ADAPTER={domain_key}")
        return

    env_path.write_text(patched, encoding="utf-8")
    print(f"  updated  .env  →  ACTIVE_ADAPTER={domain_key}")


def run_ingestion(config: dict, dry_run: bool) -> None:
    ingest_script = ROOT / "scripts" / "ingest_all_seeds.py"
    if not ingest_script.exists():
        print("  SKIP  scripts/ingest_all_seeds.py not found")
        return

    if dry_run:
        print("  [DRY RUN] would run   python scripts/ingest_all_seeds.py")
        return

    import subprocess
    print("\nSeeding Qdrant RAG collections...")
    result = subprocess.run(
        [sys.executable, str(ingest_script)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode == 0:
        print("  RAG seeding complete")
    else:
        print(f"  WARNING: RAG seeding failed (non-fatal) — run manually if needed\n{result.stderr[:300]}")


# ── Summary ────────────────────────────────────────────────────────────────────

def print_summary(config: dict) -> None:
    sep = "─" * 58
    print(f"\n{sep}")
    print(f"  Domain  : {config['domain_name']}")
    print(f"  Key     : {config['domain_key']}")
    print(f"  Class   : {config['class_name']}")
    print(f"  KPIs    : {', '.join(config['kpi_definitions'].keys())}")
    print(f"  Records : {len(config['sample_data'])} synthetic sample records")
    print(f"  Q&A     : {len(config['sample_questions'])} sample questions")
    print(sep)


def print_next_steps(config: dict) -> None:
    dk = config["domain_key"]
    print(f"""
Bootstrap complete! Generated files for domain: {config['domain_name']}

  Review generated files:
    adapters/{dk}/adapter.py          ← system prompt, KPIs, sample data
    data/seeds/{dk}/sample_faq.txt    ← RAG knowledge base

  Validate:
    pytest modules/ backend/ -v --tb=short

  Run:
    uvicorn backend.main:app --reload
    # open http://localhost:8000/health  →  adapter should show "{dk}"

  Test a question:
    curl -s -X POST http://localhost:8000/api/v1/chat \\
      -H 'Content-Type: application/json' \\
      -d '{{"message": "{config['sample_questions'][0]}"}}' | python -m json.tool
""")


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Auto-generate adapter from a hackathon use case document",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Steps:
  1. Paste the hackathon problem statement into  data/usecase.md
  2. Run this script
  3. Review the generated files
  4. Run pytest and start the server
        """,
    )
    parser.add_argument(
        "--usecase",
        default="data/usecase.md",
        help="Path to use case file (default: data/usecase.md)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without writing any files",
    )
    args = parser.parse_args()

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        sys.exit("\nERROR: ANTHROPIC_API_KEY is not set.\nAdd it to .env or export it in your shell.\n")

    usecase_path = Path(args.usecase)
    if not usecase_path.is_absolute():
        usecase_path = ROOT / usecase_path

    print(f"\nEnterprise AI Platform — Use Case Bootstrap")
    print(f"{'─' * 44}")
    print(f"  Use case : {usecase_path.relative_to(ROOT)}")
    print(f"  Dry run  : {args.dry_run}")

    use_case_text = read_usecase(usecase_path)
    print(f"  Input    : {len(use_case_text)} characters read\n")

    config = call_claude(use_case_text, api_key)
    print_summary(config)

    mode = "DRY RUN — " if args.dry_run else ""
    print(f"\n{mode}Writing files...")
    write_adapter(config, args.dry_run)
    write_seed_faq(config, args.dry_run)
    patch_metrics(config, args.dry_run)
    patch_env(config, args.dry_run)
    run_ingestion(config, args.dry_run)

    if not args.dry_run:
        print_next_steps(config)
    else:
        print("\n[DRY RUN complete] No files were written. Remove --dry-run to generate.\n")


if __name__ == "__main__":
    main()
