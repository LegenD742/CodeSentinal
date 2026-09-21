"""
Chunks + embeds a set of repo files and upserts them into pgvector,
scoped to (repository_id, commit_sha) so retrieval is always against a
consistent snapshot of the codebase.
"""
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.orm.code_embedding import CodeEmbedding
from app.rag.chunker import chunk_file
from app.rag.embedder import embed_texts

logger = get_logger(__name__)


async def index_files(
    db: AsyncSession,
    repository_id,
    commit_sha: str,
    files: dict[str, str],  # file_path -> source content
) -> int:
    all_chunks = []
    for path, content in files.items():
        all_chunks.extend(chunk_file(path, content))

    if not all_chunks:
        return 0

    vectors = await embed_texts([c.content for c in all_chunks])

    # Replace any stale embeddings for these exact files at this commit (idempotent re-index).
    touched_paths = list({c.file_path for c in all_chunks})
    await db.execute(
        delete(CodeEmbedding).where(
            CodeEmbedding.repository_id == repository_id,
            CodeEmbedding.commit_sha == commit_sha,
            CodeEmbedding.file_path.in_(touched_paths),
        )
    )

    for idx, (chunk, vector) in enumerate(zip(all_chunks, vectors)):
        db.add(
            CodeEmbedding(
                repository_id=repository_id,
                file_path=chunk.file_path,
                commit_sha=commit_sha,
                chunk_index=idx,
                start_line=chunk.start_line,
                end_line=chunk.end_line,
                symbol_name=chunk.symbol_name,
                content=chunk.content,
                embedding=vector,
            )
        )
    await db.flush()
    logger.info("Indexed %s chunks for commit %s", len(all_chunks), commit_sha)
    return len(all_chunks)
