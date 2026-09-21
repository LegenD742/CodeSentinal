"""
Thin async wrapper around the GitHub REST API for the specific endpoints
CodeSentinel needs: PR metadata, diffs, file contents, and review posting.
"""
import httpx

from app.core.config import get_settings
from app.github_integration.app_auth import get_installation_token

settings = get_settings()


class GitHubClient:
    def __init__(self, installation_id: int):
        self.installation_id = installation_id
        self.base_url = settings.github_api_base_url

    async def _headers(self, accept: str = "application/vnd.github+json") -> dict:
        token = await get_installation_token(self.installation_id)
        return {"Authorization": f"Bearer {token}", "Accept": accept}

    async def get_pull_request(self, owner: str, repo: str, pr_number: int) -> dict:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=await self._headers())
            resp.raise_for_status()
            return resp.json()

    async def get_pull_request_diff(self, owner: str, repo: str, pr_number: int) -> str:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        headers = await self._headers(accept="application/vnd.github.v3.diff")
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.text

    async def list_pull_request_files(self, owner: str, repo: str, pr_number: int) -> list[dict]:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        results, page = [], 1
        async with httpx.AsyncClient() as client:
            while True:
                resp = await client.get(
                    url, headers=await self._headers(), params={"per_page": 100, "page": page}
                )
                resp.raise_for_status()
                batch = resp.json()
                results.extend(batch)
                if len(batch) < 100:
                    break
                page += 1
        return results

    async def get_file_content(self, owner: str, repo: str, path: str, ref: str) -> str | None:
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url, headers=await self._headers(accept="application/vnd.github.raw"), params={"ref": ref}
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.text

    async def create_review(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        body: str,
        event: str,  # COMMENT | APPROVE | REQUEST_CHANGES
        comments: list[dict],
    ) -> dict:
        """Post a single PR review containing all inline comments at once."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        payload = {"body": body, "event": event, "comments": comments}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=await self._headers(), json=payload)
            resp.raise_for_status()
            return resp.json()
