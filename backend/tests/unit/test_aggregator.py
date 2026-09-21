from app.graph.aggregator_node import _compute_risk_score, _risk_level, _verdict_for
from app.core.constants import VerdictAction


def test_compute_risk_score_ignores_rejected_findings():
    findings = [
        {"severity": "critical", "confidence": 90, "critic_verdict": "confirmed"},
        {"severity": "high", "confidence": 80, "critic_verdict": "rejected"},
    ]
    score = _compute_risk_score(findings)
    assert score == 36.0  # 40 * 0.9


def test_verdict_request_changes_on_confirmed_critical():
    findings = [{"severity": "critical", "critic_verdict": "confirmed"}]
    assert _verdict_for("critical", findings) == VerdictAction.REQUEST_CHANGES


def test_verdict_approve_on_low_risk():
    assert _verdict_for("low", []) == VerdictAction.APPROVE
