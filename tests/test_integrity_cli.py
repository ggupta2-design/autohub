import json

from autohub.cli import run


def workflow_payload(*, with_findings=False):
    first_title = "Review records"
    second_title = "review records" if with_findings else "Publish summary"
    second_dependencies = [] if with_findings else ["first"]
    return {
        "schema_version": 1,
        "name": "Secret workflow",
        "description": "Private integrity test",
        "enabled": True,
        "trigger": {"type": "manual", "interval_minutes": None},
        "steps": [
            {
                "id": "first",
                "title": first_title,
                "action": "collect",
                "depends_on": [],
                "timeout_seconds": 30,
                "retries": 0,
                "continue_on_error": False,
            },
            {
                "id": "second",
                "title": second_title,
                "action": "export",
                "depends_on": second_dependencies,
                "timeout_seconds": 30,
                "retries": 0,
                "continue_on_error": False,
            },
        ],
    }


def write_workflow(tmp_path, *, with_findings=False):
    path = tmp_path / "workflow.json"
    path.write_text(
        json.dumps(workflow_payload(with_findings=with_findings)),
        encoding="utf-8",
    )
    return path


def test_clean_integrity_audit_returns_success(tmp_path, capsys):
    path = write_workflow(tmp_path)
    assert run(["audit-integrity", str(path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["decision"] == "clean"
    assert payload["summary"]["finding_count"] == 0


def test_integrity_findings_return_review_status_and_aggregates(tmp_path, capsys):
    path = write_workflow(tmp_path, with_findings=True)
    assert run(
        ["audit-integrity", str(path), "--json", "--redact-names"]
    ) == 1
    rendered = capsys.readouterr().out
    payload = json.loads(rendered)
    assert payload["decision"] == "review_required"
    assert payload["summary"]["finding_count"] == 2
    assert [item["code"] for item in payload["findings"]] == [
        "DUPLICATE_STEP_TITLE",
        "DISCONNECTED_COMPONENT",
    ]
    assert "Secret workflow" not in rendered
    assert "Review records" not in rendered
    assert '"first"' not in rendered


def test_integrity_export_is_private_and_non_overwriting(tmp_path, capsys):
    path = write_workflow(tmp_path)
    output = tmp_path / "reports" / "integrity.json"
    command = [
        "audit-integrity",
        str(path),
        "--json",
        "--redact-names",
        "--output",
        str(output),
    ]
    assert run(command) == 0
    assert capsys.readouterr().out == "Wrote integrity.json\n"
    assert output.exists()
    assert run(command) == 2
    assert "already exists" in capsys.readouterr().err


def test_invalid_integrity_input_returns_error(tmp_path, capsys):
    path = tmp_path / "invalid.json"
    path.write_text("{}", encoding="utf-8")
    assert run(["audit-integrity", str(path)]) == 2
    assert "workflow must contain exactly" in capsys.readouterr().err
