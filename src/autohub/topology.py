"""Privacy-safe workflow dependency topology analysis."""

from __future__ import annotations

from dataclasses import dataclass

from .models import AutoHubError, Workflow
from .planner import build_execution_plan


@dataclass(frozen=True, slots=True)
class TopologyAnalysis:
    """Aggregate graph structure without step identities."""

    workflow_name: str
    step_count: int
    dependency_edges: int
    root_steps: int
    leaf_steps: int
    dependency_depth: int
    parallel_waves: int
    maximum_parallel_width: int
    maximum_fan_in: int
    maximum_fan_out: int
    steps_with_dependents: int
    maximum_downstream_steps: int

    @property
    def has_parallelism(self) -> bool:
        return self.maximum_parallel_width > 1

    @property
    def fully_sequential(self) -> bool:
        return self.maximum_parallel_width == 1


def analyze_workflow_topology(workflow: Workflow) -> TopologyAnalysis:
    """Measure a valid workflow DAG without executing or modifying it."""

    if not isinstance(workflow, Workflow):
        raise AutoHubError("workflow must be valid")

    step_ids = {step.id for step in workflow.steps}
    dependents: dict[str, set[str]] = {step_id: set() for step_id in step_ids}
    for step in workflow.steps:
        for dependency in step.depends_on:
            dependents[dependency].add(step.id)

    downstream_counts: list[int] = []
    for step_id in sorted(step_ids):
        discovered: set[str] = set()
        pending = list(dependents[step_id])
        while pending:
            candidate = pending.pop()
            if candidate in discovered:
                continue
            discovered.add(candidate)
            pending.extend(dependents[candidate] - discovered)
        downstream_counts.append(len(discovered))

    plan = build_execution_plan(workflow)
    fan_in = [len(step.depends_on) for step in workflow.steps]
    fan_out = [len(dependents[step.id]) for step in workflow.steps]
    return TopologyAnalysis(
        workflow_name=workflow.name,
        step_count=len(workflow.steps),
        dependency_edges=sum(fan_in),
        root_steps=sum(value == 0 for value in fan_in),
        leaf_steps=sum(value == 0 for value in fan_out),
        dependency_depth=plan.wave_count,
        parallel_waves=sum(len(wave) > 1 for wave in plan.waves),
        maximum_parallel_width=max(len(wave) for wave in plan.waves),
        maximum_fan_in=max(fan_in),
        maximum_fan_out=max(fan_out),
        steps_with_dependents=sum(value > 0 for value in fan_out),
        maximum_downstream_steps=max(downstream_counts),
    )
