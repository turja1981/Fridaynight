from __future__ import annotations
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.config import settings
from modules.voice.interface import VoiceInterface

router = APIRouter(tags=["voice"])
_voice = VoiceInterface(whisper_api_key=settings.whisper_api_key)


@router.post("/voice/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe uploaded audio (WebM/WAV/MP3) to text via Whisper or demo mock."""
    audio_bytes = await file.read()
    try:
        transcript = _voice.transcribe(audio_bytes)
        return {"transcript": transcript, "language": "en"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/voice/synthesize")
async def synthesize(body: dict):
    """Return browser TTS instructions for the given text."""
    text = body.get("text", "")
    return _voice.synthesize_text(text)
