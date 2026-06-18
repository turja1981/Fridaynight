from __future__ import annotations
import time
from typing import Optional

from .ingestion import DocumentIngester
from .hybrid import HybridRetriever


class RagPipeline:
    """End-to-end RAG pipeline combining ingestion and hybrid retrieval."""

    def __init__(self, chroma_path: str = "./data/chroma") -> None:
        self._ingester = DocumentIngester(chroma_path=chroma_path)
        self._retriever = HybridRetriever(chroma_path=chroma_path)

    def run(self, query: str, context_window: int = 4000) -> dict:
        start = time.perf_counter()
        results = self._retriever.retrieve(query, top_k=5)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Build context respecting window size
        context_parts: list[str] = []
        sources: list[str] = []
        total_chars = 0
        for r in results:
            chunk = r["content"]
            if total_chars + len(chunk) > context_window:
                break
            context_parts.append(chunk)
            src = r["metadata"].get("source", "unknown")
            if src not in sources:
                sources.append(src)
            total_chars += len(chunk)

        context = "\n\n".join(context_parts) if context_parts else "No context available."
        return {
            "context": context,
            "sources": sources,
            "retrieval_time_ms": round(elapsed_ms, 2),
        }

    def ingest(self, text: str, source: str) -> dict:
        ids = self._ingester.ingest_text(text, source_name=source)
        return {"chunk_count": len(ids), "source": source, "ids": ids}
