"""
GitHub webhook receiver. Verifies HMAC signature, dispatches by event
type, and returns immediately after enqueueing background work — GitHub
expects a fast 2xx response and will retry/disable the webhook if the
endpoint is slow or errors out.
"""
from fastapi import APIRouter, Header, HTTPException, Request

from app.core.logging import get_logger
from app.core.security import verify_github_signature
from app.github_integration.webhook_handlers import handle_pull_request_event

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = get_logger(__name__)


@router.post("/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
):
    body = await request.body()
    if not verify_github_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = await request.json()

    if x_github_event == "pull_request":
        result = await handle_pull_request_event(payload)
        return result

    if x_github_event == "ping":
        return {"status": "pong"}

    return {"status": "ignored", "reason": f"event '{x_github_event}' not handled"}
