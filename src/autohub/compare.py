"""Privacy-aware, read-only workflow version comparisons."""

from __future__ import annotations

from dataclasses import dataclass

from .models import AutoHubError, Workflow, WorkflowStep
from .planner import build_execution_plan


_STEP_FIELDS = (
    "title",
    "action",
    "depends_on",
    "timeout_seconds",
    "retries",
    "continue_on_error",
)


@dataclass(frozen=True, slots=True)
class WorkflowComparison:
    baseline_name: str
    current_name: str
    metadata_changes: tuple[str, ...]
    added_steps: int
    removed_steps: int
    modified_steps: int
    unchanged_steps: int
    step_field_changes: tuple[tuple[str, int], ...]
    impacted_steps: int
    step_delta: int
    wave_delta: int
    attempt_delta: int
    timeout_delta_seconds: int

    @property
    def changed(self) -> bool:
        return bool(
            self.metadata_changes
            or self.added_steps
            or self.removed_steps
            or self.modified_steps
        )

    @property
    def changed_steps(self) -> int:
        return self.added_steps + self.removed_steps + self.modified_steps


def _changed_fields(baseline: WorkflowStep, current: WorkflowStep) -> tuple[str, ...]:
    return tuple(
        field
        for field in _STEP_FIELDS
        if getattr(baseline, field) != getattr(current, field)
    )


def _downstream(workflow: Workflow, seeds: set[str]) -> set[str]:
    impacted = set(seeds)
    changed = True
    while changed:
        changed = False
        for step in workflow.steps:
            if step.id not in impacted and set(step.depends_on) & impacted:
                impacted.add(step.id)
                changed = True
    return impacted


def compare_workflows(
    baseline: Workflow,
    current: Workflow,
) -> WorkflowComparison:
    """Compare two valid workflows without modifying either input."""

    if not isinstance(baseline, Workflow) or not isinstance(current, Workflow):
        raise AutoHubError("baseline and current workflows must be valid")

    metadata_changes = tuple(
        field
        for field, before, after in (
            ("name", baseline.name, current.name),
            ("description", baseline.description, current.description),
            ("enabled", baseline.enabled, current.enabled),
            ("trigger_type", baseline.trigger.type, current.trigger.type),
            (
                "interval_minutes",
                baseline.trigger.interval_minutes,
                current.trigger.interval_minutes,
            ),
        )
        if before != after
    )

    before_steps = {step.id: step for step in baseline.steps}
    after_steps = {step.id: step for step in current.steps}
    before_ids = set(before_steps)
    after_ids = set(after_steps)
    added = after_ids - before_ids
    removed = before_ids - after_ids
    common = before_ids & after_ids

    modified_ids: set[str] = set()
    field_counts = {field: 0 for field in _STEP_FIELDS}
    for step_id in sorted(common):
        fields = _changed_fields(before_steps[step_id], after_steps[step_id])
        if fields:
            modified_ids.add(step_id)
            for field in fields:
                field_counts[field] += 1

    unchanged_steps = len(common - modified_ids)
    impacted_before = _downstream(baseline, removed | modified_ids)
    impacted_after = _downstream(current, added | modified_ids)
    impacted_steps = len(impacted_before | impacted_after)

    before_plan = build_execution_plan(baseline)
    after_plan = build_execution_plan(current)
    return WorkflowComparison(
        baseline_name=baseline.name,
        current_name=current.name,
        metadata_changes=metadata_changes,
        added_steps=len(added),
        removed_steps=len(removed),
        modified_steps=len(modified_ids),
        unchanged_steps=unchanged_steps,
        step_field_changes=tuple(
            (field, count) for field, count in field_counts.items() if count
        ),
        impacted_steps=impacted_steps,
        step_delta=after_plan.step_count - before_plan.step_count,
        wave_delta=after_plan.wave_count - before_plan.wave_count,
        attempt_delta=after_plan.maximum_attempts - before_plan.maximum_attempts,
        timeout_delta_seconds=(
            after_plan.maximum_timeout_seconds
            - before_plan.maximum_timeout_seconds
        ),
    )
