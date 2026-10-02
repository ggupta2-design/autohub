"""Policy-gated, read-only workflow change reviews."""

from __future__ import annotations

from dataclasses import dataclass

from .audit import AuditFinding, PreflightAudit, audit_workflow
from .compare import WorkflowComparison, compare_workflows
from .models import AutoHubError, Workflow
from .policy import GuardrailPolicy


@dataclass(frozen=True, slots=True)
class ChangeReview:
    """Aggregate evidence for reviewing a workflow version change."""

    comparison: WorkflowComparison
    current_audit: PreflightAudit

    def __post_init__(self) -> None:
        if not isinstance(self.comparison, WorkflowComparison):
            raise AutoHubError("comparison must be valid")
        if not isinstance(self.current_audit, PreflightAudit):
            raise AutoHubError("current audit must be valid")
        if self.comparison.current_name != self.current_audit.workflow_name:
            raise AutoHubError("audit does not belong to the current workflow")

    @property
    def decision(self) -> str:
        if not self.current_audit.ready:
            return "blocked"
        if self.comparison.changed:
            return "review_required"
        return "unchanged"

    @property
    def changed(self) -> bool:
        return self.comparison.changed

    @property
    def policy_ready(self) -> bool:
        return self.current_audit.ready

    @property
    def policy_findings(self) -> tuple[AuditFinding, ...]:
        return self.current_audit.findings

    @property
    def finding_count(self) -> int:
        return self.current_audit.finding_count


def review_workflow_change(
    baseline: Workflow,
    current: Workflow,
    policy: GuardrailPolicy,
) -> ChangeReview:
    """Compare and audit a proposed workflow without executing either version."""

    if not isinstance(baseline, Workflow) or not isinstance(current, Workflow):
        raise AutoHubError("baseline and current workflows must be valid")
    if not isinstance(policy, GuardrailPolicy):
        raise AutoHubError("policy must be valid")
    return ChangeReview(
        comparison=compare_workflows(baseline, current),
        current_audit=audit_workflow(current, policy),
    )
