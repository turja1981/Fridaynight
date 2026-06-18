from __future__ import annotations
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from modules.logging_obs.structured import get_logger

_logger = get_logger("http")


class LoggingMiddleware(BaseHTTPMiddleware):
    """HTTP request/response logging middleware with correlation IDs."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Log each request with method, path, status, latency, and correlation ID."""
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4())[:8])
        start = time.perf_counter()

        _logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            correlation_id=correlation_id,
        )

        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        _logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            correlation_id=correlation_id,
        )

        response.headers["X-Correlation-ID"] = correlation_id
        return response
