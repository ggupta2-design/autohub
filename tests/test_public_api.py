import pytest

import autohub
from autohub.cli import build_parser


def test_planning_workflow_is_available_from_public_api():
    assert autohub.__version__ == "0.1.0"
    assert callable(autohub.load_workflow)
    assert callable(autohub.workflow_from_dict)
    assert callable(autohub.build_execution_plan)
    assert callable(autohub.execution_plan_to_dict)
    assert callable(autohub.format_execution_plan)
    assert callable(autohub.write_output)
    assert autohub.ActionType.COLLECT.value == "collect"


def test_cli_reports_synced_release_version(capsys):
    with pytest.raises(SystemExit) as raised:
        build_parser().parse_args(["--version"])

    assert raised.value.code == 0
    assert capsys.readouterr().out == "autohub 0.1.0\n"
