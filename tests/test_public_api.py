import pytest

import autohub
from autohub.cli import build_parser


def test_planning_and_audit_workflows_are_available_from_public_api():
    assert autohub.__version__ == "0.6.0"
    assert callable(autohub.load_workflow)
    assert callable(autohub.workflow_from_dict)
    assert callable(autohub.build_execution_plan)
    assert callable(autohub.analyze_workflow_topology)
    assert callable(autohub.topology_analysis_to_dict)
    assert callable(autohub.format_topology_analysis)
    assert callable(autohub.execution_plan_to_dict)
    assert callable(autohub.format_execution_plan)
    assert callable(autohub.load_policy)
    assert callable(autohub.policy_from_dict)
    assert callable(autohub.audit_workflow)
    assert callable(autohub.preflight_audit_to_dict)
    assert callable(autohub.format_preflight_audit)
    assert callable(autohub.compare_workflows)
    assert callable(autohub.review_workflow_change)
    assert callable(autohub.change_review_to_dict)
    assert callable(autohub.format_change_review)
    assert callable(autohub.discover_workflow_files)
    assert callable(autohub.audit_workflow_folder)
    assert callable(autohub.portfolio_audit_to_dict)
    assert callable(autohub.format_portfolio_audit)
    assert callable(autohub.workflow_comparison_to_dict)
    assert callable(autohub.format_workflow_comparison)
    assert callable(autohub.write_output)
    assert autohub.ActionType.COLLECT.value == "collect"
    assert autohub.MAX_POLICY_BYTES == 64 * 1024
    assert autohub.MAX_PORTFOLIO_FILES == 1000


def test_cli_reports_synced_release_version(capsys):
    with pytest.raises(SystemExit) as raised:
        build_parser().parse_args(["--version"])

    assert raised.value.code == 0
    assert capsys.readouterr().out == "autohub 0.6.0\n"
