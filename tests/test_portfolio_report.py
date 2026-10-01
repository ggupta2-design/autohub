import json

from autohub.audit import AuditFinding
from autohub.portfolio import PortfolioAudit
from autohub.portfolio_report import format_portfolio_audit, portfolio_audit_to_dict


def portfolio(*, blocked=1, invalid=1):
    return PortfolioAudit(
        policy_name="Confidential portfolio policy",
        discovered_files=3,
        ready_workflows=1,
        blocked_workflows=blocked,
        invalid_files=invalid,
        findings=(AuditFinding("STEP_LIMIT_EXCEEDED", blocked),)
        if blocked
        else (),
    )


def test_json_portfolio_report_is_deterministic():
    payload = json.loads(format_portfolio_audit(portfolio(), as_json=True))
    assert payload == {
        "decision": "review_required",
        "findings": [{"code": "STEP_LIMIT_EXCEEDED", "count": 1}],
        "policy": "Confidential portfolio policy",
        "report": "portfolio_audit",
        "schema": 1,
        "summary": {
            "audited_workflows": 2,
            "blocked_workflows": 1,
            "discovered_files": 3,
            "finding_count": 1,
            "invalid_files": 1,
            "ready_workflows": 1,
        },
    }


def test_redacted_report_omits_policy_and_per_file_values():
    rendered = format_portfolio_audit(
        portfolio(),
        as_json=True,
        redact_names=True,
    )
    assert "Confidential portfolio policy" not in rendered
    assert "[redacted]" in rendered
    assert "private-workflow.json" not in rendered
    assert "Private workflow" not in rendered


def test_text_report_contains_aggregate_review_counts():
    rendered = format_portfolio_audit(portfolio())
    assert "Decision: review_required" in rendered
    assert "Discovered files: 3" in rendered
    assert "Blocked workflows: 1" in rendered
    assert "Invalid files: 1" in rendered
    assert "STEP_LIMIT_EXCEEDED: 1" in rendered


def test_ready_report_omits_finding_section():
    result = PortfolioAudit(
        policy_name="Policy",
        discovered_files=1,
        ready_workflows=1,
        blocked_workflows=0,
        invalid_files=0,
        findings=(),
    )
    rendered = format_portfolio_audit(result)
    assert "Decision: ready" in rendered
    assert "Findings: 0" in rendered
    assert "Finding codes:" not in rendered


def test_dictionary_report_never_contains_path_field():
    payload = portfolio_audit_to_dict(portfolio(), redact_names=True)
    assert "paths" not in payload
    assert "files" not in payload
    assert set(payload["summary"]) == {
        "discovered_files",
        "audited_workflows",
        "ready_workflows",
        "blocked_workflows",
        "invalid_files",
        "finding_count",
    }
