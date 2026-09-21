"""
Handles the specific GitHub webhook event types CodeSentinel cares about
and enqueues a background review job. Kept free of business logic beyond
extracting the right IDs — the actual pipeline lives in workers/tasks.py.
"""
from app.core.logging import get_logger
from app.workers.tasks import run_pr_review_pipeline

logger = get_logger(__name__)

HANDLED_ACTIONS = {"opened", "synchronize", "reopened", "ready_for_review"}


async def handle_pull_request_event(payload: dict) -> dict:
    action = payload.get("action")
    if action not in HANDLED_ACTIONS:
        return {"status": "ignored", "reason": f"action '{action}' not handled"}

    pr = payload["pull_request"]
    if pr.get("draft") and action != "ready_for_review":
        return {"status": "ignored", "reason": "draft PR"}

    installation_id = payload["installation"]["id"]
    repo_full_name = payload["repository"]["full_name"]
    repo_github_id = payload["repository"]["id"]
    pr_number = pr["number"]

    task = run_pr_review_pipeline.delay(
        installation_id=installation_id,
        repo_full_name=repo_full_name,
        repo_github_id=repo_github_id,
        pr_number=pr_number,
        pr_payload={
            "title": pr["title"],
            "author_login": pr["user"]["login"],
            "base_branch": pr["base"]["ref"],
            "head_branch": pr["head"]["ref"],
            "head_sha": pr["head"]["sha"],
            "additions": pr.get("additions", 0),
            "deletions": pr.get("deletions", 0),
            "changed_files": pr.get("changed_files", 0),
        },
    )
    logger.info("Queued review pipeline task=%s pr=%s#%s", task.id, repo_full_name, pr_number)
    return {"status": "queued", "task_id": task.id}
