from fastapi import APIRouter, HTTPException

from app.github.client import GitHubClient


router = APIRouter(prefix="/github", tags=["GitHub"])


@router.get("/repos/{owner}/{repo}/pulls/{pr_number}")
def get_pull_request(
    owner: str,
    repo: str,
    pr_number: int,
):
    try:
        client = GitHubClient()

        repository = f"{owner}/{repo}"

        pr = client.get_pull_request(
            repository,
            pr_number,
        )

        return {
            "number": pr.number,
            "title": pr.title,
            "body": pr.body,
            "state": pr.state,
            "user": pr.user.login,
            "html_url": pr.html_url,
            "base_branch": pr.base.ref,
            "head_branch": pr.head.ref,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/repos/{owner}/{repo}/pulls/{pr_number}/files")
def get_pull_request_files(
    owner: str,
    repo: str,
    pr_number: int,
):
    try:
        client = GitHubClient()

        repository = f"{owner}/{repo}"

        return client.get_pr_diff(
            repository,
            pr_number,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )