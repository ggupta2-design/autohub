# Policy-gated workflow change reviews

AutoHub can combine a semantic workflow comparison with a guardrail audit of the
proposed version. The review is local, deterministic, read-only, and never
executes either workflow.

## Review a proposed change

```bash
autohub review-change \
  ~/private/workflow-baseline.json \
  ~/private/workflow-proposed.json \
  --policy ~/private/guardrail-policy.json \
  --json --redact-names
```

A review validates all three inputs, compares the workflow versions, builds the
current execution plan, and evaluates that plan against the policy. The report
combines aggregate change evidence, plan-budget deltas, current-plan totals, and
stable policy finding codes.

## Decisions

- `unchanged`: no semantic change was detected and the current version passes
  the policy.
- `review_required`: a semantic change was detected and the current version
  passes the policy. Human approval is still required.
- `blocked`: the current version violates at least one policy constraint,
  whether or not it changed.

Exit status `0` is reserved for an unchanged, policy-ready workflow. Both
`review_required` and `blocked` return status `1`, making accidental
approval difficult in automation. Invalid input or an unsafe output request
returns status `2`.

## Privacy and safety

Reports omit step identifiers, titles, descriptions, dependency values,
trigger values, and individual retry or timeout values. Use
`--redact-names` to replace baseline, current, and policy names. Aggregate
counts, changed field labels, plan deltas, and finding codes remain visible.

Exports use private permissions where supported and cannot overwrite an
existing file. The operation does not modify source files, approve changes,
schedule work, send notifications, or execute workflow actions.
