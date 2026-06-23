from __future__ import annotations
import base64
from pathlib import Path
import anthropic

TASK_PROMPTS = {
    "damage_assessment": "Analyze this image for damage. Provide: severity (LOW/MEDIUM/HIGH), affected areas, estimated repair scope, and any safety concerns.",
    "document_extraction": "Extract all text, numbers, dates, and key fields from this document. Return as structured JSON.",
    "invoice_processing": "Extract invoice details: vendor, date, line items (description, qty, price), subtotal, taxes, total amount. Return as JSON.",
    "id_verification": "Verify this ID document. Extract: document_type, name, id_number, expiry_date, issuing_authority. Redact sensitive numbers in response.",
    "quality_control": "Inspect this product/component image for defects. Identify: defect_type, location, severity, pass/fail recommendation.",
    "general": "Describe what you see in this image in detail. Extract any text or important information.",
}

class MultimodalProcessor:
    """Processes images and documents using Claude vision."""

    def __init__(self, api_key: str = "", model: str = "claude-sonnet-4-6"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def analyze_image(self, image_path: str, task: str = "general") -> dict:
        """Analyze an image file using Claude vision."""
        path = Path(image_path)
        suffix = path.suffix.lower()
        media_type_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"}
        media_type = media_type_map.get(suffix, "image/jpeg")

        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        prompt = TASK_PROMPTS.get(task, TASK_PROMPTS["general"])
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}},
                {"type": "text", "text": prompt},
            ]}],
        )
        return {"task": task, "analysis": message.content[0].text, "model": self.model}

    def analyze_image_bytes(self, image_bytes: bytes, media_type: str = "image/jpeg", task: str = "general") -> dict:
        """Analyze image from bytes directly."""
        image_data = base64.standard_b64encode(image_bytes).decode("utf-8")
        prompt = TASK_PROMPTS.get(task, TASK_PROMPTS["general"])
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}},
                {"type": "text", "text": prompt},
            ]}],
        )
        return {"task": task, "analysis": message.content[0].text, "model": self.model}
