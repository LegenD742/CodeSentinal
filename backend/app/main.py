from fastapi import FastAPI

from app.config import settings
from app.database.connection import Base, engine
from app.api.github import router as github_router


app = FastAPI(
    title=settings.app_name,
    description="Autonomous AI-powered GitHub Pull Request Review System",
    version="0.1.0",
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "CodeSentinel",
    }


app.include_router(github_router)