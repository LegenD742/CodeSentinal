"""
Single entry point for talking to a local, open-source LLM served by
Ollama (https://ollama.com) — used instead of a hosted API so the whole
pipeline can run fully offline on a laptop.

Every agent/node in the codebase calls `chat_completion()` here rather
than instantiating a provider SDK directly, so swapping models (or
swapping Ollama for vLLM/llama.cpp server/LM Studio later) only means
editing this one file.

Default model: llama3.2:3b (pull it first with `ollama pull llama3.2:3b`).
You can point different agents at different local models via the
`model` argument if you want a bigger model (e.g. llama3.1:8b,
qwen2.5-coder:7b) doing security/critic reasoning and the small 3b model
doing lighter categories — see core/config.py.
"""
import json

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


async def chat_completion(
    system_prompt: str,
    user_prompt: str,
    model: str | None = None,
    force_json: bool = True,
    temperature: float = 0.1,
    timeout: float = 120.0,
) -> str:
    """
    Calls Ollama's /api/chat endpoint (non-streaming) and returns the
    model's raw text response. `force_json` sets Ollama's `format: "json"`
    option, which constrains decoding to valid JSON — important for small
    open models like llama3.2:3b, which are much less reliable than
    hosted frontier models at following "respond with only JSON" as a
    plain instruction.
    """
    model_name = model or settings.llm_model
    url = f"{settings.ollama_base_url}/api/chat"

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": {"temperature": temperature},
    }
    if force_json:
        payload["format"] = "json"

    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
        except httpx.ConnectError as exc:
            raise RuntimeError(
                f"Could not reach Ollama at {settings.ollama_base_url}. "
                f"Is `ollama serve` running and is '{model_name}' pulled? "
                f"(ollama pull {model_name})"
            ) from exc

        data = resp.json()

    return data.get("message", {}).get("content", "")


async def embed(texts: list[str], model: str | None = None) -> list[list[float]]:
    """Batch-embeds text via Ollama's /api/embed endpoint (local embedding model)."""
    if not texts:
        return []

    model_name = model or settings.embedding_model
    url = f"{settings.ollama_base_url}/api/embed"

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(url, json={"model": model_name, "input": texts})
            resp.raise_for_status()
        except httpx.ConnectError as exc:
            raise RuntimeError(
                f"Could not reach Ollama at {settings.ollama_base_url} for embeddings. "
                f"Is '{model_name}' pulled? (ollama pull {model_name})"
            ) from exc
        data = resp.json()

    return data["embeddings"]


def safe_json_loads(raw_text: str, fallback=None):
    """Small helper: Ollama's JSON mode is much better than free-text parsing but
    small models occasionally wrap output in stray whitespace/newlines — strip and retry."""
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        cleaned = raw_text.strip().strip("`").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM JSON output: %s", raw_text[:300])
            return fallback
