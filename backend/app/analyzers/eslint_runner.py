"""
Runs ESLint against changed JS/TS files using a bundled minimal config
(security + correctness plugins), so results are consistent regardless
of the target repo's own lint setup.
"""
import asyncio
import json
import os

from app.analyzers.base import BaseAnalyzer, RawToolFinding
from app.core.logging import get_logger

logger = get_logger(__name__)

_ESLINT_SEVERITY = {1: "warning", 2: "error"}

_BUNDLED_CONFIG = """
module.exports = {
  root: true,
  parserOptions: { ecmaVersion: 2022, sourceType: "module", ecmaFeatures: { jsx: true } },
  env: { es2022: true, node: true, browser: true },
  extends: ["eslint:recommended"],
  rules: {
    "no-eval": "error",
    "no-implied-eval": "error",
    "no-new-func": "error",
    "no-unused-vars": "warn"
  }
};
"""


class ESLintAnalyzer(BaseAnalyzer):
    name = "eslint"

    def supports(self, file_path: str) -> bool:
        return file_path.endswith((".js", ".jsx", ".ts", ".tsx"))

    async def run(self, target_dir: str, changed_files: list[str]) -> list[RawToolFinding]:
        targets = [f for f in changed_files if self.supports(f)]
        if not targets:
            return []

        config_path = os.path.join(target_dir, ".codesentinel.eslintrc.js")
        with open(config_path, "w") as f:
            f.write(_BUNDLED_CONFIG)

        cmd = ["eslint", "--no-eslintrc", "-c", config_path, "--format", "json", *targets]
        proc = await asyncio.create_subprocess_exec(
            *cmd, cwd=target_dir, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        try:
            data = json.loads(stdout.decode() or "[]")
        except json.JSONDecodeError:
            logger.error("eslint produced invalid JSON: %s", stderr.decode()[:300])
            return []

        findings = []
        for file_result in data:
            path = file_result.get("filePath", "")
            for msg in file_result.get("messages", []):
                findings.append(
                    RawToolFinding(
                        tool=self.name,
                        rule_id=msg.get("ruleId") or "parse-error",
                        file_path=path,
                        start_line=msg.get("line", 0),
                        end_line=msg.get("endLine", msg.get("line", 0)),
                        message=msg.get("message", ""),
                        severity_raw=_ESLINT_SEVERITY.get(msg.get("severity", 1), "warning"),
                    )
                )
        return findings
