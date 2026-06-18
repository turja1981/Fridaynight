from __future__ import annotations
from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from backend.config import settings
from modules.rag import RagPipeline, DocumentIngester
import tempfile, os

router = APIRouter(tags=["rag"])
_pipeline = RagPipeline(persist_directory=settings.chroma_path, anthropic_api_key=settings.anthropic_api_key)
_ingester = DocumentIngester(persist_directory=settings.chroma_path)

@router.post("/rag/ingest")
async def ingest_document(file: UploadFile = File(...)):
    content = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        ids = _ingester.ingest_file(tmp_path)
    finally:
        os.unlink(tmp_path)
    return {"status": "ok", "chunks_added": len(ids), "filename": file.filename}

class RagQuery(BaseModel):
    query: str
    top_k: int = 5

@router.post("/rag/query")
async def query_rag(req: RagQuery):
    result = _pipeline.run(req.query)
    return result
