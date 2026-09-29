import pytest

from autohub.audit import AuditFinding, audit_workflow
from autohub.models import AutoHubError, Trigger, Workflow, WorkflowStep
from autohub.planner import build_execution_plan
from autohub.policy import GuardrailPolicy


def workflow(*, enabled=True, continue_on_error=False):
    return Workflow(
        name="Private operations workflow",
        description="Fictional local workflow",
        enabled=enabled,
        trigger=Trigger("manual"),
        steps=(
            WorkflowStep(
                "collect_data",
                "Collect",
                "collect",
                timeout_seconds=30,
                retries=1,
                continue_on_error=continue_on_error,
            ),
            WorkflowStep(
                "validate_data",
                "Validate",
                "validate",
                depends_on=("collect_data",),
                timeout_seconds=20,
            ),
            WorkflowStep(
                "export_data",
                "Export",
                "export",
                depends_on=("validate_data",),
                timeout_seconds=10,
            ),
        ),
    )


def policy(**changes):
    values = {
        "name": "Conservative policy",
        "require_enabled": True,
        "maximum_steps": 10,
        "maximum_waves": 10,
        "maximum_attempts": 10,
        "maximum_timeout_seconds": 1000,
        "allow_continue_on_error": False,
        "allowed_actions": ("collect", "validate", "transform", "export"),
    }
    values.update(changes)
    return GuardrailPolicy(**values)


def test_ready_workflow_has_no_findings():
    audit = audit_workflow(workflow(), policy())
    assert audit.ready is True
    assert audit.finding_count == 0
    assert audit.step_count == 3
    assert audit.wave_count == 3
    assert audit.maximum_attempts == 4
    assert audit.maximum_timeout_seconds == 100


def test_audit_emits_stable_aggregate_findings():
    audit = audit_workflow(
        workflow(enabled=False, continue_on_error=True),
        policy(
            maximum_steps=2,
            maximum_waves=2,
            maximum_attempts=3,
            maximum_timeout_seconds=99,
            allowed_actions=("validate",),
        ),
    )
    assert [(item.code, item.count) for item in audit.findings] == [
        ("WORKFLOW_DISABLED", 1),
        ("STEP_LIMIT_EXCEEDED", 1),
        ("WAVE_LIMIT_EXCEEDED", 1),
        ("ATTEMPT_LIMIT_EXCEEDED", 1),
        ("TIMEOUT_BUDGET_EXCEEDED", 1),
        ("CONTINUE_ON_ERROR_DISALLOWED", 1),
        ("ACTION_NOT_ALLOWED", 2),
    ]
    assert audit.ready is False
    assert audit.finding_count == 8


def test_audit_does_not_modify_workflow_or_plan():
    source = workflow()
    plan = build_execution_plan(source)
    before = (source, plan)
    audit_workflow(source, policy(), plan=plan)
    assert (source, plan) == before


def test_audit_rejects_plan_from_another_workflow():
    source = workflow()
    other = Workflow(
        name="Other",
        description=source.description,
        enabled=True,
        trigger=source.trigger,
        steps=source.steps,
    )
    with pytest.raises(AutoHubError, match="does not belong"):
        audit_workflow(source, policy(), plan=build_execution_plan(other))


def test_audit_validates_inputs():
    with pytest.raises(AutoHubError, match="workflow"):
        audit_workflow(object(), policy())
    with pytest.raises(AutoHubError, match="policy"):
        audit_workflow(workflow(), object())


@pytest.mark.parametrize(("code", "count"), [("", 1), ("CODE", 0), ("CODE", True)])
def test_audit_finding_validates_values(code, count):
    with pytest.raises(AutoHubError):
        AuditFinding(code, count)
