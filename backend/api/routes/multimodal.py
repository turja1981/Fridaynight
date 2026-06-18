from __future__ import annotations
import os
import tempfile

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

router = APIRouter(prefix="/api/v1/multimodal", tags=["multimodal"])


@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    task: str = Form(default="general"),
) -> dict:
    """Analyze an image using Claude vision capabilities."""
    from modules.multimodal.processor import MultimodalProcessor

    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type: {file.content_type}",
        )

    content = await file.read()
    suffix = "." + file.content_type.split("/")[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        processor = MultimodalProcessor()
        result = processor.analyze_image(tmp_path, task=task)
        return {
            "status": "success",
            "task": task,
            "file_name": file.filename,
            **result,
        }
    finally:
        os.unlink(tmp_path)
