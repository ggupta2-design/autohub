"""Strict local workflow manifest loading."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import AutoHubError, Trigger, Workflow, WorkflowStep


MAX_WORKFLOW_BYTES = 256 * 1024
_WORKFLOW_FIELDS = {
    "schema_version",
    "name",
    "description",
    "enabled",
    "trigger",
    "steps",
}
_TRIGGER_FIELDS = {"type", "interval_minutes"}
_STEP_FIELDS = {
    "id",
    "title",
    "action",
    "depends_on",
    "timeout_seconds",
    "retries",
    "continue_on_error",
}


def _exact_fields(payload: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(payload, dict) or set(payload) != expected:
        raise AutoHubError(f"{label} must contain exactly the supported fields")
    return payload


def workflow_from_dict(payload: Any) -> Workflow:
    """Build a validated workflow from a strict schema-version-1 object."""

    data = _exact_fields(payload, _WORKFLOW_FIELDS, "workflow")
    if data["schema_version"] != 1:
        raise AutoHubError(
            f"unsupported workflow schema_version: {data['schema_version']}"
        )
    trigger_data = _exact_fields(data["trigger"], _TRIGGER_FIELDS, "trigger")
    raw_steps = data["steps"]
    if not isinstance(raw_steps, list):
        raise AutoHubError("workflow steps must be a list")
    steps = []
    for raw_step in raw_steps:
        step = _exact_fields(raw_step, _STEP_FIELDS, "step")
        dependencies = step["depends_on"]
        if not isinstance(dependencies, list):
            raise AutoHubError("step depends_on must be a list")
        steps.append(
            WorkflowStep(
                id=step["id"],
                title=step["title"],
                action=step["action"],
                depends_on=tuple(dependencies),
                timeout_seconds=step["timeout_seconds"],
                retries=step["retries"],
                continue_on_error=step["continue_on_error"],
            )
        )
    return Workflow(
        name=data["name"],
        description=data["description"],
        enabled=data["enabled"],
        trigger=Trigger(
            type=trigger_data["type"],
            interval_minutes=trigger_data["interval_minutes"],
        ),
        steps=tuple(steps),
    )


def load_workflow(path: str | Path) -> Workflow:
    """Load a bounded UTF-8 workflow without following symbolic links."""

    source = Path(path)
    if source.is_symlink():
        raise AutoHubError("workflow cannot be a symbolic link")
    if not source.exists():
        raise AutoHubError("workflow file does not exist")
    if not source.is_file():
        raise AutoHubError("workflow path is not a file")
    try:
        size = source.stat().st_size
    except OSError as exc:
        raise AutoHubError("could not inspect workflow file") from exc
    if size > MAX_WORKFLOW_BYTES:
        raise AutoHubError(
            f"workflow file cannot exceed {MAX_WORKFLOW_BYTES} bytes"
        )
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise AutoHubError("workflow is not valid UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise AutoHubError(
            f"workflow is not valid JSON at line {exc.lineno}"
        ) from exc
    except OSError as exc:
        raise AutoHubError("could not read workflow file") from exc
    return workflow_from_dict(payload)
