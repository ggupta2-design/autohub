from autohub.models import Trigger, Workflow, WorkflowStep
from autohub.policy import GuardrailPolicy
from autohub.review import review_workflow_change


def workflow(*, enabled=True, timeout=30, retries=0, continue_on_error=False):
    return Workflow(
        name="Private workflow",
        description="Private description",
        enabled=enabled,
        trigger=Trigger("manual"),
        steps=(
            WorkflowStep(
                "collect",
                "Private collect",
                "collect",
                timeout_seconds=timeout,
                retries=retries,
                continue_on_error=continue_on_error,
            ),
        ),
    )


def policy():
    return GuardrailPolicy(
        name="Private policy",
        require_enabled=True,
        maximum_steps=5,
        maximum_waves=5,
        maximum_attempts=1,
        maximum_timeout_seconds=30,
        allow_continue_on_error=False,
        allowed_actions=("validate",),
    )


def test_change_review_preserves_stable_policy_finding_order():
    baseline = workflow()
    current = workflow(
        enabled=False,
        timeout=31,
        retries=1,
        continue_on_error=True,
    )
    review = review_workflow_change(baseline, current, policy())
    assert review.decision == "blocked"
    assert review.finding_count == 5
    assert [(item.code, item.count) for item in review.policy_findings] == [
        ("WORKFLOW_DISABLED", 1),
        ("ATTEMPT_LIMIT_EXCEEDED", 1),
        ("TIMEOUT_BUDGET_EXCEEDED", 1),
        ("CONTINUE_ON_ERROR_DISALLOWED", 1),
        ("ACTION_NOT_ALLOWED", 1),
    ]


def test_policy_boundary_is_inclusive_for_current_version():
    source = workflow(timeout=30)
    review = review_workflow_change(source, source, policy())
    assert review.current_audit.maximum_timeout_seconds == 30
    assert "TIMEOUT_BUDGET_EXCEEDED" not in {
        item.code for item in review.policy_findings
    }


def test_review_keeps_comparison_aggregate_and_value_free():
    review = review_workflow_change(
        workflow(timeout=30),
        workflow(timeout=31, retries=1),
        policy(),
    )
    assert review.comparison.modified_steps == 1
    assert review.comparison.step_field_changes == (
        ("timeout_seconds", 1),
        ("retries", 1),
    )
    rendered = repr(review.comparison.step_field_changes)
    assert "Private collect" not in rendered
    assert "collect" not in rendered
