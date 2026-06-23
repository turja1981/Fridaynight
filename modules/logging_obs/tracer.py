from __future__ import annotations
import functools
import time
import uuid
from .structured import get_logger

logger = get_logger("tracer")

def trace_agent_call(func):
    """Decorator that logs entry, exit, duration, and errors for agent calls."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        correlation_id = str(uuid.uuid4())[:8]
        t0 = time.time()
        logger.info("agent_call_start", func=func.__name__, correlation_id=correlation_id)
        try:
            result = func(*args, **kwargs)
            duration_ms = round((time.time() - t0) * 1000, 2)
            logger.info("agent_call_end", func=func.__name__, duration_ms=duration_ms, correlation_id=correlation_id)
            return result
        except Exception as exc:
            duration_ms = round((time.time() - t0) * 1000, 2)
            logger.error("agent_call_error", func=func.__name__, error=str(exc), duration_ms=duration_ms, correlation_id=correlation_id)
            raise
    return wrapper
