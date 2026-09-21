"""
Uses Tree-sitter to extract structural context around changed lines
(enclosing function/class, signature, docstring) so agents get more than
a raw diff hunk — they get "this change is inside function `foo(a, b)`".
"""
from dataclasses import dataclass

from tree_sitter_languages import get_parser

_LANGUAGE_BY_EXT = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".go": "go",
    ".java": "java",
    ".rb": "ruby",
}

_ENCLOSING_NODE_TYPES = {
    "python": {"function_definition", "class_definition"},
    "javascript": {"function_declaration", "method_definition", "class_declaration", "arrow_function"},
    "typescript": {"function_declaration", "method_definition", "class_declaration", "arrow_function"},
    "tsx": {"function_declaration", "method_definition", "class_declaration", "arrow_function"},
    "go": {"function_declaration", "method_declaration"},
    "java": {"method_declaration", "class_declaration"},
    "ruby": {"method", "class"},
}


@dataclass
class EnclosingContext:
    node_type: str
    name: str | None
    start_line: int
    end_line: int
    source: str


def _language_for(file_path: str) -> str | None:
    for ext, lang in _LANGUAGE_BY_EXT.items():
        if file_path.endswith(ext):
            return lang
    return None


def _find_name(node) -> str | None:
    for child in node.children:
        if child.type in ("identifier", "property_identifier"):
            return child.text.decode("utf-8")
    return None


def get_enclosing_context(file_path: str, source_code: str, target_line: int) -> EnclosingContext | None:
    """Return the innermost function/class enclosing `target_line` (1-indexed)."""
    language = _language_for(file_path)
    if language is None:
        return None

    parser = get_parser(language)
    tree = parser.parse(source_code.encode("utf-8"))
    enclosing_types = _ENCLOSING_NODE_TYPES.get(language, set())

    best: EnclosingContext | None = None

    def visit(node):
        nonlocal best
        start_line = node.start_point[0] + 1
        end_line = node.end_point[0] + 1
        if start_line <= target_line <= end_line:
            if node.type in enclosing_types:
                best = EnclosingContext(
                    node_type=node.type,
                    name=_find_name(node),
                    start_line=start_line,
                    end_line=end_line,
                    source=node.text.decode("utf-8"),
                )
            for child in node.children:
                visit(child)

    visit(tree.root_node)
    return best
