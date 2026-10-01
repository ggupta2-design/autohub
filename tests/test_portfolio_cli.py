import json

from autohub.cli import run


def workflow_payload(*, enabled=True):
    return {
        "schema_version": 1,
        "name": "Private workflow",
        "description": "Fictional local workflow",
        "enabled": enabled,
        "trigger": {"type": "manual", "interval_minutes": None},
        "steps": [
            {
                "id": "collect",
                "title": "Collect",
                "action": "collect",
                "depends_on": [],
                "timeout_seconds": 30,
                "retries": 0,
                "continue_on_error": False,
            }
        ],
    }


def policy_payload():
    return {
        "schema_version": 1,
        "name": "Private portfolio policy",
        "require_enabled": True,
        "maximum_steps": 5,
        "maximum_waves": 5,
        "maximum_attempts": 5,
        "maximum_timeout_seconds": 300,
        "allow_continue_on_error": False,
        "allowed_actions": ["collect", "validate", "transform", "export"],
    }


def write_inputs(tmp_path):
    root = tmp_path / "workflows"
    root.mkdir()
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps(policy_payload()), encoding="utf-8")
    return root, policy


def test_ready_folder_audit_returns_success(tmp_path, capsys):
    root, policy = write_inputs(tmp_path)
    (root / "ready.json").write_text(
        json.dumps(workflow_payload()), encoding="utf-8"
    )
    assert run(["audit-folder", str(root), "--policy", str(policy), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["decision"] == "ready"
    assert payload["summary"]["ready_workflows"] == 1


def test_folder_audit_isolates_invalid_and_blocked_files(tmp_path, capsys):
    root, policy = write_inputs(tmp_path)
    (root / "blocked.json").write_text(
        json.dumps(workflow_payload(enabled=False)), encoding="utf-8"
    )
    (root / "private-invalid.json").write_text("{broken", encoding="utf-8")
    assert run(["audit-folder", str(root), "--policy", str(policy), "--json"]) == 1
    output = capsys.readouterr().out
    payload = json.loads(output)
    assert payload["summary"]["blocked_workflows"] == 1
    assert payload["summary"]["invalid_files"] == 1
    assert payload["findings"] == [{"code": "WORKFLOW_DISABLED", "count": 1}]
    assert "private-invalid.json" not in output


def test_recursive_folder_audit_and_file_limit(tmp_path, capsys):
    root, policy = write_inputs(tmp_path)
    nested = root / "nested"
    nested.mkdir()
    (nested / "workflow.json").write_text(
        json.dumps(workflow_payload()), encoding="utf-8"
    )
    command = [
        "audit-folder",
        str(root),
        "--policy",
        str(policy),
        "--recursive",
        "--max-files",
        "1",
        "--json",
    ]
    assert run(command) == 0
    assert json.loads(capsys.readouterr().out)["summary"]["discovered_files"] == 1
    (root / "second.json").write_text(
        json.dumps(workflow_payload()), encoding="utf-8"
    )
    assert run(command) == 2
    assert "more than 1 workflow files" in capsys.readouterr().err


def test_redacted_folder_export_is_private_and_non_overwriting(tmp_path, capsys):
    root, policy = write_inputs(tmp_path)
    (root / "secret-project.json").write_text(
        json.dumps(workflow_payload()), encoding="utf-8"
    )
    output = tmp_path / "reports" / "portfolio.json"
    command = [
        "audit-folder",
        str(root),
        "--policy",
        str(policy),
        "--json",
        "--redact-names",
        "--output",
        str(output),
    ]
    assert run(command) == 0
    assert capsys.readouterr().out == "Wrote portfolio.json\n"
    rendered = output.read_text(encoding="utf-8")
    assert "Private portfolio policy" not in rendered
    assert "Private workflow" not in rendered
    assert "secret-project.json" not in rendered
    assert run(command) == 2
    assert "already exists" in capsys.readouterr().err


def test_invalid_folder_policy_returns_error(tmp_path, capsys):
    root, policy = write_inputs(tmp_path)
    policy.write_text("{}", encoding="utf-8")
    assert run(["audit-folder", str(root), "--policy", str(policy)]) == 2
    assert "policy must contain exactly" in capsys.readouterr().err
