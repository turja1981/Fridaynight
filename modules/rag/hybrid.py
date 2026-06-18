from __future__ import annotations
from typing import Optional

from rank_bm25 import BM25Okapi

from .retrieval import VectorRetriever

RRF_K = 60


class HybridRetriever:
    """Combines vector similarity and BM25 keyword search with RRF re-ranking."""

    def __init__(self, chroma_path: str = "./data/chroma") -> None:
        self._vector = VectorRetriever(chroma_path=chroma_path)

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        # Get vector results (fetch more candidates for re-ranking)
        candidates = self._vector.retrieve(query, top_k=top_k * 3)
        if not candidates:
            return []

        # Build BM25 corpus from candidates
        corpus = [c["content"].split() for c in candidates]
        bm25 = BM25Okapi(corpus)
        query_tokens = query.split()
        bm25_scores = bm25.get_scores(query_tokens)

        # Build vector rank map
        vector_ranks: dict[int, int] = {i: i for i in range(len(candidates))}
        # Sort BM25 ranks
        bm25_ranks: dict[int, int] = {
            idx: rank
            for rank, idx in enumerate(
                sorted(range(len(bm25_scores)), key=lambda x: -bm25_scores[x])
            )
        }

        # RRF fusion
        rrf_scores: dict[int, float] = {}
        for i in range(len(candidates)):
            v_rank = vector_ranks.get(i, len(candidates))
            b_rank = bm25_ranks.get(i, len(candidates))
            rrf_scores[i] = 1.0 / (RRF_K + v_rank) + 1.0 / (RRF_K + b_rank)

        sorted_indices = sorted(rrf_scores, key=lambda x: -rrf_scores[x])
        result: list[dict] = []
        for idx in sorted_indices[:top_k]:
            entry = dict(candidates[idx])
            entry["rrf_score"] = rrf_scores[idx]
            result.append(entry)
        return result
