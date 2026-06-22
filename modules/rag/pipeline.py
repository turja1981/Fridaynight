from __future__ import annotations
import time
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from .ingestion import DocumentIngester
from .hybrid import HybridRetriever

RAG_PROMPT = ChatPromptTemplate.from_template(
    """You are a helpful enterprise AI assistant. Answer based on the context provided.
If the answer is not in the context, say so clearly.

Context:
{context}

Question: {question}

Answer:"""
)

class RagPipeline:
    """End-to-end RAG pipeline built with LangChain LCEL."""

    def __init__(
        self,
        collection_name: str = "enterprise_docs",
        persist_directory: str = "./data/qdrant",
        model: str = "claude-sonnet-4-6",
        anthropic_api_key: str = "",
    ):
        self.ingester = DocumentIngester(collection_name, persist_directory)
        self.retriever = HybridRetriever(collection_name, persist_directory)
        self.llm = ChatAnthropic(model=model, api_key=anthropic_api_key, max_tokens=1024)

    def run(self, query: str) -> dict:
        """Run the full RAG pipeline and return response with metadata."""
        t0 = time.time()
        results = self.retriever.retrieve(query, top_k=5)
        context = "\n\n".join(r["content"] for r in results)
        prompt_value = RAG_PROMPT.invoke({"context": context, "question": query})
        response = self.llm.invoke(prompt_value)
        answer = getattr(response, "content", str(response))
        return {
            "answer": answer,
            "context": context,
            "sources": [r.get("metadata", {}).get("source", "unknown") for r in results],
            "retrieval_time_ms": round((time.time() - t0) * 1000, 2),
        }

    def ingest(self, text: str, source: str) -> dict:
        ids = self.ingester.ingest_text(text, source)
        return {"status": "ok", "chunks_added": len(ids), "source": source}
