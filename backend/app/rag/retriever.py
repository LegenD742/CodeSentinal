"""
Cosine-similarity retrieval over pgvector, used to pull in relevant
repo context (e.g. related functions, callers, similar past patterns)
around a diff hunk before agents reason about it.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.orm.code_embedding import CodeEmbedding
from app.rag.embedder import embed_query


async def retrieve_context(
    db: AsyncSession,
    repository_id,
    query_text: str,
    top_k: int = 5,
    exclude_file_path: str | None = None,
) -> list[dict]:
    query_vector = await embed_query(query_text)

    stmt = (
        select(CodeEmbedding)
        .where(CodeEmbedding.repository_id == repository_id)
        .order_by(CodeEmbedding.embedding.cosine_distance(query_vector))
        .limit(top_k + (5 if exclude_file_path else 0))
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()

    if exclude_file_path:
        rows = [r for r in rows if r.file_path != exclude_file_path][:top_k]

    return [
        {
            "file_path": r.file_path,
            "start_line": r.start_line,
            "end_line": r.end_line,
            "symbol_name": r.symbol_name,
            "content": r.content,
        }
        for r in rows
    ]


async def repo_context_builder(db: AsyncSession, repository_id, diff_hunk_text: str, file_path: str) -> str:
    """Builds a short 'related context' block to inject into agent prompts."""
    matches = await retrieve_context(db, repository_id, diff_hunk_text, top_k=4, exclude_file_path=file_path)
    if not matches:
        return "No additional repository context retrieved."

    blocks = []
    for m in matches:
        label = m["symbol_name"] or f"{m['file_path']}:{m['start_line']}-{m['end_line']}"
        blocks.append(f"### {label}\n```\n{m['content']}\n```")
    return "\n\n".join(blocks)
