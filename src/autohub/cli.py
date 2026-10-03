"""AutoHub command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .audit import audit_workflow
from .audit_report import format_preflight_audit
from .compare import compare_workflows
from .compare_report import format_workflow_comparison
from .loader import load_workflow
from .models import AutoHubError
from .output import write_output
from .planner import build_execution_plan
from .policy import load_policy
from .portfolio import audit_workflow_folder
from .portfolio_report import format_portfolio_audit
from .report import format_execution_plan
from .review import review_workflow_change
from .review_report import format_change_review
from .topology import analyze_workflow_topology
from .topology_report import format_topology_analysis


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="autohub",
        description="Validate workflows and build safe execution plans",
    )
    parser.add_argument("--version", action="version", version="autohub 0.5.0")
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser(
        "validate",
        help="validate a workflow without executing it",
    )
    validate.add_argument("workflow", type=Path)
    validate.add_argument("--json", action="store_true", dest="as_json")

    plan = commands.add_parser(
        "plan",
        help="compile dependency waves without executing actions",
    )
    plan.add_argument("workflow", type=Path)
    plan.add_argument("--json", action="store_true", dest="as_json")
    plan.add_argument("--redact-names", action="store_true")
    plan.add_argument("--output", type=Path)

    topology = commands.add_parser(
        "analyze-topology",
        help="analyze workflow dependency topology without executing actions",
    )
    topology.add_argument("workflow", type=Path)
    topology.add_argument("--json", action="store_true", dest="as_json")
    topology.add_argument("--redact-names", action="store_true")
    topology.add_argument("--output", type=Path)

    validate_policy = commands.add_parser(
        "validate-policy",
        help="validate a local guardrail policy",
    )
    validate_policy.add_argument("policy", type=Path)
    validate_policy.add_argument("--json", action="store_true", dest="as_json")

    audit = commands.add_parser(
        "audit",
        help="evaluate a workflow against a policy without executing it",
    )
    audit.add_argument("workflow", type=Path)
    audit.add_argument("--policy", type=Path, required=True)
    audit.add_argument("--json", action="store_true", dest="as_json")
    audit.add_argument("--redact-names", action="store_true")
    audit.add_argument("--output", type=Path)

    folder = commands.add_parser(
        "audit-folder",
        help="audit a bounded workflow folder without executing",
    )
    folder.add_argument("root", type=Path)
    folder.add_argument("--policy", type=Path, required=True)
    folder.add_argument("--recursive", action="store_true")
    folder.add_argument("--max-files", type=int, default=100)
    folder.add_argument("--json", action="store_true", dest="as_json")
    folder.add_argument("--redact-names", action="store_true")
    folder.add_argument("--output", type=Path)

    review = commands.add_parser(
        "review-change",
        help="compare and audit a proposed workflow change without executing",
    )
    review.add_argument("baseline", type=Path)
    review.add_argument("current", type=Path)
    review.add_argument("--policy", type=Path, required=True)
    review.add_argument("--json", action="store_true", dest="as_json")
    review.add_argument("--redact-names", action="store_true")
    review.add_argument("--output", type=Path)

    compare = commands.add_parser(
        "compare",
        help="compare two workflow versions without executing either",
    )
    compare.add_argument("baseline", type=Path)
    compare.add_argument("current", type=Path)
    compare.add_argument("--json", action="store_true", dest="as_json")
    compare.add_argument("--redact-names", action="store_true")
    compare.add_argument("--output", type=Path)
    return parser


def _emit(content: str, output: Path | None) -> None:
    if output is None:
        print(content, end="" if content.endswith("\n") else "\n")
    else:
        destination = write_output(output, content)
        print(f"Wrote {destination.name}")


def _validate_policy(args: argparse.Namespace) -> int:
    policy = load_policy(args.policy)
    payload = {
        "valid": True,
        "require_enabled": policy.require_enabled,
        "maximum_steps": policy.maximum_steps,
        "maximum_waves": policy.maximum_waves,
        "maximum_attempts": policy.maximum_attempts,
        "maximum_timeout_seconds": policy.maximum_timeout_seconds,
        "allow_continue_on_error": policy.allow_continue_on_error,
        "allowed_actions": [action.value for action in policy.allowed_actions],
    }
    if args.as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            "Policy is valid\n"
            f"Require enabled: {'yes' if policy.require_enabled else 'no'}\n"
            f"Maximum steps: {policy.maximum_steps}\n"
            f"Maximum waves: {policy.maximum_waves}\n"
            f"Maximum attempts: {policy.maximum_attempts}\n"
            f"Maximum timeout budget: {policy.maximum_timeout_seconds} seconds\n"
            f"Continue on error allowed: "
            f"{'yes' if policy.allow_continue_on_error else 'no'}"
        )
    return 0


def run(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "validate-policy":
            return _validate_policy(args)

        if args.command == "audit-folder":
            policy = load_policy(args.policy)
            audit = audit_workflow_folder(
                args.root,
                policy,
                recursive=args.recursive,
                max_files=args.max_files,
            )
            content = format_portfolio_audit(
                audit,
                as_json=args.as_json,
                redact_names=args.redact_names,
            )
            _emit(content, args.output)
            return 1 if audit.review_required else 0

        if args.command == "review-change":
            baseline = load_workflow(args.baseline)
            current = load_workflow(args.current)
            policy = load_policy(args.policy)
            review = review_workflow_change(baseline, current, policy)
            content = format_change_review(
                review,
                as_json=args.as_json,
                redact_names=args.redact_names,
            )
            _emit(content, args.output)
            return 0 if review.decision == "unchanged" else 1

        if args.command == "compare":
            baseline = load_workflow(args.baseline)
            current = load_workflow(args.current)
            comparison = compare_workflows(baseline, current)
            content = format_workflow_comparison(
                comparison,
                as_json=args.as_json,
                redact_names=args.redact_names,
            )
            _emit(content, args.output)
            return 1 if comparison.changed else 0

        workflow = load_workflow(args.workflow)
        plan = build_execution_plan(workflow)
        if args.command == "validate":
            payload = {
                "valid": True,
                "enabled": workflow.enabled,
                "steps": plan.step_count,
                "waves": plan.wave_count,
                "trigger": workflow.trigger.type.value,
            }
            if args.as_json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(
                    "Workflow is valid\n"
                    f"Enabled: {'yes' if workflow.enabled else 'no'}\n"
                    f"Trigger: {workflow.trigger.type.value}\n"
                    f"Steps: {plan.step_count}\n"
                    f"Waves: {plan.wave_count}"
                )
            return 0

        if args.command == "analyze-topology":
            analysis = analyze_workflow_topology(workflow)
            content = format_topology_analysis(
                analysis,
                as_json=args.as_json,
                redact_names=args.redact_names,
            )
            _emit(content, args.output)
            return 0

        if args.command == "audit":
            policy = load_policy(args.policy)
            audit = audit_workflow(workflow, policy, plan=plan)
            content = format_preflight_audit(
                audit,
                as_json=args.as_json,
                redact_names=args.redact_names,
            )
            _emit(content, args.output)
            return 0 if audit.ready else 1

        content = format_execution_plan(
            plan,
            as_json=args.as_json,
            redact_names=args.redact_names,
        )
        _emit(content, args.output)
        return 0 if workflow.enabled else 1
    except AutoHubError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
