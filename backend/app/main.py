"""
FastAPI application entrypoint for CodeSentinel's backend API.
The review pipeline itself runs out-of-process in Celery workers
(see app/workers/tasks.py) — this process only serves the REST API
and the GitHub webhook receiver.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger

settings = get_settings()
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("CodeSentinel API starting in '%s' mode", settings.environment)
    yield
    logger.info("CodeSentinel API shutting down")


app = FastAPI(
    title="CodeSentinel API",
    description="Autonomous AI-powered GitHub Pull Request review system",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.environment}
