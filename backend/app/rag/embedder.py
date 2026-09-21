"""
Wraps the embedding model call behind two small async functions so the
rest of the app doesn't care which provider serves embeddings.

Fully local via Ollama's /api/embed endpoint, using an open embedding
model — default `nomic-embed-text` (768-dim, good quality/size tradeoff,
runs comfortably on CPU). Pull it once with:
    ollama pull nomic-embed-text

If you swap to a different local embedding model, update
EMBEDDING_DIM in .env AND the `Vector(...)` dimension in
app/db/orm/code_embedding.py + the VECTOR(...) column in
infra/postgres/init_pgvector.sql to match — pgvector requires the
column width to be fixed up front.
"""
from app.core.llm_client import embed as ollama_embed
from app.core.logging import get_logger

logger = get_logger(__name__)


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Batch-embeds a list of code/text chunks. Returns one vector per input."""
    return await ollama_embed(texts)


async def embed_query(text: str) -> list[float]:
    vectors = await ollama_embed([text])
    return vectors[0]
