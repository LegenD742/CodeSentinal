"""
Runs Bandit (Python security linter) against changed .py files.
"""
import asyncio
import json

from app.analyzers.base import BaseAnalyzer, RawToolFinding
from app.core.logging import get_logger

logger = get_logger(__name__)


class BanditAnalyzer(BaseAnalyzer):
    name = "bandit"

    def supports(self, file_path: str) -> bool:
        return file_path.endswith(".py")

    async def run(self, target_dir: str, changed_files: list[str]) -> list[RawToolFinding]:
        targets = [f for f in changed_files if self.supports(f)]
        if not targets:
            return []

        cmd = ["bandit", "-f", "json", "-q", *targets]
        proc = await asyncio.create_subprocess_exec(
            *cmd, cwd=target_dir, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        try:
            data = json.loads(stdout.decode() or "{}")
        except json.JSONDecodeError:
            logger.error("bandit produced invalid JSON: %s", stderr.decode()[:300])
            return []

        findings = []
        for res in data.get("results", []):
            findings.append(
                RawToolFinding(
                    tool=self.name,
                    rule_id=res.get("test_id", "unknown"),
                    file_path=res.get("filename", ""),
                    start_line=res.get("line_number", 0),
                    end_line=res.get("line_number", 0),
                    message=res.get("issue_text", ""),
                    severity_raw=res.get("issue_severity", "MEDIUM"),
                    code_snippet=res.get("code", ""),
                )
            )
        return findings
