from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.api.routes import auth, chat, rag, agents, kpi, multimodal
from modules.mcp.server import router as mcp_router
from modules.logging_obs.structured import setup_logging
from modules.logging_obs.structured import get_logger
from modules.logging_obs.exceptions import handle_exception, AppException

app = FastAPI(
    title="Enterprise AI Platform",
    version="1.0.0",
    description="TCS Hackathon — Pluggable Enterprise AI Platform",
)

# CORS — allow all origins for hackathon demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize logging and log startup."""
    setup_logging(settings.log_level)
    logger = get_logger("main")
    logger.info("Platform started", adapter=settings.active_adapter, version="1.0.0")


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle application exceptions."""
    return handle_exception(exc)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    return handle_exception(exc)


# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(rag.router)
app.include_router(agents.router)
app.include_router(kpi.router)
app.include_router(multimodal.router)
app.include_router(mcp_router)


# Add logging middleware after routers
from backend.api.middleware.logging_middleware import LoggingMiddleware
app.add_middleware(LoggingMiddleware)


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "adapter": settings.active_adapter,
    }
