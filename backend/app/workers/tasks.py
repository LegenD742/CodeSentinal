"""
The Celery task that runs the full CodeSentinel pipeline for one PR
event: fetch diff/files -> static analysis -> build per-hunk agent
tasks -> invoke the LangGraph review graph -> (graph posts to GitHub).
"""
import asyncio
import tempfile
from pathlib import Path

from sqlalchemy import select

from app.analyzers.result_normalizer import run_all_analyzers
#from app.analyzers.tree_sitter_parser import get_enclosing_context
from app.core.constants import RunStatus
from app.core.logging import get_logger
from app.db.orm.pull_request import PullRequest
from app.db.orm.repository import Repository
from app.db.orm.review_run import ReviewRun
from app.db.session import db_session_ctx
from app.github_integration.client import GitHubClient
from app.github_integration.diff_parser import parse_unified_diff
from app.rag.indexer import index_files
from app.rag.retriever import repo_context_builder
from app.workers.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="run_pr_review_pipeline", bind=True)
def run_pr_review_pipeline(self, installation_id: int, repo_full_name: str, repo_github_id: int,
                            pr_number: int, pr_payload: dict):
    """Celery entrypoint — bridges into the async pipeline."""
    return asyncio.run(
        _run_pipeline_async(installation_id, repo_full_name, repo_github_id, pr_number, pr_payload)
    )


async def _get_or_create_repository(db, repo_full_name: str, repo_github_id: int, installation_id: int) -> Repository:
    result = await db.execute(select(Repository).where(Repository.github_repo_id == repo_github_id))
    repo = result.scalar_one_or_none()
    if repo is None:
        repo = Repository(
            github_repo_id=repo_github_id,
            full_name=repo_full_name,
            installation_id=installation_id,
        )
        db.add(repo)
        await db.flush()
    return repo


async def _get_or_create_pull_request(db, repository: Repository, pr_number: int, pr_payload: dict) -> PullRequest:
    result = await db.execute(
        select(PullRequest).where(
            PullRequest.repository_id == repository.id,
            PullRequest.github_pr_number == pr_number,
        )
    )
    pr = result.scalar_one_or_none()
    if pr is None:
        pr = PullRequest(repository_id=repository.id, github_pr_number=pr_number, **pr_payload)
        db.add(pr)
    else:
        for key, value in pr_payload.items():
            setattr(pr, key, value)
    await db.flush()
    return pr


async def _run_pipeline_async(installation_id, repo_full_name, repo_github_id, pr_number, pr_payload):
    from app.graph.build_graph import review_graph  # imported here to avoid circulars at module load

    owner, repo_name = repo_full_name.split("/")
    client = GitHubClient(installation_id)

    async with db_session_ctx() as db:
        repository = await _get_or_create_repository(db, repo_full_name, repo_github_id, installation_id)
        pull_request = await _get_or_create_pull_request(db, repository, pr_number, pr_payload)

        review_run = ReviewRun(
            pull_request_id=pull_request.id,
            trigger_sha=pr_payload["head_sha"],
            status=RunStatus.FETCHING,
        )
        db.add(review_run)
        await db.flush()
        review_run_id = str(review_run.id)
        repository_id = repository.id

    # --- Fetch diff + changed files ---
    diff_text = await client.get_pull_request_diff(owner, repo_name, pr_number)
    files_meta = await client.list_pull_request_files(owner, repo_name, pr_number)
    file_diffs = parse_unified_diff(diff_text)

    changed_paths = [f["filename"] for f in files_meta if f["status"] != "removed"]

    with tempfile.TemporaryDirectory() as tmp_dir:
        file_contents: dict[str, str] = {}
        for path in changed_paths:
            content = await client.get_file_content(owner, repo_name, path, pr_payload["head_sha"])
            if content is None:
                continue
            file_contents[path] = content
            local_path = Path(tmp_dir) / path
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_text(content, errors="ignore")

        # --- Static analysis ---
        static_findings = await run_all_analyzers(tmp_dir, changed_paths)
        static_by_file: dict[str, list[dict]] = {}
        for sf in static_findings:
            static_by_file.setdefault(sf["file_path"], []).append(sf)

        # --- RAG indexing of this snapshot (so retrieval has something fresh to search) ---
        async with db_session_ctx() as db:
            await index_files(db, repository_id, pr_payload["head_sha"], file_contents)

        # --- Build per-file hunk tasks with Tree-sitter + RAG context ---
        hunk_tasks = []
        async with db_session_ctx() as db:
            for fd in file_diffs:
                path = fd.new_path
                content = file_contents.get(path)
                if content is None or not fd.hunks:
                    continue

                diff_hunk_text = "\n".join(h.header + "\n" + "\n".join(l.content for l in h.lines) for h in fd.hunks)
                first_added_line = next(iter(fd.added_line_numbers()), 1)
                enclosing = ""
                repo_context = await repo_context_builder(db, repository_id, diff_hunk_text, path)

                hunk_tasks.append(
                    {
                        "file_path": path,
                        "diff_hunk": diff_hunk_text,
                        "enclosing_context": enclosing.source if enclosing else "N/A",
                        "repo_context": repo_context,
                        "static_findings": static_by_file.get(path, []),
                    }
                )

    # --- Run the LangGraph multi-agent review ---
    initial_state = {
        "repository_id": str(repository_id),
        "installation_id": installation_id,
        "owner": owner,
        "repo": repo_name,
        "pr_number": pr_number,
        "head_sha": pr_payload["head_sha"],
        "review_run_id": review_run_id,
        "hunk_tasks": hunk_tasks,
        "raw_findings": [],
        "errors": [],
    }

    final_state = await review_graph.ainvoke(initial_state)
    logger.info(
        "Review run %s completed: risk=%s verdict=%s",
        review_run_id, final_state.get("risk_score"), final_state.get("verdict_action"),
    )
    return {"review_run_id": review_run_id, "risk_score": final_state.get("risk_score")}
