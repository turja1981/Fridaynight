from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from backend.config import settings
from modules.memory import AgentMemoryManager

router = APIRouter(tags=["memory"])

_memory = AgentMemoryManager(
    anthropic_api_key=settings.anthropic_api_key,
    mem0_api_key=settings.mem0_api_key,
)


class MemorySearchRequest(BaseModel):
    query: str
    user_id: str
    limit: int = 5


@router.get("/memory/{user_id}")
async def get_user_memories(user_id: str):
    """Return all stored memories for a user."""
    memories = _memory.get_all(user_id)
    return {"user_id": user_id, "memories": memories, "count": len(memories)}


@router.post("/memory/search")
async def search_memories(req: MemorySearchRequest):
    """Search relevant memories for a user given a query."""
    results = _memory.search(req.query, req.user_id, req.limit)
    context = _memory.build_memory_context(req.query, req.user_id, req.limit)
    return {"user_id": req.user_id, "results": results, "context_string": context}


@router.delete("/memory/{user_id}")
async def clear_memories(user_id: str):
    """Clear all memories for a user."""
    _memory.delete_all(user_id)
    return {"status": "cleared", "user_id": user_id}
