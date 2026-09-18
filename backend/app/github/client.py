from github import Github

from app.config import settings


class GitHubClient:

    def __init__(self):
        if not settings.github_token:
            raise ValueError("GITHUB_TOKEN is not configured")

        self.github = Github(settings.github_token)

    def get_repository(self, repo_name: str):
        return self.github.get_repo(repo_name)

    def get_pull_request(self, repo_name: str, pr_number: int):
        repo = self.get_repository(repo_name)
        return repo.get_pull(pr_number)

    def get_pr_files(self, repo_name: str, pr_number: int):
        pr = self.get_pull_request(repo_name, pr_number)

        return list(pr.get_files())

    def get_pr_diff(self, repo_name: str, pr_number: int):
        files = self.get_pr_files(repo_name, pr_number)

        diff = []

        for file in files:
            diff.append({
                "filename": file.filename,
                "status": file.status,
                "additions": file.additions,
                "deletions": file.deletions,
                "changes": file.changes,
                "patch": file.patch,
            })

        return diff