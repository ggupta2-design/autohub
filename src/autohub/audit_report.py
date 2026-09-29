"""Privacy-aware preflight audit reporting."""

from __future__ import annotations

import json
from typing import Any

from .audit import PreflightAudit


def preflight_audit_to_dict(
    audit: PreflightAudit, *, redact_names: bool = False
) -> dict[str, Any]:
    """Return a deterministic aggregate policy-audit report."""

    return {
        "schema": 1,
        "report": "preflight_audit",
        "workflow": "[redacted]" if redact_names else audit.workflow_name,
        "policy": "[redacted]" if redact_names else audit.policy_name,
        "decision": "ready" if audit.ready else "blocked",
        "summary": {
            "steps": audit.step_count,
            "waves": audit.wave_count,
            "maximum_attempts": audit.maximum_attempts,
            "maximum_timeout_seconds": audit.maximum_timeout_seconds,
            "finding_count": audit.finding_count,
        },
        "findings": [
            {"code": finding.code, "count": finding.count}
            for finding in audit.findings
        ],
    }


def format_preflight_audit(
    audit: PreflightAudit,
    *,
    as_json: bool = False,
    redact_names: bool = False,
) -> str:
    """Format an aggregate audit without exposing step-level values."""

    payload = preflight_audit_to_dict(audit, redact_names=redact_names)
    if as_json:
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"

    lines = [
        "AutoHub preflight audit",
        f"Workflow: {payload['workflow']}",
        f"Policy: {payload['policy']}",
        f"Decision: {payload['decision']}",
        f"Steps: {payload['summary']['steps']}",
        f"Waves: {payload['summary']['waves']}",
        f"Maximum attempts: {payload['summary']['maximum_attempts']}",
        (
            "Maximum timeout budget: "
            f"{payload['summary']['maximum_timeout_seconds']} seconds"
        ),
        f"Findings: {payload['summary']['finding_count']}",
    ]
    if payload["findings"]:
        lines.append("Finding codes:")
        lines.extend(
            f"  {finding['code']}: {finding['count']}"
            for finding in payload["findings"]
        )
    return "\n".join(lines) + "\n"
