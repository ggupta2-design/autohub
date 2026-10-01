import json

from autohub.policy import GuardrailPolicy
from autohub.portfolio import audit_workflow_folder


def policy():
    return GuardrailPolicy(
        name="Private portfolio policy",
        require_enabled=True,
        maximum_steps=1,
        maximum_waves=10,
        maximum_attempts=10,
        maximum_timeout_seconds=1000,
        allow_continue_on_error=False,
        allowed_actions=("collect", "validate", "transform", "export"),
    )


def workflow_payload(*, name, enabled=True, steps=1):
    entries = [
        {
            "id": "collect",
            "title": "Collect",
            "action": "collect",
            "depends_on": [],
            "timeout_seconds": 30,
            "retries": 0,
            "continue_on_error": False,
        }
    ]
    if steps == 2:
        entries.append(
            {
                "id": "export",
                "title": "Export",
                "action": "export",
                "depends_on": ["collect"],
                "timeout_seconds": 30,
                "retries": 0,
                "continue_on_error": False,
            }
        )
    return {
        "schema_version": 1,
        "name": name,
        "description": "Fictional local workflow",
        "enabled": enabled,
        "trigger": {"type": "manual", "interval_minutes": None},
        "steps": entries,
    }


def write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_portfolio_audit_isolates_invalid_files_and_aggregates_findings(tmp_path):
    write_json(
        tmp_path / "ready.json",
        workflow_payload(name="Secret ready"),
    )
    write_json(
        tmp_path / "blocked.json",
        workflow_payload(name="Secret blocked", enabled=False, steps=2),
    )
    (tmp_path / "invalid.json").write_text("{broken", encoding="utf-8")

    result = audit_workflow_folder(tmp_path, policy())
    assert result.discovered_files == 3
    assert result.audited_workflows == 2
    assert result.ready_workflows == 1
    assert result.blocked_workflows == 1
    assert result.invalid_files == 1
    assert result.review_required is True
    assert result.finding_count == 2
    assert [(finding.code, finding.count) for finding in result.findings] == [
        ("STEP_LIMIT_EXCEEDED", 1),
        ("WORKFLOW_DISABLED", 1),
    ]


def test_portfolio_audit_handles_empty_folder(tmp_path):
    result = audit_workflow_folder(tmp_path, policy())
    assert result.discovered_files == 0
    assert result.audited_workflows == 0
    assert result.review_required is False
    assert result.findings == ()


def test_portfolio_audit_does_not_modify_source_files(tmp_path):
    path = tmp_path / "workflow.json"
    write_json(path, workflow_payload(name="Private source"))
    before = path.read_bytes()
    audit_workflow_folder(tmp_path, policy())
    assert path.read_bytes() == before


def test_recursive_audit_respects_discovery_mode(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    write_json(nested / "workflow.json", workflow_payload(name="Nested"))

    shallow = audit_workflow_folder(tmp_path, policy())
    recursive = audit_workflow_folder(tmp_path, policy(), recursive=True)
    assert shallow.discovered_files == 0
    assert recursive.discovered_files == 1
    assert recursive.ready_workflows == 1


def test_portfolio_result_contains_no_workflow_or_file_names(tmp_path):
    write_json(
        tmp_path / "confidential-name.json",
        workflow_payload(name="Confidential workflow"),
    )
    result = audit_workflow_folder(tmp_path, policy())
    rendered = repr(result)
    assert "confidential-name.json" not in rendered
    assert "Confidential workflow" not in rendered
