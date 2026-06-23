from __future__ import annotations
import structlog
import logging
import sys

def setup_logging(log_level: str = "INFO") -> None:
    """Configure structlog with JSON output."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
    logging.basicConfig(stream=sys.stdout, level=getattr(logging, log_level.upper(), logging.INFO))

def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a structured logger bound to the given name."""
    return structlog.get_logger(name)
