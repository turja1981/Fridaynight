from __future__ import annotations
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document
import pytest


def _mock_vectorstore(docs=None):
    """Return a mock LangChain Chroma vectorstore."""
    store = MagicMock()
    sample_docs = docs or [Document(page_content="chunk one", metadata={"source": "test.txt"})]
    store.add_documents.return_value = ["id-1", "id-2"]
    store.similarity_search_with_relevance_scores.return_value = [
        (Document(page_content="chunk one", metadata={"source": "test.txt"}), 0.9),
        (Document(page_content="chunk two", metadata={"source": "test.txt"}), 0.7),
    ]
    store.as_retriever.return_value = MagicMock()
    return store


# ── DocumentIngester ──────────────────────────────────────────────────────────

class TestDocumentIngester:
    @patch("modules.rag.ingestion._get_embeddings")
    @patch("modules.rag.ingestion.Chroma")
    def test_ingest_text_returns_ids(self, mock_chroma_cls, mock_embeddings):
        mock_chroma_cls.return_value = _mock_vectorstore()
        mock_embeddings.return_value = MagicMock()

        from modules.rag.ingestion import DocumentIngester
        ingester = DocumentIngester()
        ids = ingester.ingest_text("Hello world " * 20, "test_source")
        assert isinstance(ids, list)
        assert len(ids) > 0

    @patch("modules.rag.ingestion._get_embeddings")
    @patch("modules.rag.ingestion.Chroma")
    def test_ingest_empty_text_returns_empty(self, mock_chroma_cls, mock_embeddings):
        store = _mock_vectorstore()
        store.add_documents.return_value = []
        mock_chroma_cls.return_value = store
        mock_embeddings.return_value = MagicMock()

        from modules.rag.ingestion import DocumentIngester
        ingester = DocumentIngester()
        ids = ingester.ingest_text("", "empty_source")
        assert isinstance(ids, list)

    @patch("modules.rag.ingestion._get_embeddings")
    @patch("modules.rag.ingestion.Chroma")
    def test_ingest_file_not_found_raises(self, mock_chroma_cls, mock_embeddings):
        mock_chroma_cls.return_value = _mock_vectorstore()
        mock_embeddings.return_value = MagicMock()

        from modules.rag.ingestion import DocumentIngester
        ingester = DocumentIngester()
        with pytest.raises(Exception):
            ingester.ingest_file("/nonexistent/file.txt")


# ── VectorRetriever ───────────────────────────────────────────────────────────

class TestVectorRetriever:
    @patch("modules.rag.retrieval._get_embeddings")
    @patch("modules.rag.retrieval.Chroma")
    def test_retrieve_returns_results(self, mock_chroma_cls, mock_embeddings):
        mock_chroma_cls.return_value = _mock_vectorstore()
        mock_embeddings.return_value = MagicMock()

        from modules.rag.retrieval import VectorRetriever
        retriever = VectorRetriever()
        results = retriever.retrieve("test query")
        assert isinstance(results, list)
        for r in results:
            assert "content" in r
            assert "score" in r
            assert "metadata" in r

    @patch("modules.rag.retrieval._get_embeddings")
    @patch("modules.rag.retrieval.Chroma")
    def test_retrieve_with_context_returns_string(self, mock_chroma_cls, mock_embeddings):
        mock_chroma_cls.return_value = _mock_vectorstore()
        mock_embeddings.return_value = MagicMock()

        from modules.rag.retrieval import VectorRetriever
        retriever = VectorRetriever()
        ctx = retriever.retrieve_with_context("test query")
        assert isinstance(ctx, str)
        assert len(ctx) > 0

    @patch("modules.rag.retrieval._get_embeddings")
    @patch("modules.rag.retrieval.Chroma")
    def test_retrieve_empty_returns_empty(self, mock_chroma_cls, mock_embeddings):
        store = MagicMock()
        store.similarity_search_with_relevance_scores.return_value = []
        mock_chroma_cls.return_value = store
        mock_embeddings.return_value = MagicMock()

        from modules.rag.retrieval import VectorRetriever
        retriever = VectorRetriever()
        results = retriever.retrieve("test query")
        assert results == []


# ── HybridRetriever ───────────────────────────────────────────────────────────

class TestHybridRetriever:
    @patch("modules.rag.retrieval._get_embeddings")
    @patch("modules.rag.retrieval.Chroma")
    def test_hybrid_retrieve_returns_list(self, mock_chroma_cls, mock_embeddings):
        mock_chroma_cls.return_value = _mock_vectorstore()
        mock_embeddings.return_value = MagicMock()

        from modules.rag.hybrid import HybridRetriever
        retriever = HybridRetriever()
        results = retriever.retrieve("insurance claim")
        assert isinstance(results, list)


# ── RagPipeline ───────────────────────────────────────────────────────────────

class TestRagPipeline:
    @patch("modules.rag.ingestion._get_embeddings")
    @patch("modules.rag.retrieval._get_embeddings")
    @patch("modules.rag.ingestion.Chroma")
    @patch("modules.rag.retrieval.Chroma")
    @patch("modules.rag.pipeline.ChatAnthropic")
    def test_pipeline_ingest(self, mock_llm, mock_chroma_r, mock_chroma_i, mock_emb_r, mock_emb_i):
        store = _mock_vectorstore()
        mock_chroma_i.return_value = store
        mock_chroma_r.return_value = store
        mock_emb_i.return_value = MagicMock()
        mock_emb_r.return_value = MagicMock()
        mock_llm.return_value = MagicMock()

        from modules.rag.pipeline import RagPipeline
        pipeline = RagPipeline()
        result = pipeline.ingest("Sample insurance text " * 10, "test_source")
        assert result["status"] == "ok"
        assert result["source"] == "test_source"
        assert "chunks_added" in result

    @patch("modules.rag.ingestion._get_embeddings")
    @patch("modules.rag.retrieval._get_embeddings")
    @patch("modules.rag.ingestion.Chroma")
    @patch("modules.rag.retrieval.Chroma")
    @patch("modules.rag.pipeline.ChatAnthropic")
    def test_pipeline_run_returns_keys(self, mock_llm, mock_chroma_r, mock_chroma_i, mock_emb_r, mock_emb_i):
        store = _mock_vectorstore()
        mock_chroma_i.return_value = store
        mock_chroma_r.return_value = store
        mock_emb_i.return_value = MagicMock()
        mock_emb_r.return_value = MagicMock()
        llm_instance = MagicMock()
        llm_instance.invoke.return_value = MagicMock(content="The claim is under review.")
        mock_llm.return_value = llm_instance

        from modules.rag.pipeline import RagPipeline
        pipeline = RagPipeline()
        result = pipeline.run("What is the status of CLM-001?")
        assert "context" in result
        assert "sources" in result
        assert "retrieval_time_ms" in result
