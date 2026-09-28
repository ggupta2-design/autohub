"""AutoHub command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .loader import load_workflow
from .models import AutoHubError
from .output import write_output
from .planner import build_execution_plan
from .report import format_execution_plan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="autohub",
        description="Validate workflows and build safe execution plans",
    )
    parser.add_argument("--version", action="version", version="autohub 0.1.0")
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
    return parser


def _emit(content: str, output: Path | None) -> None:
    if output is None:
        print(content, end="" if content.endswith("\n") else "\n")
    else:
        destination = write_output(output, content)
        print(f"Wrote {destination.name}")


def run(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
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
