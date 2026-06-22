from __future__ import annotations
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import time

_EMBEDDINGS: HuggingFaceEmbeddings | None = None
_EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 output dimension

def _get_embeddings() -> HuggingFaceEmbeddings:
    global _EMBEDDINGS
    if _EMBEDDINGS is None:
        _EMBEDDINGS = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return _EMBEDDINGS

class DocumentIngester:
    """Ingests documents into Qdrant via LangChain loaders and splitters."""

    def __init__(self, collection_name: str = "enterprise_docs", persist_directory: str = "./data/qdrant"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50,
            length_function=len,
        )
        self._client = QdrantClient(path=persist_directory)
        if not self._client.collection_exists(collection_name):
            self._client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=_EMBEDDING_DIM, distance=Distance.COSINE),
            )
        self.vectorstore = QdrantVectorStore(
            client=self._client,
            collection_name=collection_name,
            embedding=_get_embeddings(),
        )

    def ingest_text(self, text: str, source_name: str, metadata: dict | None = None) -> list[str]:
        """Chunk and embed raw text into Qdrant."""
        docs = self.splitter.create_documents(
            [text],
            metadatas=[{"source": source_name, "timestamp": str(time.time()), **(metadata or {})}],
        )
        ids = self.vectorstore.add_documents(docs)
        return ids

    def ingest_file(self, file_path: str) -> list[str]:
        """Load and ingest a PDF, TXT, or other file."""
        path = Path(file_path)
        if path.suffix.lower() == ".pdf":
            loader = PyPDFLoader(file_path)
        elif path.suffix.lower() == ".txt":
            loader = TextLoader(file_path)
        else:
            loader = UnstructuredFileLoader(file_path)
        raw_docs = loader.load()
        docs = self.splitter.split_documents(raw_docs)
        ids = self.vectorstore.add_documents(docs)
        return ids

    def get_vectorstore(self) -> QdrantVectorStore:
        return self.vectorstore
