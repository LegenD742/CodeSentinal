from fastapi import APIRouter

from app.api.v1 import auth, findings, pull_requests, repos, runs, webhooks

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(webhooks.router)
api_router.include_router(repos.router)
api_router.include_router(pull_requests.router)
api_router.include_router(findings.router)
api_router.include_router(runs.router)
api_router.include_router(auth.router)
