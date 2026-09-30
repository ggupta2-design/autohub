import json

from autohub.cli import run


def payload(*, name="Private workflow", timeout=30):
    return {
        "schema_version": 1,
        "name": name,
        "description": "Private local workflow",
        "enabled": True,
        "trigger": {"type": "manual", "interval_minutes": None},
        "steps": [
            {
                "id": "private_collect",
                "title": "Collect private data",
                "action": "collect",
                "depends_on": [],
                "timeout_seconds": timeout,
                "retries": 0,
                "continue_on_error": False,
            },
            {
                "id": "private_export",
                "title": "Export private data",
                "action": "export",
                "depends_on": ["private_collect"],
                "timeout_seconds": 20,
                "retries": 0,
                "continue_on_error": False,
            },
        ],
    }


def write_versions(tmp_path, *, current=None):
    baseline = tmp_path / "baseline.json"
    latest = tmp_path / "current.json"
    baseline.write_text(json.dumps(payload()), encoding="utf-8")
    latest.write_text(json.dumps(current or payload()), encoding="utf-8")
    return baseline, latest


def test_identical_comparison_returns_success(tmp_path, capsys):
    baseline, current = write_versions(tmp_path)
    before = (baseline.read_bytes(), current.read_bytes())
    assert run(["compare", str(baseline), str(current), "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["changed"] is False
    assert report["steps"]["unchanged"] == 2
    assert (baseline.read_bytes(), current.read_bytes()) == before


def test_changed_comparison_returns_attention_status(tmp_path, capsys):
    baseline, current = write_versions(
        tmp_path,
        current=payload(timeout=45),
    )
    assert run(["compare", str(baseline), str(current), "--json"]) == 1
    report = json.loads(capsys.readouterr().out)
    assert report["changed"] is True
    assert report["steps"]["modified"] == 1
    assert report["step_field_changes"] == {"timeout_seconds": 1}
    assert report["plan_deltas"]["maximum_timeout_seconds"] == 15


def test_redacted_comparison_omits_names_and_step_values(tmp_path, capsys):
    baseline, current = write_versions(
        tmp_path,
        current=payload(name="Secret revised workflow", timeout=45),
    )
    assert run(
        [
            "compare",
            str(baseline),
            str(current),
            "--json",
            "--redact-names",
        ]
    ) == 1
    rendered = capsys.readouterr().out
    assert "Private workflow" not in rendered
    assert "Secret revised workflow" not in rendered
    assert "private_collect" not in rendered
    assert "Collect private data" not in rendered


def test_comparison_export_never_overwrites(tmp_path, capsys):
    baseline, current = write_versions(tmp_path)
    output = tmp_path / "reports" / "comparison.json"
    command = [
        "compare",
        str(baseline),
        str(current),
        "--json",
        "--redact-names",
        "--output",
        str(output),
    ]
    assert run(command) == 0
    assert capsys.readouterr().out == "Wrote comparison.json\n"
    assert output.exists()
    assert run(command) == 2
    assert "already exists" in capsys.readouterr().err


def test_invalid_comparison_input_returns_error(tmp_path, capsys):
    baseline, current = write_versions(tmp_path)
    current.write_text("{}", encoding="utf-8")
    assert run(["compare", str(baseline), str(current)]) == 2
    assert "workflow must contain exactly" in capsys.readouterr().err
