from autohub.integrity import audit_workflow_integrity
from autohub.models import Trigger, Workflow, WorkflowStep


def make_workflow(specs):
    return Workflow(
        name="Integrity graph",
        description="Fictional graph-only test",
        enabled=True,
        trigger=Trigger("manual"),
        steps=tuple(
            WorkflowStep(
                id=step_id,
                title=title,
                action="transform",
                depends_on=depends_on,
            )
            for step_id, title, depends_on in specs
        ),
    )


def pairs(audit):
    return [(finding.code, finding.count) for finding in audit.findings]


def test_diamond_edges_are_not_redundant():
    audit = audit_workflow_integrity(
        make_workflow(
            (
                ("root", "Root", ()),
                ("left", "Left", ("root",)),
                ("right", "Right", ("root",)),
                ("leaf", "Leaf", ("left", "right")),
            )
        )
    )
    assert audit.clean is True


def test_multiple_transitive_edges_are_counted_individually():
    audit = audit_workflow_integrity(
        make_workflow(
            (
                ("a", "A", ()),
                ("b", "B", ("a",)),
                ("c", "C", ("a", "b")),
                ("d", "D", ("a", "b", "c")),
            )
        )
    )
    assert pairs(audit) == [("REDUNDANT_DEPENDENCY", 3)]


def test_finding_order_is_stable_when_step_order_changes():
    first = make_workflow(
        (
            ("a", "Review", ()),
            ("b", "review", ()),
            ("c", "Publish", ("a", "b")),
            ("isolated", "Archive", ()),
        )
    )
    second = make_workflow(
        (
            ("isolated", "Archive", ()),
            ("c", "Publish", ("b", "a")),
            ("b", "review", ()),
            ("a", "Review", ()),
        )
    )
    assert pairs(audit_workflow_integrity(first)) == pairs(
        audit_workflow_integrity(second)
    )


def test_audit_representation_contains_no_step_identity():
    audit = audit_workflow_integrity(
        make_workflow(
            (
                ("sensitive-id-one", "Sensitive title", ()),
                ("sensitive-id-two", "sensitive title", ()),
            )
        )
    )
    rendered = repr(audit)
    assert "sensitive-id" not in rendered
    assert "Sensitive title" not in rendered
