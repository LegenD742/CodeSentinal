"""
Mint short-lived GitHub App installation access tokens, cached in Redis
until ~5 minutes before expiry so we don't re-mint on every API call.
"""
import json

import httpx
import redis.asyncio as aioredis

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.security import build_github_app_jwt

logger = get_logger(__name__)
settings = get_settings()


async def get_installation_token(installation_id: int) -> str:
    redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    cache_key = f"gh:installation_token:{installation_id}"

    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)["token"]

    app_jwt = build_github_app_jwt()
    url = f"{settings.github_api_base_url}/app/installations/{installation_id}/access_tokens"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {app_jwt}",
                "Accept": "application/vnd.github+json",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    # Cache for slightly less than the real ~1hr lifetime.
    await redis_client.set(cache_key, json.dumps({"token": data["token"]}), ex=55 * 60)
    return data["token"]
