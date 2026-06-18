from __future__ import annotations
import os


def setup_langsmith(api_key: str = "", project: str = "tcs-hackathon-enterprise-ai") -> bool:
    """Enable LangSmith tracing. Returns True if successfully configured.

    All LangChain and LangGraph calls are automatically traced once env vars are set —
    no code changes needed in individual modules.
    """
    key = api_key or os.getenv("LANGCHAIN_API_KEY", "")
    if not key:
        return False

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = key
    os.environ["LANGCHAIN_PROJECT"] = project
    return True


def get_langsmith_client():
    """Return a LangSmith Client if configured, else None."""
    try:
        from langsmith import Client
        return Client()
    except Exception:
        return None


def create_eval_dataset(
    dataset_name: str,
    examples: list[dict],
    description: str = "",
) -> str | None:
    """Push a labelled Q&A dataset to LangSmith for evaluation runs.

    Each example: {"input": "...", "output": "...", "context": "..."}
    Returns dataset ID or None if LangSmith not configured.
    """
    client = get_langsmith_client()
    if not client:
        return None

    try:
        dataset = client.create_dataset(dataset_name=dataset_name, description=description)
        client.create_examples(
            inputs=[{"question": e["input"]} for e in examples],
            outputs=[{"answer": e.get("output", ""), "context": e.get("context", "")} for e in examples],
            dataset_id=dataset.id,
        )
        return str(dataset.id)
    except Exception:
        return None


def log_feedback(run_id: str, score: float, key: str = "quality", comment: str = "") -> None:
    """Log human or automated feedback to a LangSmith run."""
    client = get_langsmith_client()
    if not client or not run_id:
        return
    try:
        client.create_feedback(run_id=run_id, key=key, score=score, comment=comment)
    except Exception:
        pass
