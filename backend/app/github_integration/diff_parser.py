"""
Parses a unified diff (as returned by GitHub's .diff media type) into
structured per-file hunks, so agents can reason about exact added/removed
lines instead of raw text, and so we can map findings back to a
`(file_path, line_number)` GitHub expects for inline comments.
"""
from dataclasses import dataclass, field


@dataclass
class DiffLine:
    type: str          # "added" | "removed" | "context"
    content: str
    new_line_no: int | None
    old_line_no: int | None


@dataclass
class DiffHunk:
    header: str
    lines: list[DiffLine] = field(default_factory=list)


@dataclass
class FileDiff:
    old_path: str
    new_path: str
    is_new_file: bool
    is_deleted_file: bool
    hunks: list[DiffHunk] = field(default_factory=list)

    def added_line_numbers(self) -> list[int]:
        return [
            ln.new_line_no
            for hunk in self.hunks
            for ln in hunk.lines
            if ln.type == "added" and ln.new_line_no is not None
        ]


def parse_unified_diff(diff_text: str) -> list[FileDiff]:
    files: list[FileDiff] = []
    current_file: FileDiff | None = None
    current_hunk: DiffHunk | None = None
    old_line_no = new_line_no = 0

    for raw_line in diff_text.splitlines():
        if raw_line.startswith("diff --git"):
            if current_file:
                files.append(current_file)
            current_file = FileDiff(old_path="", new_path="", is_new_file=False, is_deleted_file=False)
            continue

        if current_file is None:
            continue

        if raw_line.startswith("--- "):
            current_file.old_path = raw_line[4:].removeprefix("a/")
        elif raw_line.startswith("+++ "):
            current_file.new_path = raw_line[4:].removeprefix("b/")
        elif raw_line.startswith("new file mode"):
            current_file.is_new_file = True
        elif raw_line.startswith("deleted file mode"):
            current_file.is_deleted_file = True
        elif raw_line.startswith("@@"):
            # @@ -old_start,old_len +new_start,new_len @@
            header = raw_line
            parts = raw_line.split("@@")[1].strip().split(" ")
            old_part, new_part = parts[0], parts[1]
            old_line_no = int(old_part.lstrip("-").split(",")[0])
            new_line_no = int(new_part.lstrip("+").split(",")[0])
            current_hunk = DiffHunk(header=header)
            current_file.hunks.append(current_hunk)
        elif current_hunk is not None:
            if raw_line.startswith("+"):
                current_hunk.lines.append(
                    DiffLine(type="added", content=raw_line[1:], new_line_no=new_line_no, old_line_no=None)
                )
                new_line_no += 1
            elif raw_line.startswith("-"):
                current_hunk.lines.append(
                    DiffLine(type="removed", content=raw_line[1:], new_line_no=None, old_line_no=old_line_no)
                )
                old_line_no += 1
            else:
                content = raw_line[1:] if raw_line.startswith(" ") else raw_line
                current_hunk.lines.append(
                    DiffLine(type="context", content=content, new_line_no=new_line_no, old_line_no=old_line_no)
                )
                new_line_no += 1
                old_line_no += 1

    if current_file:
        files.append(current_file)
    return files
