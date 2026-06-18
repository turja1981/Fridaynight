from __future__ import annotations
from pathlib import Path


class DocumentParser:
    """Parses PDF and document files to extract text and tables."""

    def parse_pdf(self, file_path: str) -> dict:
        """Parse a PDF file and return text, page count, and metadata."""
        import pdfplumber

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")

        pages_text: list[str] = []
        metadata: dict = {}

        with pdfplumber.open(str(path)) as pdf:
            metadata = pdf.metadata or {}
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                pages_text.append(page_text)

        full_text = "\n\n".join(pages_text)
        return {
            "text": full_text,
            "pages": len(pages_text),
            "metadata": {
                "title": metadata.get("Title", ""),
                "author": metadata.get("Author", ""),
                "created": metadata.get("CreationDate", ""),
                "file_name": path.name,
                "file_size_bytes": path.stat().st_size,
            },
        }

    def extract_tables(self, file_path: str) -> list[list]:
        """Extract all tables from a PDF file."""
        import pdfplumber

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")

        all_tables: list[list] = []
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    all_tables.extend(tables)
        return all_tables
