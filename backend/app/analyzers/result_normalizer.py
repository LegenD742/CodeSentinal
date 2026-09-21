"""
Maps every analyzer's tool-specific severity vocabulary onto CodeSentinel's
shared severity scale, and turns RawToolFinding objects into the same
dict shape agents expect as "static analysis evidence".
"""
from app.analyzers.base import RawToolFinding
from app.core.constants import Severity

_SEVERITY_MAP = {
    # semgrep
    "ERROR": Severity.HIGH,
    "WARNING": Severity.MEDIUM,
    "INFO": Severity.LOW,
    # bandit
    "HIGH": Severity.HIGH,
    "MEDIUM": Severity.MEDIUM,
    "LOW": Severity.LOW,
    # eslint
    "error": Severity.HIGH,
    "warning": Severity.MEDIUM,
}


def normalize(raw: RawToolFinding) -> dict:
    return {
        "tool": raw.tool,
        "rule_id": raw.rule_id,
        "file_path": raw.file_path,
        "start_line": raw.start_line,
        "end_line": raw.end_line,
        "message": raw.message,
        "severity": _SEVERITY_MAP.get(raw.severity_raw, Severity.MEDIUM),
        "code_snippet": raw.code_snippet,
    }


async def run_all_analyzers(target_dir: str, changed_files: list[str]) -> list[dict]:
    """Runs semgrep, bandit and eslint concurrently and returns normalized findings."""
    import asyncio

    from app.analyzers.bandit_runner import BanditAnalyzer
    from app.analyzers.eslint_runner import ESLintAnalyzer
    from app.analyzers.semgrep_runner import SemgrepAnalyzer

    analyzers = [SemgrepAnalyzer(), BanditAnalyzer(), ESLintAnalyzer()]
    results = await asyncio.gather(
        *(a.run(target_dir, changed_files) for a in analyzers), return_exceptions=True
    )

    normalized: list[dict] = []
    for analyzer, result in zip(analyzers, results):
        if isinstance(result, Exception):
            continue
        normalized.extend(normalize(r) for r in result)
    return normalized
