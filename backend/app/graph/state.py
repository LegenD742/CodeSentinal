"""
Shared state object threaded through every LangGraph node. LangGraph
merges partial updates returned by each node into this dict-like state
using the reducers defined below (list fields append, scalar fields
overwrite).
"""
import operator
from typing import Annotated, TypedDict


class HunkTask(TypedDict):
    file_path: str
    diff_hunk: str
    enclosing_context: str
    repo_context: str
    static_findings: list[dict]


class ReviewState(TypedDict):
    # --- inputs, set once at graph start ---
    repository_id: str
    installation_id: int
    owner: str
    repo: str
    pr_number: int
    head_sha: str
    review_run_id: str

    # --- populated by fetch/analyze nodes ---
    hunk_tasks: list[HunkTask]

    # --- populated by specialist agent nodes (each appends) ---
    raw_findings: Annotated[list[dict], operator.add]

    # --- populated by critic node ---
    verified_findings: list[dict]

    # --- populated by aggregator node ---
    risk_score: float
    risk_level: str
    verdict_action: str
    summary: str

    # --- error tracking ---
    errors: Annotated[list[str], operator.add]
