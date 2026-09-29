import json

from autohub.audit import AuditFinding, PreflightAudit
from autohub.audit_report import format_preflight_audit, preflight_audit_to_dict


def audit(*, findings=()):
    return PreflightAudit(
        workflow_name="Confidential workflow",
        policy_name="Internal risk policy",
        step_count=4,
        wave_count=2,
        maximum_attempts=6,
        maximum_timeout_seconds=900,
        findings=findings,
    )


def test_json_audit_report_is_deterministic():
    rendered = format_preflight_audit(
        audit(findings=(AuditFinding("STEP_LIMIT_EXCEEDED"),)),
        as_json=True,
    )
    payload = json.loads(rendered)
    assert payload == {
        "decision": "blocked",
        "findings": [{"code": "STEP_LIMIT_EXCEEDED", "count": 1}],
        "policy": "Internal risk policy",
        "report": "preflight_audit",
        "schema": 1,
        "summary": {
            "finding_count": 1,
            "maximum_attempts": 6,
            "maximum_timeout_seconds": 900,
            "steps": 4,
            "waves": 2,
        },
        "workflow": "Confidential workflow",
    }
    assert rendered.endswith("\n")


def test_redacted_reports_remove_workflow_and_policy_names():
    result = audit(
        findings=(
            AuditFinding("ACTION_NOT_ALLOWED", 2),
            AuditFinding("CONTINUE_ON_ERROR_DISALLOWED"),
        )
    )
    for as_json in (False, True):
        rendered = format_preflight_audit(
            result, as_json=as_json, redact_names=True
        )
        assert "Confidential workflow" not in rendered
        assert "Internal risk policy" not in rendered
        assert "[redacted]" in rendered
        assert "private_step" not in rendered


def test_text_report_contains_only_aggregate_findings():
    rendered = format_preflight_audit(
        audit(findings=(AuditFinding("ACTION_NOT_ALLOWED", 2),))
    )
    assert "Decision: blocked" in rendered
    assert "ACTION_NOT_ALLOWED: 2" in rendered
    assert "Maximum timeout budget: 900 seconds" in rendered


def test_ready_report_has_no_finding_section():
    rendered = format_preflight_audit(audit())
    assert "Decision: ready" in rendered
    assert "Findings: 0" in rendered
    assert "Finding codes:" not in rendered


def test_dictionary_report_matches_ready_decision():
    payload = preflight_audit_to_dict(audit(), redact_names=True)
    assert payload["decision"] == "ready"
    assert payload["findings"] == []
    assert payload["workflow"] == "[redacted]"
