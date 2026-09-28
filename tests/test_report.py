import json

from autohub.models import Trigger, Workflow, WorkflowStep
from autohub.planner import build_execution_plan
from autohub.report import execution_plan_to_dict, format_execution_plan


def plan():
    workflow = Workflow(
        "Confidential customer sync",
        "Private workflow",
        True,
        Trigger("interval", 30),
        (
            WorkflowStep("private_collect", "Private collection", "collect"),
            WorkflowStep(
                "private_export",
                "Private export",
                "export",
                depends_on=("private_collect",),
                timeout_seconds=60,
                retries=1,
            ),
        ),
    )
    return build_execution_plan(workflow)


def test_plan_report_contains_deterministic_bounds():
    payload = execution_plan_to_dict(plan())
    assert payload["schema"] == 1
    assert payload["summary"] == {
        "steps": 2,
        "waves": 2,
        "maximum_attempts": 3,
        "maximum_timeout_seconds": 420,
    }
    assert payload["waves"][1]["steps"][0]["id"] == "private_export"


def test_redacted_reports_omit_workflow_and_step_names():
    rendered = format_execution_plan(plan(), redact_names=True)
    rendered += format_execution_plan(plan(), as_json=True, redact_names=True)
    assert "Confidential customer sync" not in rendered
    assert "private_collect" not in rendered
    assert "private_export" not in rendered
    assert "step-001" in rendered
    assert "step-002" in rendered


def test_json_report_is_deterministic_and_valid():
    first = format_execution_plan(plan(), as_json=True)
    assert first == format_execution_plan(plan(), as_json=True)
    assert json.loads(first)["trigger"]["interval_minutes"] == 30
