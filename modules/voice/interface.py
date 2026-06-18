from __future__ import annotations
import os


class VoiceInterface:
    """Handles voice transcription and synthesis."""

    def __init__(self) -> None:
        self._whisper_key = os.environ.get("WHISPER_API_KEY", "")

    def transcribe(self, audio_bytes: bytes, language: str = "en") -> str:
        """Transcribe audio bytes to text. Uses Whisper API if key available."""
        if self._whisper_key:
            try:
                import openai
                client = openai.OpenAI(api_key=self._whisper_key)
                import io
                audio_file = io.BytesIO(audio_bytes)
                audio_file.name = "audio.wav"
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                )
                return transcript.text
            except Exception:
                pass

        # Mock transcription for demo
        return f"[Mock transcription: Audio of {len(audio_bytes)} bytes in language '{language}']"

    def synthesize_text(self, text: str) -> dict:
        """Return instructions for browser-side TTS synthesis."""
        return {
            "method": "browser_tts",
            "text": text,
            "instructions": "Use window.speechSynthesis.speak() with the provided text",
        }

    def detect_language_from_audio(self, audio_bytes: bytes) -> str:
        """Detect language from audio bytes. Returns ISO language code."""
        if self._whisper_key:
            try:
                import openai
                import io
                client = openai.OpenAI(api_key=self._whisper_key)
                audio_file = io.BytesIO(audio_bytes)
                audio_file.name = "audio.wav"
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                )
                return getattr(transcript, "language", "en")
            except Exception:
                pass
        return "en"
