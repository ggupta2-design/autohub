"""Read-only structural integrity audits for AutoHub workflows."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .audit import AuditFinding
from .models import AutoHubError, Workflow


@dataclass(frozen=True, slots=True)
class WorkflowIntegrityAudit:
    """Aggregate workflow integrity findings without step identities."""

    workflow_name: str
    step_count: int
    component_count: int
    findings: tuple[AuditFinding, ...]

    @property
    def clean(self) -> bool:
        return not self.findings

    @property
    def finding_count(self) -> int:
        return sum(finding.count for finding in self.findings)


def _component_count(workflow: Workflow) -> int:
    neighbors = {step.id: set(step.depends_on) for step in workflow.steps}
    for step in workflow.steps:
        for dependency in step.depends_on:
            neighbors[dependency].add(step.id)

    remaining = set(neighbors)
    components = 0
    while remaining:
        components += 1
        pending = [min(remaining)]
        while pending:
            current = pending.pop()
            if current not in remaining:
                continue
            remaining.remove(current)
            pending.extend(neighbors[current] & remaining)
    return components


def _has_alternate_path(
    start: str,
    target: str,
    dependents: dict[str, set[str]],
    excluded_edge: tuple[str, str],
) -> bool:
    pending = [start]
    visited: set[str] = set()
    while pending:
        current = pending.pop()
        if current in visited:
            continue
        visited.add(current)
        for dependent in dependents[current]:
            if (current, dependent) == excluded_edge:
                continue
            if dependent == target:
                return True
            pending.append(dependent)
    return False


def _redundant_dependency_count(workflow: Workflow) -> int:
    dependents = {step.id: set() for step in workflow.steps}
    edges: list[tuple[str, str]] = []
    for step in workflow.steps:
        for dependency in step.depends_on:
            dependents[dependency].add(step.id)
            edges.append((dependency, step.id))
    return sum(
        _has_alternate_path(source, target, dependents, (source, target))
        for source, target in edges
    )


def audit_workflow_integrity(workflow: Workflow) -> WorkflowIntegrityAudit:
    """Detect maintainability issues without executing or modifying a workflow."""

    if not isinstance(workflow, Workflow):
        raise AutoHubError("workflow must be valid")

    title_counts = Counter(step.title.casefold() for step in workflow.steps)
    duplicate_titles = sum(count - 1 for count in title_counts.values() if count > 1)
    components = _component_count(workflow)
    redundant_dependencies = _redundant_dependency_count(workflow)

    findings: list[AuditFinding] = []
    if duplicate_titles:
        findings.append(AuditFinding("DUPLICATE_STEP_TITLE", duplicate_titles))
    if redundant_dependencies:
        findings.append(
            AuditFinding("REDUNDANT_DEPENDENCY", redundant_dependencies)
        )
    if components > 1:
        findings.append(AuditFinding("DISCONNECTED_COMPONENT", components - 1))

    return WorkflowIntegrityAudit(
        workflow_name=workflow.name,
        step_count=len(workflow.steps),
        component_count=components,
        findings=tuple(findings),
    )
