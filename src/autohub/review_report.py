"""Privacy-safe workflow change review reports."""

from __future__ import annotations

import json
from typing import Any

from .review import ChangeReview


def change_review_to_dict(
    review: ChangeReview,
    *,
    redact_names: bool = False,
) -> dict[str, Any]:
    """Return aggregate comparison and policy evidence for a change review."""

    comparison = review.comparison
    audit = review.current_audit
    hidden = "[redacted]"
    return {
        "schema": 1,
        "report": "workflow_change_review",
        "decision": review.decision,
        "baseline": hidden if redact_names else comparison.baseline_name,
        "current": hidden if redact_names else comparison.current_name,
        "policy": hidden if redact_names else audit.policy_name,
        "changed": comparison.changed,
        "policy_ready": audit.ready,
        "changes": {
            "metadata_fields": list(comparison.metadata_changes),
            "steps": {
                "added": comparison.added_steps,
                "removed": comparison.removed_steps,
                "modified": comparison.modified_steps,
                "unchanged": comparison.unchanged_steps,
                "impacted": comparison.impacted_steps,
            },
            "step_field_counts": dict(comparison.step_field_changes),
            "plan_deltas": {
                "steps": comparison.step_delta,
                "waves": comparison.wave_delta,
                "maximum_attempts": comparison.attempt_delta,
                "maximum_timeout_seconds": comparison.timeout_delta_seconds,
            },
        },
        "current_plan": {
            "steps": audit.step_count,
            "waves": audit.wave_count,
            "maximum_attempts": audit.maximum_attempts,
            "maximum_timeout_seconds": audit.maximum_timeout_seconds,
        },
        "policy_findings": [
            {"code": finding.code, "count": finding.count}
            for finding in audit.findings
        ],
        "finding_count": audit.finding_count,
    }


def format_change_review(
    review: ChangeReview,
    *,
    as_json: bool = False,
    redact_names: bool = False,
) -> str:
    """Format review evidence without exposing step identifiers or values."""

    payload = change_review_to_dict(review, redact_names=redact_names)
    if as_json:
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"

    changes = payload["changes"]
    steps = changes["steps"]
    deltas = changes["plan_deltas"]
    lines = [
        "AutoHub workflow change review",
        f"Baseline: {payload['baseline']}",
        f"Current: {payload['current']}",
        f"Policy: {payload['policy']}",
        f"Decision: {payload['decision']}",
        f"Changed: {'yes' if payload['changed'] else 'no'}",
        f"Policy ready: {'yes' if payload['policy_ready'] else 'no'}",
        (
            "Steps: "
            f"added={steps['added']} removed={steps['removed']} "
            f"modified={steps['modified']} unchanged={steps['unchanged']} "
            f"impacted={steps['impacted']}"
        ),
        (
            "Plan deltas: "
            f"steps={deltas['steps']:+d} waves={deltas['waves']:+d} "
            f"attempts={deltas['maximum_attempts']:+d} "
            f"timeout_seconds={deltas['maximum_timeout_seconds']:+d}"
        ),
        f"Policy findings: {payload['finding_count']}",
    ]
    if changes["metadata_fields"]:
        lines.append(
            "Metadata fields changed: "
            + ", ".join(changes["metadata_fields"])
        )
    if changes["step_field_counts"]:
        lines.append("Step field changes:")
        lines.extend(
            f"  {field}: {count}"
            for field, count in changes["step_field_counts"].items()
        )
    if payload["policy_findings"]:
        lines.append("Policy finding codes:")
        lines.extend(
            f"  {finding['code']}: {finding['count']}"
            for finding in payload["policy_findings"]
        )
    return "\n".join(lines) + "\n"
