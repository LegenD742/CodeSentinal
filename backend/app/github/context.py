from typing import Any

from app.github.client import GitHubClient


class RepositoryContextBuilder:

    def __init__(self):
        self.github = GitHubClient()

    def build_context(
        self,
        repo_name: str,
        pr_number: int,
    ) -> dict[str, Any]:

        repo = self.github.get_repository(repo_name)
        pr = self.github.get_pull_request(repo_name, pr_number)

        files = self.github.get_pr_diff(
            repo_name,
            pr_number,
        )

        changed_files = []

        for file in files:
            changed_files.append({
                "filename": file["filename"],
                "status": file["status"],
                "additions": file["additions"],
                "deletions": file["deletions"],
                "patch": file["patch"],
            })

        relevant_files = self._get_relevant_files(
            repo,
            changed_files,
        )

        return {
            "repository": repo.full_name,
            "pr": {
                "number": pr.number,
                "title": pr.title,
                "body": pr.body,
                "base_branch": pr.base.ref,
                "head_branch": pr.head.ref,
            },
            "changed_files": changed_files,
            "relevant_files": relevant_files,
        }

    def _get_relevant_files(
        self,
        repo,
        changed_files: list[dict],
    ) -> list[dict]:

        results = []

        changed_names = {
            file["filename"]
            for file in changed_files
        }

        for filename in changed_names:

            try:
                content = repo.get_contents(filename)

                if isinstance(content, list):
                    continue

                results.append({
                    "filename": content.path,
                    "content": content.decoded_content.decode(
                        "utf-8",
                        errors="replace",
                    ),
                })

            except Exception:
                continue

        return results