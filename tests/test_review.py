import pytest

from autohub.audit import PreflightAudit
from autohub.compare import WorkflowComparison
from autohub.models import AutoHubError, Trigger, Workflow, WorkflowStep
from autohub.policy import GuardrailPolicy
from autohub.review import ChangeReview, review_workflow_change


def workflow(*, name="Private workflow", enabled=True, timeout=30):
    return Workflow(
        name=name,
        description="Local automation",
        enabled=enabled,
        trigger=Trigger("manual"),
        steps=(
            WorkflowStep(
                "collect",
                "Collect",
                "collect",
                timeout_seconds=timeout,
            ),
        ),
    )


def policy(*, require_enabled=True, maximum_timeout_seconds=300):
    return GuardrailPolicy(
        name="Private policy",
        require_enabled=require_enabled,
        maximum_steps=5,
        maximum_waves=5,
        maximum_attempts=5,
        maximum_timeout_seconds=maximum_timeout_seconds,
        allow_continue_on_error=False,
        allowed_actions=("collect", "validate", "transform", "export"),
    )


def test_unchanged_policy_ready_workflow_needs_no_review():
    source = workflow()
    review = review_workflow_change(source, source, policy())
    assert review.decision == "unchanged"
    assert review.changed is False
    assert review.policy_ready is True
    assert review.finding_count == 0


def test_valid_change_requires_human_review():
    review = review_workflow_change(
        workflow(timeout=30),
        workflow(timeout=45),
        policy(),
    )
    assert review.decision == "review_required"
    assert review.changed is True
    assert review.policy_ready is True
    assert review.comparison.timeout_delta_seconds == 15


def test_policy_violation_blocks_changed_workflow():
    review = review_workflow_change(
        workflow(enabled=True),
        workflow(enabled=False),
        policy(),
    )
    assert review.decision == "blocked"
    assert review.changed is True
    assert review.policy_ready is False
    assert [finding.code for finding in review.policy_findings] == [
        "WORKFLOW_DISABLED"
    ]


def test_policy_violation_blocks_unchanged_workflow():
    source = workflow(enabled=False)
    review = review_workflow_change(source, source, policy())
    assert review.decision == "blocked"
    assert review.changed is False


def test_change_review_does_not_modify_inputs():
    baseline = workflow(timeout=30)
    current = workflow(timeout=45)
    guardrail = policy()
    before = (baseline, current, guardrail)
    review_workflow_change(baseline, current, guardrail)
    assert (baseline, current, guardrail) == before


def test_change_review_rejects_mismatched_audit():
    comparison = WorkflowComparison(
        baseline_name="Baseline",
        current_name="Current",
        metadata_changes=(),
        added_steps=0,
        removed_steps=0,
        modified_steps=0,
        unchanged_steps=1,
        step_field_changes=(),
        impacted_steps=0,
        step_delta=0,
        wave_delta=0,
        attempt_delta=0,
        timeout_delta_seconds=0,
    )
    audit = PreflightAudit(
        workflow_name="Different",
        policy_name="Policy",
        step_count=1,
        wave_count=1,
        maximum_attempts=1,
        maximum_timeout_seconds=30,
        findings=(),
    )
    with pytest.raises(AutoHubError, match="current workflow"):
        ChangeReview(comparison=comparison, current_audit=audit)
