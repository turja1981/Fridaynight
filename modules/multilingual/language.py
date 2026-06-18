from __future__ import annotations
import os

import anthropic

_SUPPORTED_LANGUAGES: dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "ja": "Japanese",
    "zh": "Chinese (Simplified)",
}


class LanguageDetector:
    """Detects language of input text."""

    def detect(self, text: str) -> str:
        """Detect language and return ISO 639-1 code."""
        try:
            from langdetect import detect as ld_detect
            return ld_detect(text)
        except Exception:
            return "en"


class Translator:
    """Translates text using Claude with domain term preservation."""

    def __init__(self) -> None:
        self._client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

    def translate(
        self,
        text: str,
        target_lang: str,
        preserve_terms: list[str] | None = None,
    ) -> str:
        """Translate text to target language, preserving domain-specific terms."""
        if target_lang not in _SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {target_lang}. Supported: {list(_SUPPORTED_LANGUAGES.keys())}")

        target_lang_name = _SUPPORTED_LANGUAGES[target_lang]
        preserve_clause = ""
        if preserve_terms:
            terms_str = ", ".join(f'"{t}"' for t in preserve_terms)
            preserve_clause = f"\nIMPORTANT: Keep these domain terms untranslated: {terms_str}"

        prompt = (
            f"Translate the following text to {target_lang_name}. "
            f"Maintain the professional tone and technical accuracy.{preserve_clause}\n\n"
            f"Text to translate:\n{text}\n\n"
            f"Translation:"
        )

        response = self._client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip() if response.content else text

    def supported_languages(self) -> dict[str, str]:
        """Return dict of supported language code -> language name."""
        return dict(_SUPPORTED_LANGUAGES)
