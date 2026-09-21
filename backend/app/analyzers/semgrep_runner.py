"""
Runs Semgrep with the `auto` + `p/security-audit` rulesets against the
changed files only, for fast, language-agnostic pattern-based findings
(security smells, dangerous APIs, anti-patterns).
"""
import asyncio
import json

from app.analyzers.base import BaseAnalyzer, RawToolFinding
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class SemgrepAnalyzer(BaseAnalyzer):
    name = "semgrep"

    def supports(self, file_path: str) -> bool:
        return file_path.endswith((".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".java", ".rb"))

    async def run(self, target_dir: str, changed_files: list[str]) -> list[RawToolFinding]:
        targets = [f for f in changed_files if self.supports(f)]
        if not targets:
            return []

        cmd = [
            "semgrep", "--config=auto", "--config=p/security-audit",
            "--json", "--quiet", "--timeout", str(settings.analyzer_timeout),
            *targets,
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd, cwd=target_dir, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode not in (0, 1):  # semgrep returns 1 when findings exist
            logger.warning("semgrep exited %s: %s", proc.returncode, stderr.decode()[:500])
            return []

        try:
            data = json.loads(stdout.decode() or "{}")
        except json.JSONDecodeError:
            logger.error("semgrep produced invalid JSON")
            return []

        findings = []
        for res in data.get("results", []):
            findings.append(
                RawToolFinding(
                    tool=self.name,
                    rule_id=res.get("check_id", "unknown"),
                    file_path=res.get("path", ""),
                    start_line=res.get("start", {}).get("line", 0),
                    end_line=res.get("end", {}).get("line", 0),
                    message=res.get("extra", {}).get("message", ""),
                    severity_raw=res.get("extra", {}).get("severity", "WARNING"),
                    code_snippet=res.get("extra", {}).get("lines", ""),
                )
            )
        return findings
