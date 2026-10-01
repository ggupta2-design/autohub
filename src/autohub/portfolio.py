"""Bounded, privacy-safe workflow portfolio audits."""

from __future__ import annotations

import os
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .audit import AuditFinding, audit_workflow
from .loader import load_workflow
from .models import AutoHubError
from .policy import GuardrailPolicy


MAX_PORTFOLIO_FILES = 1000


def _validate_limit(max_files: int) -> int:
    if (
        isinstance(max_files, bool)
        or not isinstance(max_files, int)
        or not 1 <= max_files <= MAX_PORTFOLIO_FILES
    ):
        raise AutoHubError(
            f"max_files must be an integer from 1 to {MAX_PORTFOLIO_FILES}"
        )
    return max_files


def discover_workflow_files(
    root: str | Path,
    *,
    recursive: bool = False,
    max_files: int = 100,
) -> tuple[Path, ...]:
    """Discover regular JSON files without following symbolic links."""

    limit = _validate_limit(max_files)
    directory = Path(root)
    if directory.is_symlink():
        raise AutoHubError("portfolio root cannot be a symbolic link")
    if not directory.exists():
        raise AutoHubError("portfolio root does not exist")
    if not directory.is_dir():
        raise AutoHubError("portfolio root must be a directory")

    files: list[Path] = []
    if recursive:
        for current, directories, names in os.walk(directory, followlinks=False):
            base = Path(current)
            directories[:] = sorted(
                name
                for name in directories
                if not (base / name).is_symlink()
            )
            for name in sorted(names):
                candidate = base / name
                if (
                    candidate.suffix.lower() == ".json"
                    and not candidate.is_symlink()
                    and candidate.is_file()
                ):
                    files.append(candidate)
    else:
        files = [
            candidate
            for candidate in directory.iterdir()
            if (
                candidate.suffix.lower() == ".json"
                and not candidate.is_symlink()
                and candidate.is_file()
            )
        ]

    ordered = tuple(sorted(files, key=lambda path: path.relative_to(directory).as_posix()))
    if len(ordered) > limit:
        raise AutoHubError(
            f"portfolio contains more than the allowed {limit} JSON files"
        )
    return ordered


@dataclass(frozen=True, slots=True)
class PortfolioAudit:
    policy_name: str
    discovered_files: int
    ready_workflows: int
    blocked_workflows: int
    invalid_files: int
    findings: tuple[AuditFinding, ...]

    @property
    def audited_workflows(self) -> int:
        return self.ready_workflows + self.blocked_workflows

    @property
    def review_required(self) -> bool:
        return bool(self.blocked_workflows or self.invalid_files)

    @property
    def finding_count(self) -> int:
        return sum(finding.count for finding in self.findings)


def audit_workflow_folder(
    root: str | Path,
    policy: GuardrailPolicy,
    *,
    recursive: bool = False,
    max_files: int = 100,
) -> PortfolioAudit:
    """Audit a bounded folder with invalid-file isolation and no execution."""

    if not isinstance(policy, GuardrailPolicy):
        raise AutoHubError("policy must be valid")
    paths = discover_workflow_files(
        root,
        recursive=recursive,
        max_files=max_files,
    )
    ready = 0
    blocked = 0
    invalid = 0
    finding_counts: Counter[str] = Counter()
    for path in paths:
        try:
            result = audit_workflow(load_workflow(path), policy)
        except AutoHubError:
            invalid += 1
            continue
        if result.ready:
            ready += 1
        else:
            blocked += 1
            for finding in result.findings:
                finding_counts[finding.code] += finding.count

    return PortfolioAudit(
        policy_name=policy.name,
        discovered_files=len(paths),
        ready_workflows=ready,
        blocked_workflows=blocked,
        invalid_files=invalid,
        findings=tuple(
            AuditFinding(code, finding_counts[code])
            for code in sorted(finding_counts)
        ),
    )
