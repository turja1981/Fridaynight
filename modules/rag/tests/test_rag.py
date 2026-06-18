from __future__ import annotations
from unittest.mock import MagicMock, patch
import pytest


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_mock_collection(docs=None, metas=None, dists=None):
    docs = docs or [["chunk one", "chunk two"]]
    metas = metas or [[{"source": "test.txt", "chunk_index": 0, "timestamp": "2024-01-01"}, {"source": "test.txt", "chunk_index": 1, "timestamp": "2024-01-01"}]]
    dists = dists or [[0.1, 0.2]]
    col = MagicMock()
    col.query.return_value = {"documents": docs, "metadatas": metas, "distances": dists}
    col.count.return_value = 2
    col.add.return_value = None
    return col


# ── DocumentIngester ──────────────────────────────────────────────────────────

class TestDocumentIngester:
    @patch("modules.rag.ingestion.chromadb.PersistentClient")
    @patch("modules.rag.ingestion.SentenceTransformer")
    def test_ingest_text_returns_ids(self, mock_st, mock_chroma):
        mock_col = _make_mock_collection()
        mock_chroma.return_value.get_or_create_collection.return_value = mock_col
        mock_st.return_value.encode.return_value = [0.1] * 384

        from modules.rag.ingestion import DocumentIngester
        ingester = DocumentIngester()
        ids = ingester.ingest_text("Hello world " * 10, "test_source")
        assert isinstance(ids, list)
        assert len(ids) > 0

    @patch("modules.rag.ingestion.chromadb.PersistentClient")
    @patch("modules.rag.ingestion.SentenceTransformer")
    def test_ingest_empty_text(self, mock_st, mock_chroma):
        mock_col = _make_mock_collection()
        mock_chroma.return_value.get_or_create_collection.return_value = mock_col
        mock_st.return_value.encode.return_value = [0.0] * 384

        from modules.rag.ingestion import DocumentIngester
        ingester = DocumentIngester()
        ids = ingester.ingest_text("", "empty_source")
        assert ids == []

    @patch("modules.rag.ingestion.chromadb.PersistentClient")
    @patch("modules.rag.ingestion.SentenceTransformer")
    def test_ingest_file_not_found(self, mock_st, mock_chroma):
        mock_col = _make_mock_collection()
        mock_chroma.return_value.get_or_create_collection.return_value = mock_col
        mock_st.return_value.encode.return_value = [0.0] * 384

        from modules.rag.ingestion import DocumentIngester
        ingester = DocumentIngester()
        with pytest.raises(FileNotFoundError):
            ingester.ingest_file("/nonexistent/file.txt")


# ── VectorRetriever ───────────────────────────────────────────────────────────

class TestVectorRetriever:
    @patch("modules.rag.retrieval.chromadb.PersistentClient")
    @patch("modules.rag.retrieval.SentenceTransformer")
    def test_retrieve_returns_results(self, mock_st, mock_chroma):
        mock_col = _make_mock_collection()
        mock_chroma.return_value.get_or_create_collection.return_value = mock_col
        mock_st.return_value.encode.return_value = [0.1] * 384

        from modules.rag.retrieval import VectorRetriever
        retriever = VectorRetriever()
        results = retriever.retrieve("test query")
        assert isinstance(results, list)
        for r in results:
            assert "content" in r
            assert "score" in r
            assert "metadata" in r

    @patch("modules.rag.retrieval.chromadb.PersistentClient")
    @patch("modules.rag.retrieval.SentenceTransformer")
    def test_retrieve_with_context_returns_string(self, mock_st, mock_chroma):
        mock_col = _make_mock_collection()
        mock_chroma.return_value.get_or_create_collection.return_value = mock_col
        mock_st.return_value.encode.return_value = [0.1] * 384

        from modules.rag.retrieval import VectorRetriever
        retriever = VectorRetriever()
        ctx = retriever.retrieve_with_context("test query")
        assert isinstance(ctx, str)
        assert len(ctx) > 0

    @patch("modules.rag.retrieval.chromadb.PersistentClient")
    @patch("modules.rag.retrieval.SentenceTransformer")
    def test_retrieve_empty_collection(self, mock_st, mock_chroma):
        mock_col = MagicMock()
        mock_col.query.return_value = {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        mock_col.count.return_value = 0
        mock_chroma.return_value.get_or_create_collection.return_value = mock_col
        mock_st.return_value.encode.return_value = [0.1] * 384

        from modules.rag.retrieval import VectorRetriever
        retriever = VectorRetriever()
        results = retriever.retrieve("test query")
        assert results == []


# ── HybridRetriever ───────────────────────────────────────────────────────────

class TestHybridRetriever:
    @patch("modules.rag.retrieval.chromadb.PersistentClient")
    @patch("modules.rag.retrieval.SentenceTransformer")
    def test_hybrid_retrieve_returns_reranked(self, mock_st, mock_chroma):
        mock_col = _make_mock_collection(
            docs=[["chunk about insurance claim processing", "banking fraud detection system"]],
            metas=[[{"source": "a.txt", "chunk_index": 0, "timestamp": "t"}, {"source": "b.txt", "chunk_index": 1, "timestamp": "t"}]],
            dists=[[0.1, 0.3]],
        )
        mock_chroma.return_value.get_or_create_collection.return_value = mock_col
        mock_st.return_value.encode.return_value = [0.1] * 384

        from modules.rag.hybrid import HybridRetriever
        retriever = HybridRetriever()
        results = retriever.retrieve("insurance claim")
        assert isinstance(results, list)


# ── RagPipeline ───────────────────────────────────────────────────────────────

class TestRagPipeline:
    @patch("modules.rag.ingestion.chromadb.PersistentClient")
    @patch("modules.rag.retrieval.chromadb.PersistentClient")
    @patch("modules.rag.ingestion.SentenceTransformer")
    @patch("modules.rag.retrieval.SentenceTransformer")
    def test_pipeline_run(self, mock_st2, mock_st1, mock_chroma2, mock_chroma1):
        mock_col = _make_mock_collection()
        for mc in [mock_chroma1, mock_chroma2]:
            mc.return_value.get_or_create_collection.return_value = mock_col
        for ms in [mock_st1, mock_st2]:
            ms.return_value.encode.return_value = [0.1] * 384

        from modules.rag.pipeline import RagPipeline
        pipeline = RagPipeline()
        result = pipeline.run("insurance claim query")
        assert "context" in result
        assert "sources" in result
        assert "retrieval_time_ms" in result

    @patch("modules.rag.ingestion.chromadb.PersistentClient")
    @patch("modules.rag.retrieval.chromadb.PersistentClient")
    @patch("modules.rag.ingestion.SentenceTransformer")
    @patch("modules.rag.retrieval.SentenceTransformer")
    def test_pipeline_ingest(self, mock_st2, mock_st1, mock_chroma2, mock_chroma1):
        mock_col = _make_mock_collection()
        for mc in [mock_chroma1, mock_chroma2]:
            mc.return_value.get_or_create_collection.return_value = mock_col
        for ms in [mock_st1, mock_st2]:
            ms.return_value.encode.return_value = [0.1] * 384

        from modules.rag.pipeline import RagPipeline
        pipeline = RagPipeline()
        result = pipeline.ingest("Sample text about claims " * 20, "test_source")
        assert "chunk_count" in result
        assert result["source"] == "test_source"
