from __future__ import annotations
import base64
import os
from pathlib import Path

import anthropic

_TASK_PROMPTS: dict[str, str] = {
    "damage_assessment": (
        "Analyze this image for damage assessment. Identify: "
        "1) Type and severity of damage (minor/moderate/severe), "
        "2) Affected areas, "
        "3) Estimated repair complexity, "
        "4) Any safety hazards visible. "
        "Return structured JSON with keys: damage_type, severity, affected_areas, repair_complexity, safety_concerns, confidence."
    ),
    "document_extraction": (
        "Extract all text and structured data from this document image. "
        "Identify: document type, key fields and values, dates, amounts, signatures present. "
        "Return as structured JSON."
    ),
    "invoice_processing": (
        "Process this invoice image. Extract: vendor name, invoice number, date, "
        "line items (description, quantity, unit price, total), subtotal, taxes, grand total, payment terms. "
        "Return structured JSON."
    ),
    "id_verification": (
        "Analyze this ID document. Extract: document type, ID number (redact last 4 digits), "
        "name, date of birth, expiry date, issuing authority. "
        "Assess document authenticity (look for tampering signs). "
        "Return structured JSON with an authenticity_score (0-100)."
    ),
    "quality_control": (
        "Perform quality control inspection on this product image. "
        "Identify: defect type (if any), location of defects, severity (pass/minor/major/critical), "
        "recommended action (accept/rework/reject). "
        "Return structured JSON."
    ),
    "general": (
        "Describe this image in detail. Identify key elements, text visible, "
        "context, and any notable features. Return a comprehensive description."
    ),
}


class MultimodalProcessor:
    """Processes images and documents using Claude vision capabilities."""

    def __init__(self) -> None:
        self._client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

    def analyze_image(self, image_path: str, task: str = "general") -> dict:
        """Analyze an image using Claude vision for a specific task."""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        suffix = path.suffix.lower()
        media_types: dict[str, str] = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        media_type = media_types.get(suffix, "image/jpeg")

        image_data = base64.standard_b64encode(path.read_bytes()).decode("utf-8")
        task_prompt = _TASK_PROMPTS.get(task, _TASK_PROMPTS["general"])

        response = self._client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {"type": "text", "text": task_prompt},
                    ],
                }
            ],
        )

        description = response.content[0].text if response.content else ""
        return {
            "description": description,
            "extracted_data": description,
            "confidence": 0.95,
            "task": task,
            "model_used": "claude-sonnet-4-6",
        }
