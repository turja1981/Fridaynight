from __future__ import annotations
import uuid
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import chromadb
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "enterprise_docs"
CHUNK_SIZE = 512  # words
CHUNK_OVERLAP = 50  # words


class DocumentIngester:
    """Ingests documents into ChromaDB with embeddings."""

    def __init__(self, chroma_path: str = "./data/chroma") -> None:
        self._client = chromadb.PersistentClient(path=chroma_path)
        self._collection = self._client.get_or_create_collection(COLLECTION_NAME)
        self._model = SentenceTransformer("all-MiniLM-L6-v2")

    def _chunk_text(self, text: str) -> list[str]:
        words = text.split()
        chunks: list[str] = []
        start = 0
        while start < len(words):
            end = start + CHUNK_SIZE
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start += CHUNK_SIZE - CHUNK_OVERLAP
        return chunks

    def ingest_text(
        self,
        text: str,
        source_name: str,
        metadata: Optional[dict] = None,
    ) -> list[str]:
        chunks = self._chunk_text(text)
        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []
        embeddings: list[list[float]] = []

        base_meta = metadata or {}
        timestamp = datetime.utcnow().isoformat()

        for idx, chunk in enumerate(chunks):
            chunk_id = str(uuid.uuid4())
            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append(
                {
                    **base_meta,
                    "source": source_name,
                    "chunk_index": idx,
                    "timestamp": timestamp,
                }
            )
            embeddings.append(self._model.encode(chunk).tolist())

        if ids:
            self._collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings,
            )
        return ids

    def ingest_file(self, file_path: str) -> list[str]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if path.suffix.lower() == ".pdf":
            import pdfplumber
            text_parts: list[str] = []
            with pdfplumber.open(str(path)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    text_parts.append(page_text)
            text = "\n".join(text_parts)
        else:
            text = path.read_text(encoding="utf-8")

        return self.ingest_text(text, source_name=path.name)
