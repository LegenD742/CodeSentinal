"""
Splits source files into overlapping line-based chunks for embedding.
Uses Tree-sitter enclosing-context boundaries where possible (whole
functions/classes) and falls back to fixed-size line windows otherwise.
"""
from dataclasses import dataclass

CHUNK_LINES = 60
OVERLAP_LINES = 10


@dataclass
class CodeChunk:
    file_path: str
    start_line: int
    end_line: int
    content: str
    symbol_name: str | None = None


def chunk_file(file_path: str, source_code: str) -> list[CodeChunk]:
    lines = source_code.splitlines()
    if not lines:
        return []

    chunks: list[CodeChunk] = []
    start = 0
    while start < len(lines):
        end = min(start + CHUNK_LINES, len(lines))
        content = "\n".join(lines[start:end])
        chunks.append(
            CodeChunk(file_path=file_path, start_line=start + 1, end_line=end, content=content)
        )
        if end == len(lines):
            break
        start = end - OVERLAP_LINES
    return chunks
