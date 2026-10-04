# Workflow integrity audits

AutoHub can review the structure of one strictly validated workflow without
executing or changing it. The audit is a maintainability aid, not an approval
or runtime-risk decision.

## Run an audit

```bash
autohub audit-integrity ~/private/workflow.json
autohub audit-integrity ~/private/workflow.json \
  --json --redact-names \
  --output ~/private/reports/integrity-audit.json
```

A clean audit exits with status 0. A valid workflow with review findings exits
with status 1. Invalid input or an unsafe export request exits with status 2.
Exports are private where supported and never overwrite an existing path.

## Findings

- `DUPLICATE_STEP_TITLE` counts normalized title occurrences beyond the first.
  Repeated titles can make reviews and operator-facing plans ambiguous.
- `REDUNDANT_DEPENDENCY` counts direct dependency edges for which another
  dependency path already exists. The edge may be intentional, but can make
  maintenance harder.
- `DISCONNECTED_COMPONENT` counts weakly connected graph components beyond the
  first. Independent workflow branches may be intentional and still deserve an
  explicit review.

Finding order and counts are deterministic and independent of manifest step
order. An audit does not rewrite a workflow or recommend an automatic fix.

## Disclosure boundary

Reports include only the workflow name, total steps, weak-component count,
aggregate finding codes, and counts. They never include step identifiers,
titles, descriptions, dependency values, action labels, timeouts, retries, or
per-step findings. `--redact-names` also replaces the workflow name.

Aggregate structure can still reveal operational complexity. Keep real
manifests and reports in approved private storage. A clean result does not prove
authorization, correctness, security, performance, or execution safety.
