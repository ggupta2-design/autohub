import json

import pytest

from autohub.audit import AuditFinding
from autohub.integrity import WorkflowIntegrityAudit
from autohub.integrity_report import (
    format_integrity_audit,
    integrity_audit_to_dict,
)
from autohub.models import AutoHubError


def sample_audit():
    return WorkflowIntegrityAudit(
        workflow_name="Private workflow",
        step_count=5,
        component_count=2,
        findings=(
            AuditFinding("DUPLICATE_STEP_TITLE", 1),
            AuditFinding("DISCONNECTED_COMPONENT", 1),
        ),
    )


def test_json_report_has_stable_aggregate_schema():
    payload = json.loads(format_integrity_audit(sample_audit(), as_json=True))
    assert payload == {
        "schema_version": 1,
        "report": "workflow_integrity_audit",
        "workflow": "Private workflow",
        "decision": "review_required",
        "summary": {
            "steps": 5,
            "components": 2,
            "finding_count": 2,
        },
        "findings": [
            {"code": "DUPLICATE_STEP_TITLE", "count": 1},
            {"code": "DISCONNECTED_COMPONENT", "count": 1},
        ],
    }


def test_redacted_reports_omit_workflow_and_step_values():
    rendered = format_integrity_audit(
        sample_audit(), as_json=True, redact_names=True
    )
    assert '"workflow": "[redacted]"' in rendered
    assert "Private workflow" not in rendered
    assert "step-id" not in rendered
    assert "step title" not in rendered


def test_text_report_formats_clean_decision():
    clean = WorkflowIntegrityAudit(
        workflow_name="Fictional workflow",
        step_count=1,
        component_count=1,
        findings=(),
    )
    rendered = format_integrity_audit(clean)
    assert "Decision: clean" in rendered
    assert "Finding count: 0" in rendered
    assert "Findings:\n- none" in rendered


def test_integrity_report_requires_audit():
    with pytest.raises(AutoHubError, match="integrity audit must be valid"):
        integrity_audit_to_dict(object())
