from __future__ import annotations
from langdetect import detect, DetectorFactory
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

DetectorFactory.seed = 42  # reproducible detection

SUPPORTED_LANGS = {"en", "hi", "ta", "te", "bn", "fr", "de", "es", "ja", "zh"}

class LanguageDetector:
    """Detects language of input text using langdetect."""

    def detect(self, text: str) -> str:
        try:
            lang = detect(text)
            return lang if lang in SUPPORTED_LANGS else "en"
        except Exception:
            return "en"

class Translator:
    """Translates text using Claude, preserving domain-specific terminology."""

    def __init__(self, model: str = "claude-haiku-4-5-20251001", anthropic_api_key: str = ""):
        self.llm = ChatAnthropic(model=model, api_key=anthropic_api_key, max_tokens=1024)

    def translate(self, text: str, target_lang: str = "en", preserve_terms: list[str] | None = None) -> str:
        lang_names = {"en": "English", "hi": "Hindi", "ta": "Tamil", "te": "Telugu", "bn": "Bengali", "fr": "French", "de": "German", "es": "Spanish", "ja": "Japanese", "zh": "Chinese"}
        target_name = lang_names.get(target_lang, target_lang)
        preserve_note = f"Keep these terms unchanged: {', '.join(preserve_terms)}." if preserve_terms else ""
        prompt = f"Translate to {target_name}. {preserve_note} Return only the translation, no explanation.\n\nText: {text}"
        return self.llm.invoke([HumanMessage(content=prompt)]).content.strip()
