"""Strict local guardrail policies for workflow preflight audits."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import ActionType, AutoHubError, _text


MAX_POLICY_BYTES = 64 * 1024
_POLICY_FIELDS = {
    "schema_version",
    "name",
    "require_enabled",
    "maximum_steps",
    "maximum_waves",
    "maximum_attempts",
    "maximum_timeout_seconds",
    "allow_continue_on_error",
    "allowed_actions",
}


def _bounded_integer(value: Any, field: str, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
        raise AutoHubError(f"{field} must be an integer from 1 to {maximum}")
    return value


@dataclass(frozen=True, slots=True)
class GuardrailPolicy:
    """Bounded, reusable constraints for a workflow execution plan."""

    name: str
    require_enabled: bool
    maximum_steps: int
    maximum_waves: int
    maximum_attempts: int
    maximum_timeout_seconds: int
    allow_continue_on_error: bool
    allowed_actions: tuple[ActionType, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _text(self.name, "policy name", maximum=100))
        if not isinstance(self.require_enabled, bool):
            raise AutoHubError("require_enabled must be true or false")
        object.__setattr__(
            self, "maximum_steps", _bounded_integer(self.maximum_steps, "maximum_steps", 100)
        )
        object.__setattr__(
            self, "maximum_waves", _bounded_integer(self.maximum_waves, "maximum_waves", 100)
        )
        object.__setattr__(
            self,
            "maximum_attempts",
            _bounded_integer(self.maximum_attempts, "maximum_attempts", 600),
        )
        object.__setattr__(
            self,
            "maximum_timeout_seconds",
            _bounded_integer(
                self.maximum_timeout_seconds, "maximum_timeout_seconds", 2_160_000
            ),
        )
        if not isinstance(self.allow_continue_on_error, bool):
            raise AutoHubError("allow_continue_on_error must be true or false")
        if not isinstance(self.allowed_actions, tuple) or not self.allowed_actions:
            raise AutoHubError("allowed_actions must contain at least one action")
        actions: list[ActionType] = []
        for action in self.allowed_actions:
            try:
                actions.append(action if isinstance(action, ActionType) else ActionType(action))
            except (TypeError, ValueError) as exc:
                raise AutoHubError("allowed_actions contains an unsupported action") from exc
        if len(actions) != len(set(actions)):
            raise AutoHubError("allowed_actions cannot contain duplicates")
        object.__setattr__(self, "allowed_actions", tuple(actions))


def policy_from_dict(payload: Any) -> GuardrailPolicy:
    """Build a validated guardrail policy from a strict versioned object."""

    if not isinstance(payload, dict) or set(payload) != _POLICY_FIELDS:
        raise AutoHubError("policy must contain exactly the supported fields")
    if payload["schema_version"] != 1:
        raise AutoHubError(
            f"unsupported policy schema_version: {payload['schema_version']}"
        )
    actions = payload["allowed_actions"]
    if not isinstance(actions, list):
        raise AutoHubError("allowed_actions must be a list")
    return GuardrailPolicy(
        name=payload["name"],
        require_enabled=payload["require_enabled"],
        maximum_steps=payload["maximum_steps"],
        maximum_waves=payload["maximum_waves"],
        maximum_attempts=payload["maximum_attempts"],
        maximum_timeout_seconds=payload["maximum_timeout_seconds"],
        allow_continue_on_error=payload["allow_continue_on_error"],
        allowed_actions=tuple(actions),
    )


def load_policy(path: str | Path) -> GuardrailPolicy:
    """Load a bounded UTF-8 policy without following symbolic links."""

    source = Path(path)
    if source.is_symlink():
        raise AutoHubError("policy cannot be a symbolic link")
    if not source.exists():
        raise AutoHubError("policy file does not exist")
    if not source.is_file():
        raise AutoHubError("policy path is not a file")
    try:
        size = source.stat().st_size
    except OSError as exc:
        raise AutoHubError("could not inspect policy file") from exc
    if size > MAX_POLICY_BYTES:
        raise AutoHubError(f"policy file cannot exceed {MAX_POLICY_BYTES} bytes")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise AutoHubError("policy is not valid UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise AutoHubError(f"policy is not valid JSON at line {exc.lineno}") from exc
    except OSError as exc:
        raise AutoHubError("could not read policy file") from exc
    return policy_from_dict(payload)
