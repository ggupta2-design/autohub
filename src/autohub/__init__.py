"""Local-first dependency planning and policy-driven preflight audits."""

from .audit import AuditFinding, PreflightAudit, audit_workflow
from .audit_report import format_preflight_audit, preflight_audit_to_dict
from .compare import WorkflowComparison, compare_workflows
from .compare_report import format_workflow_comparison, workflow_comparison_to_dict
from .loader import MAX_WORKFLOW_BYTES, load_workflow, workflow_from_dict
from .models import (
    ActionType,
    AutoHubError,
    Trigger,
    TriggerType,
    Workflow,
    WorkflowStep,
)
from .output import write_output
from .planner import ExecutionPlan, PlannedStep, build_execution_plan
from .portfolio import (
    MAX_PORTFOLIO_FILES,
    PortfolioAudit,
    audit_workflow_folder,
    discover_workflow_files,
)
from .portfolio_report import format_portfolio_audit, portfolio_audit_to_dict
from .policy import (
    MAX_POLICY_BYTES,
    GuardrailPolicy,
    load_policy,
    policy_from_dict,
)
from .report import execution_plan_to_dict, format_execution_plan

__version__ = "0.4.0"

__all__ = [
    "ActionType",
    "AuditFinding",
    "AutoHubError",
    "ExecutionPlan",
    "GuardrailPolicy",
    "MAX_POLICY_BYTES",
    "MAX_PORTFOLIO_FILES",
    "MAX_WORKFLOW_BYTES",
    "PlannedStep",
    "PortfolioAudit",
    "PreflightAudit",
    "Trigger",
    "TriggerType",
    "Workflow",
    "WorkflowComparison",
    "WorkflowStep",
    "__version__",
    "audit_workflow",
    "audit_workflow_folder",
    "build_execution_plan",
    "compare_workflows",
    "discover_workflow_files",
    "execution_plan_to_dict",
    "format_execution_plan",
    "format_portfolio_audit",
    "format_preflight_audit",
    "format_workflow_comparison",
    "load_policy",
    "load_workflow",
    "policy_from_dict",
    "portfolio_audit_to_dict",
    "preflight_audit_to_dict",
    "workflow_comparison_to_dict",
    "workflow_from_dict",
    "write_output",
]
