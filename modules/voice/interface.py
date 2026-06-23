from __future__ import annotations
import os

class VoiceInterface:
    """Voice STT/TTS abstraction. Uses Whisper API when key available, mock otherwise."""

    def __init__(self, whisper_api_key: str = ""):
        self.whisper_api_key = whisper_api_key or os.getenv("WHISPER_API_KEY", "")

    def transcribe(self, audio_bytes: bytes, language: str = "en") -> str:
        """Transcribe audio bytes to text."""
        if self.whisper_api_key:
            try:
                import openai
                client = openai.OpenAI(api_key=self.whisper_api_key)
                import io
                audio_file = io.BytesIO(audio_bytes)
                audio_file.name = "recording.webm"
                result = client.audio.transcriptions.create(model="whisper-1", file=audio_file, language=language)
                return result.text
            except Exception:
                pass
        # Mock fallback for demo
        return "[Voice transcription demo: 'What is the status of claim CLM-001?']"

    def synthesize_text(self, text: str) -> dict:
        """Return browser TTS instructions."""
        return {"method": "browser_tts", "text": text, "lang": "en-US"}
