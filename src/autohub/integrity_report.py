"""Privacy-safe workflow integrity report formatting."""

from __future__ import annotations

import json
from typing import Any

from .integrity import WorkflowIntegrityAudit
from .models import AutoHubError


def integrity_audit_to_dict(
    audit: WorkflowIntegrityAudit,
    *,
    redact_names: bool = False,
) -> dict[str, Any]:
    """Return deterministic aggregate audit data without step identities."""

    if not isinstance(audit, WorkflowIntegrityAudit):
        raise AutoHubError("integrity audit must be valid")
    return {
        "schema_version": 1,
        "report": "workflow_integrity_audit",
        "workflow": "[redacted]" if redact_names else audit.workflow_name,
        "decision": "clean" if audit.clean else "review_required",
        "summary": {
            "steps": audit.step_count,
            "components": audit.component_count,
            "finding_count": audit.finding_count,
        },
        "findings": [
            {"code": finding.code, "count": finding.count}
            for finding in audit.findings
        ],
    }


def format_integrity_audit(
    audit: WorkflowIntegrityAudit,
    *,
    as_json: bool = False,
    redact_names: bool = False,
) -> str:
    """Format a stable JSON or human-readable integrity report."""

    payload = integrity_audit_to_dict(audit, redact_names=redact_names)
    if as_json:
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"

    lines = [
        "Workflow integrity audit",
        f"Workflow: {payload['workflow']}",
        f"Decision: {payload['decision']}",
        f"Steps: {payload['summary']['steps']}",
        f"Components: {payload['summary']['components']}",
        f"Finding count: {payload['summary']['finding_count']}",
        "Findings:",
    ]
    if payload["findings"]:
        lines.extend(
            f"- {finding['code']}: {finding['count']}"
            for finding in payload["findings"]
        )
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"
