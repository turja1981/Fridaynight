from __future__ import annotations
from fastapi import APIRouter, UploadFile, File, Form
from backend.config import settings
from modules.multimodal import MultimodalProcessor
import imghdr

router = APIRouter(tags=["multimodal"])
_processor = MultimodalProcessor(api_key=settings.anthropic_api_key)

@router.post("/multimodal/analyze")
async def analyze_file(file: UploadFile = File(...), task: str = Form(default="general")):
    content = await file.read()
    media_type = file.content_type or "image/jpeg"
    result = _processor.analyze_image_bytes(content, media_type=media_type, task=task)
    return result
