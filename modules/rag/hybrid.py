from __future__ import annotations
from rank_bm25 import BM25Okapi
from .retrieval import VectorRetriever

class HybridRetriever:
    """Combines vector search with BM25 keyword search using Reciprocal Rank Fusion."""

    def __init__(self, collection_name: str = "enterprise_docs", persist_directory: str = "./data/chroma"):
        self.vector_retriever = VectorRetriever(collection_name, persist_directory)
        self._corpus: list[str] = []
        self._bm25: BM25Okapi | None = None

    def _build_bm25(self, docs: list[str]) -> None:
        self._corpus = docs
        tokenized = [d.lower().split() for d in docs]
        self._bm25 = BM25Okapi(tokenized)

    def _rrf_score(self, rank: int, k: int = 60) -> float:
        return 1.0 / (k + rank + 1)

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """RRF fusion of vector and BM25 results."""
        vector_results = self.vector_retriever.retrieve(query, top_k=top_k * 2)
        if not vector_results:
            return []

        # Build BM25 index from retrieved corpus
        corpus = [r["content"] for r in vector_results]
        self._build_bm25(corpus)

        bm25_scores = self._bm25.get_scores(query.lower().split()) if self._bm25 else []

        # Combine using RRF
        scores: dict[str, float] = {}
        content_map: dict[str, dict] = {}

        for rank, result in enumerate(vector_results):
            key = result["content"][:100]
            scores[key] = scores.get(key, 0) + self._rrf_score(rank)
            content_map[key] = result

        for rank, (idx, _) in enumerate(sorted(enumerate(bm25_scores), key=lambda x: -x[1])):
            if idx < len(corpus):
                key = corpus[idx][:100]
                scores[key] = scores.get(key, 0) + self._rrf_score(rank)

        sorted_keys = sorted(scores, key=lambda k: -scores[k])
        return [content_map[k] for k in sorted_keys[:top_k] if k in content_map]
