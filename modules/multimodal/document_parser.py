from __future__ import annotations
from pathlib import Path

class DocumentParser:
    """Parses PDF and text documents for content extraction."""

    def parse_pdf(self, file_path: str) -> dict:
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                pages = []
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    pages.append({"page": i + 1, "text": text, "chars": len(text)})
                full_text = "\n\n".join(p["text"] for p in pages)
                return {"text": full_text, "pages": len(pages), "page_details": pages, "source": Path(file_path).name}
        except ImportError:
            return {"text": f"[pdfplumber not available — install with: pip install pdfplumber]", "pages": 0}

    def extract_tables(self, file_path: str) -> list[list]:
        try:
            import pdfplumber
            tables = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend(page_tables)
            return tables
        except Exception:
            return []

    def parse_text(self, file_path: str) -> dict:
        text = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        return {"text": text, "chars": len(text), "source": Path(file_path).name}
