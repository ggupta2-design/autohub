"""Deterministic, execution-free automation planning."""

from __future__ import annotations

from dataclasses import dataclass

from .models import ActionType, AutoHubError, TriggerType, Workflow


@dataclass(frozen=True, slots=True)
class PlannedStep:
    id: str
    action: ActionType
    wave: int
    maximum_attempts: int
    timeout_seconds: int
    continue_on_error: bool


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    workflow_name: str
    enabled: bool
    trigger_type: TriggerType
    interval_minutes: int | None
    waves: tuple[tuple[PlannedStep, ...], ...]

    @property
    def step_count(self) -> int:
        return sum(len(wave) for wave in self.waves)

    @property
    def wave_count(self) -> int:
        return len(self.waves)

    @property
    def maximum_attempts(self) -> int:
        return sum(
            step.maximum_attempts for wave in self.waves for step in wave
        )

    @property
    def maximum_timeout_seconds(self) -> int:
        return sum(
            step.maximum_attempts * step.timeout_seconds
            for wave in self.waves
            for step in wave
        )


def build_execution_plan(workflow: Workflow) -> ExecutionPlan:
    """Compile a workflow DAG into stable topological execution waves."""

    if not isinstance(workflow, Workflow):
        raise AutoHubError("workflow must be valid")
    steps = {step.id: step for step in workflow.steps}
    remaining = set(steps)
    completed: set[str] = set()
    waves: list[tuple[PlannedStep, ...]] = []
    while remaining:
        ready = sorted(
            step_id
            for step_id in remaining
            if set(steps[step_id].depends_on) <= completed
        )
        if not ready:
            cycle_members = ", ".join(sorted(remaining))
            raise AutoHubError(
                f"workflow contains a dependency cycle involving: {cycle_members}"
            )
        wave_number = len(waves) + 1
        wave = tuple(
            PlannedStep(
                id=step_id,
                action=steps[step_id].action,
                wave=wave_number,
                maximum_attempts=steps[step_id].retries + 1,
                timeout_seconds=steps[step_id].timeout_seconds,
                continue_on_error=steps[step_id].continue_on_error,
            )
            for step_id in ready
        )
        waves.append(wave)
        completed.update(ready)
        remaining.difference_update(ready)

    return ExecutionPlan(
        workflow_name=workflow.name,
        enabled=workflow.enabled,
        trigger_type=workflow.trigger.type,
        interval_minutes=workflow.trigger.interval_minutes,
        waves=tuple(waves),
    )
