"""
Tool functions exposed over MCP so an external MCP-compatible client
(e.g. an IDE assistant) can query CodeSentinel's analysis capabilities
directly — reusing the same analyzer/RAG code the review pipeline uses.
"""
from app.analyzers.result_normalizer import run_all_analyzers
from app.db.session import db_session_ctx
from app.rag.retriever import retrieve_context


async def tool_run_static_analysis(target_dir: str, changed_files: list[str]) -> list[dict]:
    """MCP tool: run Semgrep/Bandit/ESLint against a set of files and return normalized findings."""
    return await run_all_analyzers(target_dir, changed_files)


async def tool_search_codebase(repository_id: str, query: str, top_k: int = 5) -> list[dict]:
    """MCP tool: semantic search over a repository's indexed code via pgvector."""
    async with db_session_ctx() as db:
        return await retrieve_context(db, repository_id, query, top_k=top_k)
