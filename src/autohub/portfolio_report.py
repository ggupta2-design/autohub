"""Path-free workflow portfolio audit reports."""

from __future__ import annotations

import json
from typing import Any

from .portfolio import PortfolioAudit


def portfolio_audit_to_dict(
    audit: PortfolioAudit,
    *,
    redact_names: bool = False,
) -> dict[str, Any]:
    """Return an aggregate report without workflow names or file paths."""

    return {
        "schema": 1,
        "report": "portfolio_audit",
        "policy": "[redacted]" if redact_names else audit.policy_name,
        "decision": "review_required" if audit.review_required else "ready",
        "summary": {
            "discovered_files": audit.discovered_files,
            "audited_workflows": audit.audited_workflows,
            "ready_workflows": audit.ready_workflows,
            "blocked_workflows": audit.blocked_workflows,
            "invalid_files": audit.invalid_files,
            "finding_count": audit.finding_count,
        },
        "findings": [
            {"code": finding.code, "count": finding.count}
            for finding in audit.findings
        ],
    }


def format_portfolio_audit(
    audit: PortfolioAudit,
    *,
    as_json: bool = False,
    redact_names: bool = False,
) -> str:
    """Format an aggregate portfolio report with no per-file details."""

    payload = portfolio_audit_to_dict(audit, redact_names=redact_names)
    if as_json:
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"

    summary = payload["summary"]
    lines = [
        "AutoHub portfolio audit",
        f"Policy: {payload['policy']}",
        f"Decision: {payload['decision']}",
        f"Discovered files: {summary['discovered_files']}",
        f"Audited workflows: {summary['audited_workflows']}",
        f"Ready workflows: {summary['ready_workflows']}",
        f"Blocked workflows: {summary['blocked_workflows']}",
        f"Invalid files: {summary['invalid_files']}",
        f"Findings: {summary['finding_count']}",
    ]
    if payload["findings"]:
        lines.append("Finding codes:")
        lines.extend(
            f"  {finding['code']}: {finding['count']}"
            for finding in payload["findings"]
        )
    return "\n".join(lines) + "\n"
