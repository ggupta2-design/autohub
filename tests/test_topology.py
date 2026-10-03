import pytest

from autohub.models import AutoHubError, Trigger, Workflow, WorkflowStep
from autohub.topology import analyze_workflow_topology


def step(step_id, depends_on=()):
    return WorkflowStep(
        id=step_id,
        title=step_id,
        action="transform",
        depends_on=depends_on,
    )


def workflow(steps):
    return Workflow(
        name="Private pipeline",
        description="Local dependency analysis",
        enabled=True,
        trigger=Trigger("manual"),
        steps=tuple(steps),
    )


def test_fork_join_topology_metrics_are_exact():
    source = workflow(
        (
            step("collect"),
            step("validate", ("collect",)),
            step("transform_a", ("validate",)),
            step("transform_b", ("validate",)),
            step("export", ("transform_a", "transform_b")),
        )
    )
    analysis = analyze_workflow_topology(source)
    assert analysis.step_count == 5
    assert analysis.dependency_edges == 5
    assert analysis.root_steps == 1
    assert analysis.leaf_steps == 1
    assert analysis.dependency_depth == 4
    assert analysis.parallel_waves == 1
    assert analysis.maximum_parallel_width == 2
    assert analysis.maximum_fan_in == 2
    assert analysis.maximum_fan_out == 2
    assert analysis.steps_with_dependents == 4
    assert analysis.maximum_downstream_steps == 4
    assert analysis.has_parallelism is True
    assert analysis.fully_sequential is False


def test_independent_steps_have_no_dependency_exposure():
    analysis = analyze_workflow_topology(
        workflow((step("alpha"), step("beta"), step("gamma")))
    )
    assert analysis.dependency_edges == 0
    assert analysis.root_steps == 3
    assert analysis.leaf_steps == 3
    assert analysis.dependency_depth == 1
    assert analysis.parallel_waves == 1
    assert analysis.maximum_parallel_width == 3
    assert analysis.maximum_fan_in == 0
    assert analysis.maximum_fan_out == 0
    assert analysis.steps_with_dependents == 0
    assert analysis.maximum_downstream_steps == 0


def test_linear_workflow_is_fully_sequential():
    analysis = analyze_workflow_topology(
        workflow(
            (
                step("first"),
                step("second", ("first",)),
                step("third", ("second",)),
            )
        )
    )
    assert analysis.dependency_depth == 3
    assert analysis.parallel_waves == 0
    assert analysis.maximum_parallel_width == 1
    assert analysis.maximum_downstream_steps == 2
    assert analysis.fully_sequential is True


def test_topology_analysis_is_independent_of_manifest_order():
    steps = (
        step("root"),
        step("left", ("root",)),
        step("right", ("root",)),
    )
    assert analyze_workflow_topology(workflow(steps)) == analyze_workflow_topology(
        workflow(reversed(steps))
    )


def test_topology_analysis_does_not_modify_workflow():
    source = workflow((step("root"), step("leaf", ("root",))))
    before = source
    analyze_workflow_topology(source)
    assert source == before


def test_topology_analysis_requires_valid_workflow():
    with pytest.raises(AutoHubError, match="workflow must be valid"):
        analyze_workflow_topology(object())
