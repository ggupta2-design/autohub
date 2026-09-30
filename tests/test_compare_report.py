import json

from autohub.compare import WorkflowComparison
from autohub.compare_report import (
    format_workflow_comparison,
    workflow_comparison_to_dict,
)


def comparison(*, changed=True):
    return WorkflowComparison(
        baseline_name="Secret baseline workflow",
        current_name="Secret current workflow",
        metadata_changes=("enabled",) if changed else (),
        added_steps=1 if changed else 0,
        removed_steps=0,
        modified_steps=1 if changed else 0,
        unchanged_steps=2,
        step_field_changes=(("timeout_seconds", 1),) if changed else (),
        impacted_steps=3 if changed else 0,
        step_delta=1 if changed else 0,
        wave_delta=1 if changed else 0,
        attempt_delta=2 if changed else 0,
        timeout_delta_seconds=120 if changed else 0,
    )


def test_json_comparison_report_is_stable():
    payload = json.loads(format_workflow_comparison(comparison(), as_json=True))
    assert payload == {
        "baseline": "Secret baseline workflow",
        "changed": True,
        "current": "Secret current workflow",
        "metadata_changes": ["enabled"],
        "plan_deltas": {
            "maximum_attempts": 2,
            "maximum_timeout_seconds": 120,
            "steps": 1,
            "waves": 1,
        },
        "report": "workflow_comparison",
        "schema": 1,
        "step_field_changes": {"timeout_seconds": 1},
        "steps": {
            "added": 1,
            "impacted": 3,
            "modified": 1,
            "removed": 0,
            "unchanged": 2,
        },
    }


def test_redacted_comparison_omits_names_and_step_values():
    rendered = format_workflow_comparison(
        comparison(),
        as_json=True,
        redact_names=True,
    )
    assert "Secret baseline workflow" not in rendered
    assert "Secret current workflow" not in rendered
    assert "[redacted]" in rendered
    assert "step_identifier" not in rendered
    assert "step title" not in rendered


def test_text_report_contains_aggregate_deltas():
    rendered = format_workflow_comparison(comparison())
    assert "Changed: yes" in rendered
    assert "added=1" in rendered
    assert "impacted=3" in rendered
    assert "attempts=+2" in rendered
    assert "timeout_seconds=+120" in rendered
    assert "Metadata fields changed: enabled" in rendered
    assert "timeout_seconds: 1" in rendered


def test_unchanged_report_omits_empty_change_sections():
    rendered = format_workflow_comparison(comparison(changed=False))
    assert "Changed: no" in rendered
    assert "Metadata fields changed:" not in rendered
    assert "Step field changes:" not in rendered


def test_dictionary_report_preserves_signed_decreases():
    value = comparison()
    decreased = WorkflowComparison(
        baseline_name=value.baseline_name,
        current_name=value.current_name,
        metadata_changes=(),
        added_steps=0,
        removed_steps=1,
        modified_steps=0,
        unchanged_steps=2,
        step_field_changes=(),
        impacted_steps=1,
        step_delta=-1,
        wave_delta=-1,
        attempt_delta=-2,
        timeout_delta_seconds=-120,
    )
    payload = workflow_comparison_to_dict(decreased, redact_names=True)
    assert payload["plan_deltas"]["steps"] == -1
    assert payload["plan_deltas"]["maximum_timeout_seconds"] == -120
