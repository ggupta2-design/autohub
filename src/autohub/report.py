"""Readable and JSON execution-plan reports."""

from __future__ import annotations

import json
from typing import Any

from .planner import ExecutionPlan


def execution_plan_to_dict(
    plan: ExecutionPlan, *, redact_names: bool = False
) -> dict[str, Any]:
    """Return a stable execution-plan report."""

    labels: dict[str, str] = {}
    if redact_names:
        ordered_ids = [
            step.id for wave in plan.waves for step in wave
        ]
        labels = {
            step_id: f"step-{index:03d}"
            for index, step_id in enumerate(ordered_ids, start=1)
        }

    return {
        "schema": 1,
        "report": "execution_plan",
        "workflow": "[redacted]" if redact_names else plan.workflow_name,
        "enabled": plan.enabled,
        "trigger": {
            "type": plan.trigger_type.value,
            "interval_minutes": plan.interval_minutes,
        },
        "summary": {
            "steps": plan.step_count,
            "waves": plan.wave_count,
            "maximum_attempts": plan.maximum_attempts,
            "maximum_timeout_seconds": plan.maximum_timeout_seconds,
        },
        "waves": [
            {
                "number": number,
                "steps": [
                    {
                        "id": labels.get(step.id, step.id),
                        "action": step.action.value,
                        "maximum_attempts": step.maximum_attempts,
                        "timeout_seconds": step.timeout_seconds,
                        "continue_on_error": step.continue_on_error,
                    }
                    for step in wave
                ],
            }
            for number, wave in enumerate(plan.waves, start=1)
        ],
    }


def format_execution_plan(
    plan: ExecutionPlan,
    *,
    as_json: bool = False,
    redact_names: bool = False,
) -> str:
    """Format a plan without executing any workflow action."""

    payload = execution_plan_to_dict(plan, redact_names=redact_names)
    if as_json:
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"

    lines = [
        "AutoHub execution plan",
        f"Workflow: {payload['workflow']}",
        f"Enabled: {'yes' if payload['enabled'] else 'no'}",
        f"Trigger: {payload['trigger']['type']}",
        f"Steps: {payload['summary']['steps']}",
        f"Waves: {payload['summary']['waves']}",
        f"Maximum attempts: {payload['summary']['maximum_attempts']}",
        (
            "Maximum timeout budget: "
            f"{payload['summary']['maximum_timeout_seconds']} seconds"
        ),
    ]
    for wave in payload["waves"]:
        lines.append(f"Wave {wave['number']}:")
        for step in wave["steps"]:
            lines.append(
                f"  {step['id']} [{step['action']}] "
                f"attempts={step['maximum_attempts']} "
                f"timeout={step['timeout_seconds']}s"
            )
    return "\n".join(lines) + "\n"
