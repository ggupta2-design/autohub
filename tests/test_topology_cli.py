import json

from autohub.cli import run


def workflow_payload():
    return {
        "schema_version": 1,
        "name": "Secret workflow",
        "description": "Private local process",
        "enabled": True,
        "trigger": {"type": "manual", "interval_minutes": None},
        "steps": [
            {
                "id": "private_root",
                "title": "Private root",
                "action": "collect",
                "depends_on": [],
                "timeout_seconds": 30,
                "retries": 0,
                "continue_on_error": False,
            },
            {
                "id": "private_left",
                "title": "Private left",
                "action": "transform",
                "depends_on": ["private_root"],
                "timeout_seconds": 30,
                "retries": 0,
                "continue_on_error": False,
            },
            {
                "id": "private_right",
                "title": "Private right",
                "action": "transform",
                "depends_on": ["private_root"],
                "timeout_seconds": 30,
                "retries": 0,
                "continue_on_error": False,
            },
        ],
    }


def write_workflow(tmp_path):
    path = tmp_path / "workflow.json"
    path.write_text(json.dumps(workflow_payload()), encoding="utf-8")
    return path


def test_topology_command_reports_aggregate_graph_metrics(tmp_path, capsys):
    path = write_workflow(tmp_path)
    assert run(["analyze-topology", str(path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["structure"]["steps"] == 3
    assert payload["structure"]["dependency_depth"] == 2
    assert payload["parallelism"]["maximum_width"] == 2
    assert payload["exposure"]["maximum_downstream_steps"] == 2


def test_redacted_topology_command_omits_operational_values(tmp_path, capsys):
    path = write_workflow(tmp_path)
    assert run(
        ["analyze-topology", str(path), "--json", "--redact-names"]
    ) == 0
    rendered = capsys.readouterr().out
    assert "Secret workflow" not in rendered
    assert "Private local process" not in rendered
    assert "private_root" not in rendered
    assert "Private root" not in rendered


def test_topology_export_is_private_and_non_overwriting(tmp_path, capsys):
    path = write_workflow(tmp_path)
    output = tmp_path / "reports" / "topology.json"
    command = [
        "analyze-topology",
        str(path),
        "--json",
        "--redact-names",
        "--output",
        str(output),
    ]
    assert run(command) == 0
    assert capsys.readouterr().out == "Wrote topology.json\n"
    assert output.exists()
    assert run(command) == 2
    assert "already exists" in capsys.readouterr().err


def test_invalid_topology_input_returns_error(tmp_path, capsys):
    path = tmp_path / "invalid.json"
    path.write_text("{}", encoding="utf-8")
    assert run(["analyze-topology", str(path)]) == 2
    assert "workflow must contain exactly" in capsys.readouterr().err
