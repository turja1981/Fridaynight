from __future__ import annotations
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from backend.config import settings
from modules.logging_obs import setup_logging, get_logger
from modules.logging_obs.exceptions import AppException
from modules.observability import setup_langsmith

setup_logging(settings.log_level)
logger = get_logger("main")

_langsmith_enabled = setup_langsmith(
    api_key=settings.langchain_api_key,
    project=settings.langchain_project,
)
if _langsmith_enabled:
    logger.info("langsmith_tracing_enabled", project=settings.langchain_project)

app = FastAPI(title="Enterprise AI Platform", version="1.0.0", description="TCS Hackathon — Modular AI Platform")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    t0 = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - t0) * 1000, 2)
    logger.info("http_request", method=request.method, path=request.url.path, status=response.status_code, duration_ms=duration_ms)
    return response

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.code, "message": exc.message})

from backend.api.routes import auth, chat, rag, agents, kpi, multimodal, memory, audit, hitl
from modules.mcp.server import mcp_router

app.include_router(auth.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(rag.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
app.include_router(kpi.router, prefix="/api/v1")
app.include_router(multimodal.router, prefix="/api/v1")
app.include_router(memory.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")
app.include_router(hitl.router, prefix="/api/v1")
app.include_router(mcp_router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "adapter": settings.active_adapter}
