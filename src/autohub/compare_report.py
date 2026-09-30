"""Privacy-safe workflow comparison reports."""

from __future__ import annotations

import json
from typing import Any

from .compare import WorkflowComparison


def workflow_comparison_to_dict(
    comparison: WorkflowComparison,
    *,
    redact_names: bool = False,
) -> dict[str, Any]:
    """Return an aggregate workflow-version comparison report."""

    return {
        "schema": 1,
        "report": "workflow_comparison",
        "baseline": "[redacted]" if redact_names else comparison.baseline_name,
        "current": "[redacted]" if redact_names else comparison.current_name,
        "changed": comparison.changed,
        "metadata_changes": list(comparison.metadata_changes),
        "steps": {
            "added": comparison.added_steps,
            "removed": comparison.removed_steps,
            "modified": comparison.modified_steps,
            "unchanged": comparison.unchanged_steps,
            "impacted": comparison.impacted_steps,
        },
        "step_field_changes": {
            field: count for field, count in comparison.step_field_changes
        },
        "plan_deltas": {
            "steps": comparison.step_delta,
            "waves": comparison.wave_delta,
            "maximum_attempts": comparison.attempt_delta,
            "maximum_timeout_seconds": comparison.timeout_delta_seconds,
        },
    }


def format_workflow_comparison(
    comparison: WorkflowComparison,
    *,
    as_json: bool = False,
    redact_names: bool = False,
) -> str:
    """Format a comparison without exposing step identifiers or values."""

    payload = workflow_comparison_to_dict(
        comparison,
        redact_names=redact_names,
    )
    if as_json:
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"

    lines = [
        "AutoHub workflow comparison",
        f"Baseline: {payload['baseline']}",
        f"Current: {payload['current']}",
        f"Changed: {'yes' if payload['changed'] else 'no'}",
        (
            "Steps: "
            f"added={payload['steps']['added']} "
            f"removed={payload['steps']['removed']} "
            f"modified={payload['steps']['modified']} "
            f"unchanged={payload['steps']['unchanged']} "
            f"impacted={payload['steps']['impacted']}"
        ),
        (
            "Plan deltas: "
            f"steps={payload['plan_deltas']['steps']:+d} "
            f"waves={payload['plan_deltas']['waves']:+d} "
            f"attempts={payload['plan_deltas']['maximum_attempts']:+d} "
            "timeout_seconds="
            f"{payload['plan_deltas']['maximum_timeout_seconds']:+d}"
        ),
    ]
    if payload["metadata_changes"]:
        lines.append(
            "Metadata fields changed: "
            + ", ".join(payload["metadata_changes"])
        )
    if payload["step_field_changes"]:
        lines.append("Step field changes:")
        lines.extend(
            f"  {field}: {count}"
            for field, count in payload["step_field_changes"].items()
        )
    return "\n".join(lines) + "\n"
