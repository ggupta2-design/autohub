import json

from autohub.cli import run


def workflow_payload(*, name, enabled=True, timeout=30):
    return {
        "schema_version": 1,
        "name": name,
        "description": "Private local workflow",
        "enabled": enabled,
        "trigger": {"type": "manual", "interval_minutes": None},
        "steps": [
            {
                "id": "private_collect",
                "title": "Private collect",
                "action": "collect",
                "depends_on": [],
                "timeout_seconds": timeout,
                "retries": 0,
                "continue_on_error": False,
            }
        ],
    }


def policy_payload():
    return {
        "schema_version": 1,
        "name": "Private change policy",
        "require_enabled": True,
        "maximum_steps": 5,
        "maximum_waves": 5,
        "maximum_attempts": 5,
        "maximum_timeout_seconds": 300,
        "allow_continue_on_error": False,
        "allowed_actions": ["collect"],
    }


def write_inputs(tmp_path, *, current_enabled=True, current_timeout=30):
    baseline = tmp_path / "baseline.json"
    current = tmp_path / "current.json"
    policy = tmp_path / "policy.json"
    baseline.write_text(
        json.dumps(workflow_payload(name="Secret baseline")),
        encoding="utf-8",
    )
    current.write_text(
        json.dumps(
            workflow_payload(
                name="Secret current",
                enabled=current_enabled,
                timeout=current_timeout,
            )
        ),
        encoding="utf-8",
    )
    policy.write_text(json.dumps(policy_payload()), encoding="utf-8")
    return baseline, current, policy


def command(baseline, current, policy):
    return [
        "review-change",
        str(baseline),
        str(current),
        "--policy",
        str(policy),
        "--json",
    ]


def test_unchanged_change_review_returns_success(tmp_path, capsys):
    baseline, current, policy = write_inputs(tmp_path)
    current.write_bytes(baseline.read_bytes())
    assert run(command(baseline, current, policy)) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["decision"] == "unchanged"


def test_valid_change_requires_review_status(tmp_path, capsys):
    baseline, current, policy = write_inputs(tmp_path, current_timeout=45)
    assert run(command(baseline, current, policy)) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["decision"] == "review_required"
    assert payload["policy_ready"] is True


def test_policy_violation_returns_blocked_status(tmp_path, capsys):
    baseline, current, policy = write_inputs(tmp_path, current_enabled=False)
    assert run(command(baseline, current, policy)) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["decision"] == "blocked"
    assert payload["policy_findings"] == [
        {"code": "WORKFLOW_DISABLED", "count": 1}
    ]


def test_redacted_change_review_export_is_non_overwriting(tmp_path, capsys):
    baseline, current, policy = write_inputs(tmp_path, current_timeout=45)
    output = tmp_path / "reports" / "review.json"
    args = command(baseline, current, policy) + [
        "--redact-names",
        "--output",
        str(output),
    ]
    assert run(args) == 1
    assert capsys.readouterr().out == "Wrote review.json\n"
    rendered = output.read_text(encoding="utf-8")
    assert "Secret baseline" not in rendered
    assert "Secret current" not in rendered
    assert "Private change policy" not in rendered
    assert run(args) == 2
    assert "already exists" in capsys.readouterr().err


def test_invalid_change_review_input_returns_error(tmp_path, capsys):
    baseline, current, policy = write_inputs(tmp_path)
    current.write_text("{}", encoding="utf-8")
    assert run(command(baseline, current, policy)) == 2
    assert "workflow must contain exactly" in capsys.readouterr().err
