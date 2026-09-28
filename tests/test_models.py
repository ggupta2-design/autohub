import pytest

from autohub.models import (
    ActionType,
    AutoHubError,
    Trigger,
    TriggerType,
    Workflow,
    WorkflowStep,
)


def step(**overrides):
    values = {
        "id": "collect_data",
        "title": "Collect data",
        "action": ActionType.COLLECT,
    }
    values.update(overrides)
    return WorkflowStep(**values)


def test_models_normalize_values_and_string_enums():
    workflow = Workflow(
        name="  Daily   review ",
        description="  Review   local inputs ",
        enabled=True,
        trigger=Trigger("interval", 60),
        steps=(step(action="collect"),),
    )
    assert workflow.name == "Daily review"
    assert workflow.trigger.type is TriggerType.INTERVAL
    assert workflow.steps[0].action is ActionType.COLLECT


@pytest.mark.parametrize("step_id", ["Upper", "1start", "has space", "a" * 51])
def test_step_ids_are_strict(step_id):
    with pytest.raises(AutoHubError):
        step(id=step_id)


@pytest.mark.parametrize("timeout", [0, 3601, True])
def test_timeout_bounds(timeout):
    with pytest.raises(AutoHubError):
        step(timeout_seconds=timeout)


@pytest.mark.parametrize("retries", [-1, 6, True])
def test_retry_bounds(retries):
    with pytest.raises(AutoHubError):
        step(retries=retries)


def test_manual_and_interval_trigger_rules():
    assert Trigger("manual").interval_minutes is None
    with pytest.raises(AutoHubError):
        Trigger("manual", 5)
    with pytest.raises(AutoHubError):
        Trigger("interval", 4)


def test_workflow_rejects_duplicate_and_unknown_dependencies():
    with pytest.raises(AutoHubError):
        Workflow(
            "Duplicate",
            "Duplicate identifiers",
            True,
            Trigger("manual"),
            (step(id="same"), step(id="same")),
        )
    with pytest.raises(AutoHubError):
        Workflow(
            "Missing",
            "Unknown dependency",
            True,
            Trigger("manual"),
            (step(depends_on=("missing",)),),
        )
