import json

from autohub.cli import run


def write_inputs(tmp_path, *, maximum_steps=5, workflow_name="Private workflow"):
    workflow = {
        "schema_version": 1,
        "name": workflow_name,
        "description": "Local test workflow",
        "enabled": True,
        "trigger": {"type": "manual", "interval_minutes": None},
        "steps": [
            {
                "id": "private_collect",
                "title": "Collect private values",
                "action": "collect",
                "depends_on": [],
                "timeout_seconds": 30,
                "retries": 0,
                "continue_on_error": False,
            },
            {
                "id": "private_export",
                "title": "Export private values",
                "action": "export",
                "depends_on": ["private_collect"],
                "timeout_seconds": 30,
                "retries": 0,
                "continue_on_error": False,
            },
        ],
    }
    policy = {
        "schema_version": 1,
        "name": "Private policy",
        "require_enabled": True,
        "maximum_steps": maximum_steps,
        "maximum_waves": 5,
        "maximum_attempts": 5,
        "maximum_timeout_seconds": 300,
        "allow_continue_on_error": False,
        "allowed_actions": ["collect", "validate", "transform", "export"],
    }
    workflow_path = tmp_path / "workflow.json"
    policy_path = tmp_path / "policy.json"
    workflow_path.write_text(json.dumps(workflow), encoding="utf-8")
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    return workflow_path, policy_path


def test_validate_policy_command_reports_bounds(tmp_path, capsys):
    _, policy = write_inputs(tmp_path)
    assert run(["validate-policy", str(policy), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["valid"] is True
    assert payload["maximum_steps"] == 5
    assert payload["allowed_actions"] == [
        "collect",
        "validate",
        "transform",
        "export",
    ]


def test_ready_audit_returns_success_without_modifying_inputs(tmp_path, capsys):
    workflow, policy = write_inputs(tmp_path)
    before = (workflow.read_bytes(), policy.read_bytes())
    assert run(["audit", str(workflow), "--policy", str(policy), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["decision"] == "ready"
    assert payload["findings"] == []
    assert (workflow.read_bytes(), policy.read_bytes()) == before


def test_blocked_audit_returns_attention_status(tmp_path, capsys):
    workflow, policy = write_inputs(tmp_path, maximum_steps=1)
    assert run(["audit", str(workflow), "--policy", str(policy), "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["decision"] == "blocked"
    assert payload["findings"] == [{"code": "STEP_LIMIT_EXCEEDED", "count": 1}]


def test_redacted_audit_omits_names_and_step_values(tmp_path, capsys):
    workflow, policy = write_inputs(tmp_path, workflow_name="Secret operation")
    assert run(
        [
            "audit",
            str(workflow),
            "--policy",
            str(policy),
            "--json",
            "--redact-names",
        ]
    ) == 0
    rendered = capsys.readouterr().out
    assert "Secret operation" not in rendered
    assert "Private policy" not in rendered
    assert "private_collect" not in rendered
    assert "Collect private values" not in rendered


def test_audit_export_is_private_and_non_overwriting(tmp_path, capsys):
    workflow, policy = write_inputs(tmp_path)
    output = tmp_path / "reports" / "audit.json"
    command = [
        "audit",
        str(workflow),
        "--policy",
        str(policy),
        "--json",
        "--redact-names",
        "--output",
        str(output),
    ]
    assert run(command) == 0
    assert capsys.readouterr().out == "Wrote audit.json\n"
    assert output.exists()
    assert run(command) == 2
    assert "already exists" in capsys.readouterr().err


def test_invalid_policy_returns_error_without_audit(tmp_path, capsys):
    workflow, policy = write_inputs(tmp_path)
    policy.write_text("{}", encoding="utf-8")
    assert run(["audit", str(workflow), "--policy", str(policy)]) == 2
    assert "policy must contain exactly" in capsys.readouterr().err
