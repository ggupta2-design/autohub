import json

import pytest

from autohub.loader import MAX_WORKFLOW_BYTES, load_workflow, workflow_from_dict
from autohub.models import AutoHubError, TriggerType


def payload():
    return {
        "schema_version": 1,
        "name": "Daily review",
        "description": "Review local data",
        "enabled": True,
        "trigger": {"type": "interval", "interval_minutes": 60},
        "steps": [
            {
                "id": "collect",
                "title": "Collect inputs",
                "action": "collect",
                "depends_on": [],
                "timeout_seconds": 30,
                "retries": 1,
                "continue_on_error": False,
            }
        ],
    }


def test_workflow_from_dict_loads_strict_manifest():
    workflow = workflow_from_dict(payload())
    assert workflow.name == "Daily review"
    assert workflow.trigger.type is TriggerType.INTERVAL
    assert workflow.steps[0].maximum_attempts if False else workflow.steps[0].retries == 1


@pytest.mark.parametrize(
    "mutate",
    [
        lambda value: value.update(extra=True),
        lambda value: value.update(schema_version=2),
        lambda value: value["trigger"].update(extra=True),
        lambda value: value["steps"][0].update(extra=True),
        lambda value: value.update(steps="not-a-list"),
    ],
)
def test_loader_rejects_unknown_versions_fields_and_shapes(mutate):
    value = payload()
    mutate(value)
    with pytest.raises(AutoHubError):
        workflow_from_dict(value)


def test_load_workflow_rejects_missing_invalid_and_oversized_files(tmp_path):
    with pytest.raises(AutoHubError):
        load_workflow(tmp_path / "missing.json")

    invalid = tmp_path / "invalid.json"
    invalid.write_text("{", encoding="utf-8")
    with pytest.raises(AutoHubError):
        load_workflow(invalid)

    oversized = tmp_path / "oversized.json"
    oversized.write_bytes(b" " * (MAX_WORKFLOW_BYTES + 1))
    with pytest.raises(AutoHubError):
        load_workflow(oversized)


def test_load_workflow_rejects_symbolic_links(tmp_path):
    source = tmp_path / "workflow.json"
    source.write_text(json.dumps(payload()), encoding="utf-8")
    linked = tmp_path / "linked.json"
    linked.symlink_to(source)
    with pytest.raises(AutoHubError):
        load_workflow(linked)
