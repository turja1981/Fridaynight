from __future__ import annotations
from typing import Optional

import chromadb
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "enterprise_docs"


class VectorRetriever:
    """Retrieves relevant documents from ChromaDB using vector similarity."""

    def __init__(self, chroma_path: str = "./data/chroma") -> None:
        self._client = chromadb.PersistentClient(path=chroma_path)
        self._collection = self._client.get_or_create_collection(COLLECTION_NAME)
        self._model = SentenceTransformer("all-MiniLM-L6-v2")

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.3,
    ) -> list[dict]:
        embedding = self._model.encode(query).tolist()
        results = self._collection.query(
            query_embeddings=[embedding],
            n_results=min(top_k, max(1, self._collection.count())),
            include=["documents", "metadatas", "distances"],
        )
        output: list[dict] = []
        if not results["documents"] or not results["documents"][0]:
            return output
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            score = 1.0 - dist  # convert distance to similarity
            if score >= min_score:
                output.append({"content": doc, "score": score, "metadata": meta})
        return output

    def retrieve_with_context(self, query: str, top_k: int = 5) -> str:
        results = self.retrieve(query, top_k=top_k)
        if not results:
            return "No relevant context found."
        parts: list[str] = []
        for i, r in enumerate(results, 1):
            src = r["metadata"].get("source", "unknown")
            parts.append(f"[{i}] (source: {src})\n{r['content']}")
        return "\n\n".join(parts)
