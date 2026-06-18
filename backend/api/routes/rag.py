from __future__ import annotations
import os
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/rag", tags=["rag"])


class QueryRequest(BaseModel):
    """RAG query request."""
    query: str
    top_k: int = 5


@router.post("/ingest")
async def ingest_document(file: UploadFile = File(...)) -> dict:
    """Ingest a document (PDF or text) into the RAG knowledge base."""
    from modules.rag.pipeline import RagPipeline
    from backend.config import settings

    allowed_types = {"application/pdf", "text/plain"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type: {file.content_type}. Allowed: PDF, plain text",
        )

    content = await file.read()
    pipeline = RagPipeline(chroma_path=settings.chroma_path)

    suffix = ".pdf" if file.content_type == "application/pdf" else ".txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        ingester = pipeline._ingester
        ids = ingester.ingest_file(tmp_path)
        return {
            "status": "success",
            "file_name": file.name,
            "chunk_count": len(ids),
            "chunk_ids": ids[:5],  # return first 5 IDs
        }
    finally:
        os.unlink(tmp_path)


@router.post("/query")
async def query_rag(body: QueryRequest) -> dict:
    """Query the RAG knowledge base."""
    from modules.rag.pipeline import RagPipeline
    from backend.config import settings

    pipeline = RagPipeline(chroma_path=settings.chroma_path)
    result = pipeline.run(body.query, context_window=4000)

    # Also get raw results
    raw_results = pipeline._retriever.retrieve(body.query, top_k=body.top_k)

    return {
        "query": body.query,
        "context": result["context"],
        "sources": result["sources"],
        "retrieval_time_ms": result["retrieval_time_ms"],
        "results": raw_results,
    }
