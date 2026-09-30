from autohub.compare import compare_workflows
from autohub.models import Trigger, Workflow, WorkflowStep


def workflow(*, name="Private workflow", enabled=True, steps=None):
    return Workflow(
        name=name,
        description="Local automation",
        enabled=enabled,
        trigger=Trigger("manual"),
        steps=steps
        or (
            WorkflowStep("collect", "Collect", "collect", timeout_seconds=30),
            WorkflowStep(
                "validate",
                "Validate",
                "validate",
                depends_on=("collect",),
                timeout_seconds=20,
            ),
            WorkflowStep(
                "export",
                "Export",
                "export",
                depends_on=("validate",),
                timeout_seconds=10,
            ),
        ),
    )


def test_identical_workflows_report_no_change():
    source = workflow()
    comparison = compare_workflows(source, source)
    assert comparison.changed is False
    assert comparison.changed_steps == 0
    assert comparison.unchanged_steps == 3
    assert comparison.metadata_changes == ()
    assert comparison.step_field_changes == ()
    assert comparison.impacted_steps == 0
    assert comparison.step_delta == 0
    assert comparison.wave_delta == 0
    assert comparison.attempt_delta == 0
    assert comparison.timeout_delta_seconds == 0


def test_comparison_aggregates_structural_and_plan_changes():
    baseline = workflow()
    current = workflow(
        enabled=False,
        steps=(
            WorkflowStep(
                "collect",
                "Collect revised",
                "collect",
                timeout_seconds=45,
                retries=1,
            ),
            WorkflowStep(
                "validate",
                "Validate",
                "validate",
                depends_on=("collect",),
                timeout_seconds=20,
            ),
            WorkflowStep(
                "archive",
                "Archive",
                "export",
                depends_on=("validate",),
                timeout_seconds=15,
            ),
        ),
    )

    comparison = compare_workflows(baseline, current)
    assert comparison.changed is True
    assert comparison.metadata_changes == ("enabled",)
    assert comparison.added_steps == 1
    assert comparison.removed_steps == 1
    assert comparison.modified_steps == 1
    assert comparison.unchanged_steps == 1
    assert comparison.changed_steps == 3
    assert comparison.step_field_changes == (
        ("title", 1),
        ("timeout_seconds", 1),
        ("retries", 1),
    )
    assert comparison.impacted_steps == 4
    assert comparison.step_delta == 0
    assert comparison.wave_delta == 0
    assert comparison.attempt_delta == 1
    assert comparison.timeout_delta_seconds == 65


def test_metadata_changes_report_field_names_not_values():
    comparison = compare_workflows(
        workflow(name="Secret baseline"),
        workflow(name="Secret current"),
    )
    assert comparison.metadata_changes == ("name",)
    assert "Secret baseline" not in comparison.metadata_changes
    assert "Secret current" not in comparison.metadata_changes


def test_reordering_steps_does_not_create_change():
    baseline = workflow()
    current = workflow(steps=tuple(reversed(baseline.steps)))
    comparison = compare_workflows(baseline, current)
    assert comparison.changed is False
    assert comparison.unchanged_steps == 3


def test_comparison_does_not_modify_inputs():
    baseline = workflow()
    current = workflow(enabled=False)
    before = (baseline, current)
    compare_workflows(baseline, current)
    assert (baseline, current) == before
