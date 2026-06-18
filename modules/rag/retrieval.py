from __future__ import annotations
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

_EMBEDDINGS: HuggingFaceEmbeddings | None = None

def _get_embeddings() -> HuggingFaceEmbeddings:
    global _EMBEDDINGS
    if _EMBEDDINGS is None:
        _EMBEDDINGS = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return _EMBEDDINGS

class VectorRetriever:
    """Semantic retriever backed by ChromaDB via LangChain."""

    def __init__(self, collection_name: str = "enterprise_docs", persist_directory: str = "./data/chroma"):
        self.vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=_get_embeddings(),
            persist_directory=persist_directory,
        )

    def retrieve(self, query: str, top_k: int = 5, min_score: float = 0.3) -> list[dict]:
        """Return top_k docs with similarity scores."""
        results = self.vectorstore.similarity_search_with_relevance_scores(query, k=top_k)
        return [
            {"content": doc.page_content, "score": score, "metadata": doc.metadata}
            for doc, score in results
            if score >= min_score
        ]

    def as_langchain_retriever(self, top_k: int = 5):
        """Return a LangChain BaseRetriever for use in LCEL chains."""
        return self.vectorstore.as_retriever(search_kwargs={"k": top_k})

    def retrieve_with_context(self, query: str, top_k: int = 5) -> str:
        results = self.retrieve(query, top_k)
        return "\n\n".join(f"[{i+1}] {r['content']}" for i, r in enumerate(results))
