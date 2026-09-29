"""Read-only policy evaluation for AutoHub workflow plans."""

from __future__ import annotations

from dataclasses import dataclass

from .models import AutoHubError, Workflow
from .planner import ExecutionPlan, build_execution_plan
from .policy import GuardrailPolicy


@dataclass(frozen=True, slots=True)
class AuditFinding:
    """Stable, value-free policy finding."""

    code: str
    count: int = 1

    def __post_init__(self) -> None:
        if not isinstance(self.code, str) or not self.code:
            raise AutoHubError("finding code cannot be blank")
        if isinstance(self.count, bool) or not isinstance(self.count, int) or self.count < 1:
            raise AutoHubError("finding count must be a positive integer")


@dataclass(frozen=True, slots=True)
class PreflightAudit:
    workflow_name: str
    policy_name: str
    step_count: int
    wave_count: int
    maximum_attempts: int
    maximum_timeout_seconds: int
    findings: tuple[AuditFinding, ...]

    @property
    def ready(self) -> bool:
        return not self.findings

    @property
    def finding_count(self) -> int:
        return sum(finding.count for finding in self.findings)


def audit_workflow(
    workflow: Workflow,
    policy: GuardrailPolicy,
    *,
    plan: ExecutionPlan | None = None,
) -> PreflightAudit:
    """Evaluate a workflow plan without executing or modifying the workflow."""

    if not isinstance(workflow, Workflow):
        raise AutoHubError("workflow must be valid")
    if not isinstance(policy, GuardrailPolicy):
        raise AutoHubError("policy must be valid")
    evaluated_plan = build_execution_plan(workflow) if plan is None else plan
    if not isinstance(evaluated_plan, ExecutionPlan):
        raise AutoHubError("plan must be valid")
    if evaluated_plan.workflow_name != workflow.name:
        raise AutoHubError("plan does not belong to workflow")

    findings: list[AuditFinding] = []
    if policy.require_enabled and not workflow.enabled:
        findings.append(AuditFinding("WORKFLOW_DISABLED"))
    if evaluated_plan.step_count > policy.maximum_steps:
        findings.append(AuditFinding("STEP_LIMIT_EXCEEDED"))
    if evaluated_plan.wave_count > policy.maximum_waves:
        findings.append(AuditFinding("WAVE_LIMIT_EXCEEDED"))
    if evaluated_plan.maximum_attempts > policy.maximum_attempts:
        findings.append(AuditFinding("ATTEMPT_LIMIT_EXCEEDED"))
    if evaluated_plan.maximum_timeout_seconds > policy.maximum_timeout_seconds:
        findings.append(AuditFinding("TIMEOUT_BUDGET_EXCEEDED"))

    planned_steps = tuple(
        step for wave in evaluated_plan.waves for step in wave
    )
    if not policy.allow_continue_on_error:
        count = sum(step.continue_on_error for step in planned_steps)
        if count:
            findings.append(AuditFinding("CONTINUE_ON_ERROR_DISALLOWED", count))
    disallowed = sum(
        step.action not in policy.allowed_actions for step in planned_steps
    )
    if disallowed:
        findings.append(AuditFinding("ACTION_NOT_ALLOWED", disallowed))

    return PreflightAudit(
        workflow_name=workflow.name,
        policy_name=policy.name,
        step_count=evaluated_plan.step_count,
        wave_count=evaluated_plan.wave_count,
        maximum_attempts=evaluated_plan.maximum_attempts,
        maximum_timeout_seconds=evaluated_plan.maximum_timeout_seconds,
        findings=tuple(findings),
    )
