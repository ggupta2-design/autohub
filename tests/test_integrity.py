import pytest

from autohub.integrity import audit_workflow_integrity
from autohub.models import AutoHubError, Trigger, Workflow, WorkflowStep


def step(step_id, *, title=None, depends_on=()):
    return WorkflowStep(
        id=step_id,
        title=title or step_id,
        action="transform",
        depends_on=depends_on,
    )


def workflow(steps):
    return Workflow(
        name="Private workflow",
        description="Local integrity test",
        enabled=True,
        trigger=Trigger("manual"),
        steps=tuple(steps),
    )


def finding_pairs(audit):
    return [(finding.code, finding.count) for finding in audit.findings]


def test_clean_connected_workflow_has_no_findings():
    audit = audit_workflow_integrity(
        workflow(
            (
                step("collect", title="Collect"),
                step("validate", title="Validate", depends_on=("collect",)),
                step("export", title="Export", depends_on=("validate",)),
            )
        )
    )
    assert audit.clean is True
    assert audit.finding_count == 0
    assert audit.component_count == 1
    assert audit.findings == ()


def test_normalized_duplicate_titles_are_aggregated():
    audit = audit_workflow_integrity(
        workflow(
            (
                step("first", title="Review Data"),
                step("second", title="review data"),
                step("third", title="REVIEW DATA"),
            )
        )
    )
    assert finding_pairs(audit) == [
        ("DUPLICATE_STEP_TITLE", 2),
        ("DISCONNECTED_COMPONENT", 2),
    ]


def test_redundant_transitive_dependency_is_detected():
    audit = audit_workflow_integrity(
        workflow(
            (
                step("collect"),
                step("validate", depends_on=("collect",)),
                step("export", depends_on=("collect", "validate")),
            )
        )
    )
    assert finding_pairs(audit) == [("REDUNDANT_DEPENDENCY", 1)]


def test_disconnected_components_are_counted_beyond_first():
    audit = audit_workflow_integrity(
        workflow(
            (
                step("first_root"),
                step("first_leaf", depends_on=("first_root",)),
                step("second_root"),
                step("second_leaf", depends_on=("second_root",)),
                step("third_root"),
            )
        )
    )
    assert audit.component_count == 3
    assert finding_pairs(audit) == [("DISCONNECTED_COMPONENT", 2)]


def test_integrity_audit_does_not_modify_workflow():
    source = workflow((step("root"), step("leaf", depends_on=("root",))))
    before = source
    audit_workflow_integrity(source)
    assert source == before


def test_integrity_audit_requires_valid_workflow():
    with pytest.raises(AutoHubError, match="workflow must be valid"):
        audit_workflow_integrity(object())
