import json

from autohub.models import Trigger, Workflow, WorkflowStep
from autohub.policy import GuardrailPolicy
from autohub.review import review_workflow_change
from autohub.review_report import change_review_to_dict, format_change_review


def workflow(*, name, enabled=True, timeout=30):
    return Workflow(
        name=name,
        description="Private description",
        enabled=enabled,
        trigger=Trigger("manual"),
        steps=(
            WorkflowStep(
                "private_collect",
                "Private collect title",
                "collect",
                timeout_seconds=timeout,
            ),
        ),
    )


def policy():
    return GuardrailPolicy(
        name="Private change policy",
        require_enabled=True,
        maximum_steps=5,
        maximum_waves=5,
        maximum_attempts=5,
        maximum_timeout_seconds=300,
        allow_continue_on_error=False,
        allowed_actions=("collect",),
    )


def review(*, enabled=True, timeout=45):
    return review_workflow_change(
        workflow(name="Secret baseline", timeout=30),
        workflow(name="Secret current", enabled=enabled, timeout=timeout),
        policy(),
    )


def test_change_review_json_contains_combined_aggregate_evidence():
    payload = json.loads(format_change_review(review(), as_json=True))
    assert payload["schema"] == 1
    assert payload["report"] == "workflow_change_review"
    assert payload["decision"] == "review_required"
    assert payload["changed"] is True
    assert payload["policy_ready"] is True
    assert payload["changes"]["steps"]["modified"] == 1
    assert payload["changes"]["plan_deltas"]["maximum_timeout_seconds"] == 15
    assert payload["policy_findings"] == []


def test_redacted_change_review_omits_operational_names_and_values():
    rendered = format_change_review(
        review(enabled=False),
        as_json=True,
        redact_names=True,
    )
    assert "Secret baseline" not in rendered
    assert "Secret current" not in rendered
    assert "Private change policy" not in rendered
    assert "private_collect" not in rendered
    assert "Private collect title" not in rendered
    assert "Private description" not in rendered
    payload = json.loads(rendered)
    assert payload["baseline"] == "[redacted]"
    assert payload["current"] == "[redacted]"
    assert payload["policy"] == "[redacted]"


def test_blocked_text_report_contains_stable_findings():
    rendered = format_change_review(review(enabled=False))
    assert "Decision: blocked" in rendered
    assert "Policy ready: no" in rendered
    assert "WORKFLOW_DISABLED: 1" in rendered


def test_unchanged_text_report_is_deterministic():
    source = workflow(name="Same")
    result = review_workflow_change(source, source, policy())
    first = format_change_review(result)
    second = format_change_review(result)
    assert first == second
    assert "Decision: unchanged" in first
    assert "Changed: no" in first


def test_change_review_dictionary_has_no_step_identity_fields():
    payload = change_review_to_dict(review(), redact_names=True)
    rendered = json.dumps(payload, sort_keys=True)
    assert "step_id" not in rendered
    assert "title" not in rendered
    assert "description" not in rendered
    assert "depends_on" not in rendered
