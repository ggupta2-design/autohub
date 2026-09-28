import pytest

from autohub.models import AutoHubError, Trigger, Workflow, WorkflowStep
from autohub.planner import build_execution_plan


def step(step_id, action, depends_on=(), timeout=10, retries=0):
    return WorkflowStep(
        id=step_id,
        title=step_id,
        action=action,
        depends_on=depends_on,
        timeout_seconds=timeout,
        retries=retries,
    )


def workflow(steps):
    return Workflow(
        "Pipeline",
        "Dependency planning",
        True,
        Trigger("manual"),
        tuple(steps),
    )


def test_planner_builds_deterministic_parallel_waves():
    plan = build_execution_plan(
        workflow(
            (
                step("export", "export", ("transform_a", "transform_b")),
                step("transform_b", "transform", ("validate",)),
                step("collect", "collect"),
                step("transform_a", "transform", ("validate",)),
                step("validate", "validate", ("collect",)),
            )
        )
    )
    assert tuple(
        tuple(item.id for item in wave) for wave in plan.waves
    ) == (
        ("collect",),
        ("validate",),
        ("transform_a", "transform_b"),
        ("export",),
    )
    assert plan.step_count == 5
    assert plan.wave_count == 4


def test_planner_calculates_attempt_and_timeout_bounds():
    plan = build_execution_plan(
        workflow(
            (
                step("collect", "collect", timeout=10, retries=2),
                step("export", "export", ("collect",), timeout=20, retries=1),
            )
        )
    )
    assert plan.maximum_attempts == 5
    assert plan.maximum_timeout_seconds == 70


def test_planner_rejects_dependency_cycles():
    cyclic = workflow(
        (
            step("one", "collect", ("two",)),
            step("two", "validate", ("one",)),
        )
    )
    with pytest.raises(AutoHubError, match="dependency cycle"):
        build_execution_plan(cyclic)


def test_plan_is_independent_of_manifest_step_order():
    steps = (
        step("collect", "collect"),
        step("validate", "validate", ("collect",)),
        step("export", "export", ("validate",)),
    )
    assert build_execution_plan(workflow(steps)) == build_execution_plan(
        workflow(tuple(reversed(steps)))
    )
