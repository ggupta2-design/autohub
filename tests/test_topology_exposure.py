from autohub.models import Trigger, Workflow, WorkflowStep
from autohub.topology import analyze_workflow_topology


def make_workflow(steps):
    return Workflow(
        name="Private graph",
        description="Shared downstream graph",
        enabled=True,
        trigger=Trigger("manual"),
        steps=tuple(steps),
    )


def step(step_id, depends_on=()):
    return WorkflowStep(
        id=step_id,
        title="Private title",
        action="transform",
        depends_on=depends_on,
    )


def test_diamond_descendants_are_counted_once():
    analysis = analyze_workflow_topology(
        make_workflow(
            (
                step("root"),
                step("left", ("root",)),
                step("right", ("root",)),
                step("join", ("left", "right")),
            )
        )
    )
    assert analysis.dependency_edges == 4
    assert analysis.maximum_downstream_steps == 3
    assert analysis.maximum_fan_in == 2
    assert analysis.maximum_fan_out == 2


def test_disconnected_components_preserve_aggregate_depth():
    analysis = analyze_workflow_topology(
        make_workflow(
            (
                step("first_root"),
                step("first_leaf", ("first_root",)),
                step("second_root"),
                step("second_middle", ("second_root",)),
                step("second_leaf", ("second_middle",)),
            )
        )
    )
    assert analysis.root_steps == 2
    assert analysis.leaf_steps == 2
    assert analysis.dependency_depth == 3
    assert analysis.maximum_downstream_steps == 2


def test_analysis_representation_does_not_retain_step_identity():
    analysis = analyze_workflow_topology(
        make_workflow(
            (
                step("confidential_root"),
                step("confidential_leaf", ("confidential_root",)),
            )
        )
    )
    rendered = repr(analysis)
    assert "confidential_root" not in rendered
    assert "confidential_leaf" not in rendered
    assert "Private title" not in rendered
