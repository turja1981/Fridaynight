from __future__ import annotations
import os


def _build_mem0_config(anthropic_api_key: str) -> dict:
    return {
        "llm": {
            "provider": "anthropic",
            "config": {
                "model": "claude-haiku-4-5-20251001",
                "api_key": anthropic_api_key,
            },
        },
        "embedder": {
            "provider": "huggingface",
            "config": {"model": "all-MiniLM-L6-v2"},
        },
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": "agent_memory",
                "path": os.getenv("QDRANT_PATH", "./data/qdrant"),
            },
        },
    }


class AgentMemoryManager:
    """Persistent user and session memory using Mem0.

    Stores facts, preferences, and conversation history per user_id.
    Falls back to a simple in-process dict when Mem0 is unavailable.
    """

    def __init__(self, anthropic_api_key: str = "", mem0_api_key: str = ""):
        self._mem0 = None
        self._fallback: dict[str, list[dict]] = {}

        try:
            if mem0_api_key:
                from mem0 import MemoryClient
                self._mem0 = MemoryClient(api_key=mem0_api_key)
            else:
                from mem0 import Memory
                self._mem0 = Memory.from_config(_build_mem0_config(anthropic_api_key))
        except Exception:
            pass  # degraded to in-process fallback

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def add(self, messages: list[dict], user_id: str, metadata: dict | None = None) -> None:
        """Store conversation turn(s) for a user."""
        if self._mem0:
            try:
                self._mem0.add(messages, user_id=user_id, metadata=metadata or {})
                return
            except Exception:
                pass
        # Fallback
        self._fallback.setdefault(user_id, []).extend(messages)

    def search(self, query: str, user_id: str, limit: int = 5) -> list[dict]:
        """Retrieve memories relevant to the query for a given user."""
        if self._mem0:
            try:
                results = self._mem0.search(query, user_id=user_id, limit=limit)
                # Mem0 returns list of dicts with 'memory' key
                return results if isinstance(results, list) else results.get("results", [])
            except Exception:
                pass
        # Fallback: return last N messages
        history = self._fallback.get(user_id, [])
        return [{"memory": m.get("content", ""), "score": 1.0} for m in history[-limit:]]

    def get_all(self, user_id: str) -> list[dict]:
        """Return all stored memories for a user."""
        if self._mem0:
            try:
                results = self._mem0.get_all(user_id=user_id)
                return results if isinstance(results, list) else results.get("results", [])
            except Exception:
                pass
        return [{"memory": m.get("content", "")} for m in self._fallback.get(user_id, [])]

    def delete_all(self, user_id: str) -> None:
        """Clear all memories for a user."""
        if self._mem0:
            try:
                self._mem0.delete_all(user_id=user_id)
            except Exception:
                pass
        self._fallback.pop(user_id, None)

    # ------------------------------------------------------------------
    # Convenience: build context string for agent prompt injection
    # ------------------------------------------------------------------

    def build_memory_context(self, query: str, user_id: str, limit: int = 5) -> str:
        """Return a formatted string of relevant memories to prepend to agent prompt."""
        memories = self.search(query, user_id, limit)
        if not memories:
            return ""
        lines = [f"- {m.get('memory', m.get('content', ''))}" for m in memories if m]
        return "Relevant context from previous interactions:\n" + "\n".join(lines)
