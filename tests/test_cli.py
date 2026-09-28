import json

from autohub.cli import run


def write_workflow(tmp_path, *, enabled=True):
    payload = {
        "schema_version": 1,
        "name": "Confidential automation",
        "description": "Private local workflow",
        "enabled": enabled,
        "trigger": {"type": "manual", "interval_minutes": None},
        "steps": [
            {
                "id": "private_collect",
                "title": "Collect private data",
                "action": "collect",
                "depends_on": [],
                "timeout_seconds": 30,
                "retries": 0,
                "continue_on_error": False,
            },
            {
                "id": "private_export",
                "title": "Export private data",
                "action": "export",
                "depends_on": ["private_collect"],
                "timeout_seconds": 30,
                "retries": 1,
                "continue_on_error": False,
            },
        ],
    }
    path = tmp_path / "workflow.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_validate_command_reports_structure(tmp_path, capsys):
    source = write_workflow(tmp_path)
    assert run(["validate", str(source), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload == {
        "enabled": True,
        "steps": 2,
        "trigger": "manual",
        "valid": True,
        "waves": 2,
    }


def test_plan_command_redacts_names_without_execution(tmp_path, capsys):
    source = write_workflow(tmp_path)
    before = source.read_bytes()
    assert run(
        ["plan", str(source), "--json", "--redact-names"]
    ) == 0
    rendered = capsys.readouterr().out
    assert "Confidential automation" not in rendered
    assert "private_collect" not in rendered
    assert "private_export" not in rendered
    assert json.loads(rendered)["summary"]["steps"] == 2
    assert source.read_bytes() == before


def test_disabled_plan_uses_attention_status(tmp_path, capsys):
    source = write_workflow(tmp_path, enabled=False)
    assert run(["plan", str(source), "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["enabled"] is False


def test_plan_export_never_overwrites(tmp_path, capsys):
    source = write_workflow(tmp_path)
    output = tmp_path / "private" / "plan.json"
    command = ["plan", str(source), "--json", "--output", str(output)]

    assert run(command) == 0
    assert capsys.readouterr().out == "Wrote plan.json\n"
    assert output.exists()
    assert run(command) == 2
    assert "already exists" in capsys.readouterr().err


def test_invalid_cycle_returns_error_status(tmp_path, capsys):
    source = write_workflow(tmp_path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["steps"][0]["depends_on"] = ["private_export"]
    source.write_text(json.dumps(payload), encoding="utf-8")

    assert run(["plan", str(source)]) == 2
    assert "dependency cycle" in capsys.readouterr().err
