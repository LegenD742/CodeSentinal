"""
Common interface every static analyzer wrapper implements, and the
normalized finding shape they all produce before being handed to agents.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RawToolFinding:
    tool: str            # "semgrep" | "bandit" | "eslint"
    rule_id: str
    file_path: str
    start_line: int
    end_line: int
    message: str
    severity_raw: str    # tool's own severity label, normalized later
    code_snippet: str = ""


class BaseAnalyzer(ABC):
    name: str

    @abstractmethod
    async def run(self, target_dir: str, changed_files: list[str]) -> list[RawToolFinding]:
        """Run the tool against changed_files (paths relative to target_dir)."""
        raise NotImplementedError

    @abstractmethod
    def supports(self, file_path: str) -> bool:
        """Whether this analyzer applies to a given file, based on extension."""
        raise NotImplementedError
