"""Seed the Qdrant vector store with domain FAQ documents.

Run once before demo:
    python scripts/ingest_all_seeds.py
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.rag.ingestion import DocumentIngester

DOMAINS = ["insurance_claims", "banking", "manufacturing", "retail"]
SEEDS_DIR = Path(__file__).parent.parent / "data" / "seeds"


def main() -> None:
    for domain in DOMAINS:
        faq_path = SEEDS_DIR / domain / "sample_faq.txt"
        if not faq_path.exists():
            print(f"[skip] {domain}: seed file not found at {faq_path}")
            continue
        print(f"[ingest] {domain} ...")
        ingester = DocumentIngester(collection_name=f"{domain}_docs")
        text = faq_path.read_text(encoding="utf-8")
        ids = ingester.ingest_text(text, source_name=f"{domain}_faq")
        print(f"  -> {len(ids)} chunks ingested into '{domain}_docs' collection")
    print("Done.")


if __name__ == "__main__":
    main()
