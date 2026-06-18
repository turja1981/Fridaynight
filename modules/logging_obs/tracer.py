from __future__ import annotations
import functools
import time
import uuid
from typing import Callable, TypeVar

from .structured import get_logger

F = TypeVar("F", bound=Callable)


def trace_agent_call(func: F) -> F:
    """Decorator that logs agent call metrics including latency, tokens, and errors."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger("tracer")
        agent_name = getattr(args[0], "name", func.__name__) if args else func.__name__
        correlation_id = str(uuid.uuid4())[:8]
        user_message = args[1] if len(args) > 1 else kwargs.get("user_message", "")
        input_length = len(str(user_message))

        logger.info(
            "agent_call_start",
            agent_name=agent_name,
            input_length=input_length,
            correlation_id=correlation_id,
        )

        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            duration_ms = (time.perf_counter() - start) * 1000
            output_length = len(str(result.get("response", ""))) if isinstance(result, dict) else 0
            tokens = result.get("tokens_used", 0) if isinstance(result, dict) else 0

            logger.info(
                "agent_call_success",
                agent_name=agent_name,
                duration_ms=round(duration_ms, 2),
                output_length=output_length,
                tokens_used=tokens,
                correlation_id=correlation_id,
            )
            return result
        except Exception as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.error(
                "agent_call_error",
                agent_name=agent_name,
                duration_ms=round(duration_ms, 2),
                exception_type=type(exc).__name__,
                exception_message=str(exc),
                correlation_id=correlation_id,
            )
            raise

    return wrapper  # type: ignore[return-value]
