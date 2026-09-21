"""
GitHub webhook signature verification + GitHub App authentication helpers.
"""
import hashlib
import hmac
import time
from pathlib import Path

import jwt

from app.core.config import get_settings


def verify_github_signature(payload_body: bytes, signature_header: str | None) -> bool:
    """Verify the `X-Hub-Signature-256` header GitHub sends with every webhook."""
    settings = get_settings()
    if not signature_header:
        return False
    if not signature_header.startswith("sha256="):
        return False

    expected = hmac.new(
        key=settings.github_webhook_secret.encode(),
        msg=payload_body,
        digestmod=hashlib.sha256,
    ).hexdigest()
    received = signature_header.split("sha256=", 1)[1]
    return hmac.compare_digest(expected, received)


def build_github_app_jwt() -> str:
    """
    Build a short-lived JWT used to authenticate as the GitHub App itself
    (used only to mint installation access tokens).
    """
    settings = get_settings()
    private_key = Path(settings.github_app_private_key_path).read_text()
    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + (9 * 60),
        "iss": settings.github_app_id,
    }
    return jwt.encode(payload, private_key, algorithm="RS256")
