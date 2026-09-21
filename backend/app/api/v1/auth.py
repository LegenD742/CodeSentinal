"""
Minimal placeholder auth endpoints. In production this would implement
GitHub App/OAuth login for the dashboard; kept intentionally small for
this project's scope.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/github/install-url")
async def github_install_url():
    return {"url": "https://github.com/apps/codesentinel-bot/installations/new"}
