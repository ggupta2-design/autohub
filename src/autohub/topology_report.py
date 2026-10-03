"""Privacy-safe dependency topology reports."""

from __future__ import annotations

import json
from typing import Any

from .topology import TopologyAnalysis


def topology_analysis_to_dict(
    analysis: TopologyAnalysis,
    *,
    redact_names: bool = False,
) -> dict[str, Any]:
    """Return aggregate graph metrics without step identities."""

    return {
        "schema": 1,
        "report": "workflow_topology",
        "workflow": "[redacted]" if redact_names else analysis.workflow_name,
        "structure": {
            "steps": analysis.step_count,
            "dependency_edges": analysis.dependency_edges,
            "root_steps": analysis.root_steps,
            "leaf_steps": analysis.leaf_steps,
            "dependency_depth": analysis.dependency_depth,
        },
        "parallelism": {
            "has_parallelism": analysis.has_parallelism,
            "parallel_waves": analysis.parallel_waves,
            "maximum_width": analysis.maximum_parallel_width,
        },
        "exposure": {
            "maximum_fan_in": analysis.maximum_fan_in,
            "maximum_fan_out": analysis.maximum_fan_out,
            "steps_with_dependents": analysis.steps_with_dependents,
            "maximum_downstream_steps": analysis.maximum_downstream_steps,
        },
    }


def format_topology_analysis(
    analysis: TopologyAnalysis,
    *,
    as_json: bool = False,
    redact_names: bool = False,
) -> str:
    """Format topology metrics without disclosing graph identities."""

    payload = topology_analysis_to_dict(
        analysis,
        redact_names=redact_names,
    )
    if as_json:
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"

    structure = payload["structure"]
    parallelism = payload["parallelism"]
    exposure = payload["exposure"]
    return (
        "AutoHub workflow topology analysis\n"
        f"Workflow: {payload['workflow']}\n"
        f"Steps: {structure['steps']}\n"
        f"Dependency edges: {structure['dependency_edges']}\n"
        f"Root steps: {structure['root_steps']}\n"
        f"Leaf steps: {structure['leaf_steps']}\n"
        f"Dependency depth: {structure['dependency_depth']}\n"
        f"Parallel waves: {parallelism['parallel_waves']}\n"
        f"Maximum parallel width: {parallelism['maximum_width']}\n"
        f"Maximum fan-in: {exposure['maximum_fan_in']}\n"
        f"Maximum fan-out: {exposure['maximum_fan_out']}\n"
        f"Steps with dependents: {exposure['steps_with_dependents']}\n"
        f"Maximum downstream steps: {exposure['maximum_downstream_steps']}\n"
    )
