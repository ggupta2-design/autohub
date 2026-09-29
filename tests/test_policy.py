import json

import pytest

from autohub.models import ActionType, AutoHubError
from autohub.policy import GuardrailPolicy, MAX_POLICY_BYTES, load_policy, policy_from_dict


def policy_payload():
    return {
        "schema_version": 1,
        "name": "Conservative local policy",
        "require_enabled": True,
        "maximum_steps": 20,
        "maximum_waves": 10,
        "maximum_attempts": 30,
        "maximum_timeout_seconds": 7200,
        "allow_continue_on_error": False,
        "allowed_actions": ["collect", "validate", "transform", "export"],
    }


def test_policy_normalizes_actions_and_name():
    payload = policy_payload()
    payload["name"] = "  Conservative   local policy "
    policy = policy_from_dict(payload)
    assert policy.name == "Conservative local policy"
    assert policy.allowed_actions == tuple(ActionType)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("maximum_steps", 0),
        ("maximum_steps", 101),
        ("maximum_waves", True),
        ("maximum_attempts", 601),
        ("maximum_timeout_seconds", 2_160_001),
    ],
)
def test_policy_rejects_out_of_bounds_integers(field, value):
    payload = policy_payload()
    payload[field] = value
    with pytest.raises(AutoHubError, match=field):
        policy_from_dict(payload)


def test_policy_rejects_unknown_or_missing_fields():
    payload = policy_payload()
    payload["secret"] = "not supported"
    with pytest.raises(AutoHubError, match="exactly"):
        policy_from_dict(payload)
    payload = policy_payload()
    del payload["maximum_waves"]
    with pytest.raises(AutoHubError, match="exactly"):
        policy_from_dict(payload)


@pytest.mark.parametrize("actions", [[], ["collect", "collect"], ["execute"]])
def test_policy_rejects_invalid_action_sets(actions):
    payload = policy_payload()
    payload["allowed_actions"] = actions
    with pytest.raises(AutoHubError, match="allowed_actions"):
        policy_from_dict(payload)


def test_load_policy_reads_valid_local_json(tmp_path):
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(policy_payload()), encoding="utf-8")
    assert load_policy(path).maximum_attempts == 30


def test_load_policy_rejects_symlink_and_oversized_file(tmp_path):
    target = tmp_path / "target.json"
    target.write_text(json.dumps(policy_payload()), encoding="utf-8")
    link = tmp_path / "linked.json"
    link.symlink_to(target)
    with pytest.raises(AutoHubError, match="symbolic link"):
        load_policy(link)

    oversized = tmp_path / "oversized.json"
    oversized.write_bytes(b" " * (MAX_POLICY_BYTES + 1))
    with pytest.raises(AutoHubError, match="cannot exceed"):
        load_policy(oversized)


def test_policy_requires_boolean_flags():
    for field in ("require_enabled", "allow_continue_on_error"):
        payload = policy_payload()
        payload[field] = 1
        with pytest.raises(AutoHubError, match=field):
            policy_from_dict(payload)


def test_policy_dataclass_rejects_non_tuple_actions():
    with pytest.raises(AutoHubError, match="allowed_actions"):
        GuardrailPolicy(
            name="Policy",
            require_enabled=True,
            maximum_steps=1,
            maximum_waves=1,
            maximum_attempts=1,
            maximum_timeout_seconds=1,
            allow_continue_on_error=False,
            allowed_actions=["collect"],
        )
