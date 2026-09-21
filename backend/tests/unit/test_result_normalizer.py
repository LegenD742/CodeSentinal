from app.analyzers.base import RawToolFinding
from app.analyzers.result_normalizer import normalize
from app.core.constants import Severity


def test_normalize_maps_semgrep_severity():
    raw = RawToolFinding(
        tool="semgrep", rule_id="python.lang.security.audit.eval",
        file_path="app.py", start_line=10, end_line=10,
        message="use of eval()", severity_raw="ERROR",
    )
    result = normalize(raw)
    assert result["severity"] == Severity.HIGH
    assert result["tool"] == "semgrep"


def test_normalize_unknown_severity_defaults_medium():
    raw = RawToolFinding(
        tool="bandit", rule_id="B101", file_path="a.py",
        start_line=1, end_line=1, message="assert used", severity_raw="UNKNOWN",
    )
    assert normalize(raw)["severity"] == Severity.MEDIUM
