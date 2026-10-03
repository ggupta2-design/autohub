import json

from autohub.models import Trigger, Workflow, WorkflowStep
from autohub.topology import analyze_workflow_topology
from autohub.topology_report import (
    format_topology_analysis,
    topology_analysis_to_dict,
)


def analysis():
    workflow = Workflow(
        name="Secret workflow",
        description="Private process",
        enabled=True,
        trigger=Trigger("manual"),
        steps=(
            WorkflowStep("private_root", "Private root", "collect"),
            WorkflowStep(
                "private_left",
                "Private left",
                "transform",
                depends_on=("private_root",),
            ),
            WorkflowStep(
                "private_right",
                "Private right",
                "transform",
                depends_on=("private_root",),
            ),
        ),
    )
    return analyze_workflow_topology(workflow)


def test_topology_json_report_has_stable_sections():
    payload = json.loads(format_topology_analysis(analysis(), as_json=True))
    assert payload["schema"] == 1
    assert payload["report"] == "workflow_topology"
    assert payload["structure"] == {
        "dependency_depth": 2,
        "dependency_edges": 2,
        "leaf_steps": 2,
        "root_steps": 1,
        "steps": 3,
    }
    assert payload["parallelism"]["maximum_width"] == 2
    assert payload["exposure"]["maximum_downstream_steps"] == 2


def test_redacted_report_omits_workflow_and_step_values():
    rendered = format_topology_analysis(
        analysis(),
        as_json=True,
        redact_names=True,
    )
    assert "Secret workflow" not in rendered
    assert "Private process" not in rendered
    assert "private_root" not in rendered
    assert "Private root" not in rendered
    assert json.loads(rendered)["workflow"] == "[redacted]"


def test_text_report_contains_aggregate_metrics_only():
    rendered = format_topology_analysis(analysis())
    assert "AutoHub workflow topology analysis" in rendered
    assert "Dependency depth: 2" in rendered
    assert "Maximum fan-out: 2" in rendered
    assert "Maximum downstream steps: 2" in rendered
    assert "private_root" not in rendered


def test_topology_dictionary_is_deterministic():
    first = topology_analysis_to_dict(analysis(), redact_names=True)
    second = topology_analysis_to_dict(analysis(), redact_names=True)
    assert first == second
