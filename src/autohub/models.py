"""Validated AutoHub workflow domain models."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


class AutoHubError(ValueError):
    """Safe, user-facing AutoHub failure."""


_STEP_ID = re.compile(r"^[a-z][a-z0-9_-]{0,49}$")


def _text(value: Any, field: str, *, maximum: int) -> str:
    if not isinstance(value, str):
        raise AutoHubError(f"{field} must be text")
    cleaned = " ".join(value.split())
    if not cleaned:
        raise AutoHubError(f"{field} cannot be blank")
    if len(cleaned) > maximum:
        raise AutoHubError(f"{field} cannot exceed {maximum} characters")
    if any(ord(character) < 32 for character in cleaned):
        raise AutoHubError(f"{field} cannot contain control characters")
    return cleaned


class ActionType(str, Enum):
    COLLECT = "collect"
    VALIDATE = "validate"
    TRANSFORM = "transform"
    EXPORT = "export"


class TriggerType(str, Enum):
    MANUAL = "manual"
    INTERVAL = "interval"


@dataclass(frozen=True, slots=True)
class Trigger:
    type: TriggerType
    interval_minutes: int | None = None

    def __post_init__(self) -> None:
        if isinstance(self.type, str):
            try:
                object.__setattr__(self, "type", TriggerType(self.type))
            except ValueError as exc:
                raise AutoHubError("trigger type is not supported") from exc
        if not isinstance(self.type, TriggerType):
            raise AutoHubError("trigger type is not supported")
        if self.type is TriggerType.MANUAL:
            if self.interval_minutes is not None:
                raise AutoHubError("manual triggers cannot include interval_minutes")
            return
        if (
            isinstance(self.interval_minutes, bool)
            or not isinstance(self.interval_minutes, int)
            or not 5 <= self.interval_minutes <= 525_600
        ):
            raise AutoHubError(
                "interval_minutes must be an integer from 5 to 525600"
            )


@dataclass(frozen=True, slots=True)
class WorkflowStep:
    id: str
    title: str
    action: ActionType
    depends_on: tuple[str, ...] = ()
    timeout_seconds: int = 300
    retries: int = 0
    continue_on_error: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not _STEP_ID.fullmatch(self.id):
            raise AutoHubError(
                "step id must start with a lowercase letter and contain only "
                "lowercase letters, numbers, underscores, or hyphens"
            )
        object.__setattr__(self, "title", _text(self.title, "step title", maximum=100))
        if isinstance(self.action, str):
            try:
                object.__setattr__(self, "action", ActionType(self.action))
            except ValueError as exc:
                raise AutoHubError("step action is not supported") from exc
        if not isinstance(self.action, ActionType):
            raise AutoHubError("step action is not supported")
        if (
            not isinstance(self.depends_on, tuple)
            or any(
                not isinstance(item, str) or not _STEP_ID.fullmatch(item)
                for item in self.depends_on
            )
        ):
            raise AutoHubError("step dependencies must be valid step ids")
        if len(self.depends_on) != len(set(self.depends_on)):
            raise AutoHubError("step dependencies cannot contain duplicates")
        if self.id in self.depends_on:
            raise AutoHubError("a step cannot depend on itself")
        if (
            isinstance(self.timeout_seconds, bool)
            or not isinstance(self.timeout_seconds, int)
            or not 1 <= self.timeout_seconds <= 3600
        ):
            raise AutoHubError("timeout_seconds must be an integer from 1 to 3600")
        if (
            isinstance(self.retries, bool)
            or not isinstance(self.retries, int)
            or not 0 <= self.retries <= 5
        ):
            raise AutoHubError("retries must be an integer from 0 to 5")
        if not isinstance(self.continue_on_error, bool):
            raise AutoHubError("continue_on_error must be true or false")


@dataclass(frozen=True, slots=True)
class Workflow:
    name: str
    description: str
    enabled: bool
    trigger: Trigger
    steps: tuple[WorkflowStep, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _text(self.name, "workflow name", maximum=100))
        object.__setattr__(
            self,
            "description",
            _text(self.description, "workflow description", maximum=500),
        )
        if not isinstance(self.enabled, bool):
            raise AutoHubError("enabled must be true or false")
        if not isinstance(self.trigger, Trigger):
            raise AutoHubError("trigger must be valid")
        if (
            not isinstance(self.steps, tuple)
            or not 1 <= len(self.steps) <= 100
            or any(not isinstance(step, WorkflowStep) for step in self.steps)
        ):
            raise AutoHubError("workflow must contain from 1 to 100 valid steps")
        ids = [step.id for step in self.steps]
        if len(ids) != len(set(ids)):
            raise AutoHubError("workflow step ids must be unique")
        known = set(ids)
        missing = sorted(
            dependency
            for step in self.steps
            for dependency in step.depends_on
            if dependency not in known
        )
        if missing:
            raise AutoHubError(f"unknown step dependency: {missing[0]}")
