from __future__ import annotations
from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from backend.config import settings
from modules.rag import RagPipeline, DocumentIngester
import tempfile, os

router = APIRouter(tags=["rag"])

_pipeline: "RagPipeline | None" = None
_ingester: "DocumentIngester | None" = None


def _get_pipeline() -> RagPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = RagPipeline(
            persist_directory=settings.chroma_path,
            anthropic_api_key=settings.anthropic_api_key,
        )
    return _pipeline


def _get_ingester() -> DocumentIngester:
    global _ingester
    if _ingester is None:
        _ingester = DocumentIngester(persist_directory=settings.chroma_path)
    return _ingester


@router.post("/rag/ingest")
async def ingest_document(file: UploadFile = File(...)):
    content = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        ids = _get_ingester().ingest_file(tmp_path)
    finally:
        os.unlink(tmp_path)
    return {"status": "ok", "chunks_added": len(ids), "filename": file.filename}


class RagQuery(BaseModel):
    query: str
    top_k: int = 5


@router.post("/rag/query")
async def query_rag(req: RagQuery):
    result = _get_pipeline().run(req.query)
    return result
