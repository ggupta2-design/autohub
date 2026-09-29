# Using AutoHub

Install AutoHub in a virtual environment:

```bash
python -m pip install -e .
```

## Validate a workflow

```bash
autohub validate examples/workflow.json
autohub validate examples/workflow.json --json
```

Validation is local and does not execute any step. Manifests must use the exact
schema-version-1 fields. Unknown fields, unsupported versions, malformed
triggers, unsupported actions, invalid identifiers, missing dependencies,
cycles, excessive timeouts, excessive retries, and workflows above 100 steps
are rejected.

## Build a dry-run plan

```bash
autohub plan examples/workflow.json
autohub plan examples/workflow.json --json
```

Planning creates deterministic topological waves. Independent steps appear in
the same wave in identifier order; dependent steps appear only after every
prerequisite wave. Reports include conservative maximum attempt and timeout
budgets. No workflow actions are executed.

## Validate a guardrail policy

```bash
autohub validate-policy examples/guardrail-policy.json
autohub validate-policy examples/guardrail-policy.json --json
```

Policy validation is local and does not load or execute a workflow. It checks
the strict schema, bounded budgets, boolean safeguards, and unique allowed
action set.

## Run a read-only preflight audit

```bash
autohub audit examples/workflow.json \
  --policy examples/guardrail-policy.json

autohub audit examples/workflow.json \
  --policy examples/guardrail-policy.json \
  --json --redact-names
```

The audit validates both files, builds the deterministic plan, and evaluates its
aggregate properties against the selected policy. Status 0 means ready, status
1 means blocked by one or more policy findings, and status 2 means an input or
output request was invalid. A blocked decision never changes the workflow.

## Redact operational names

```bash
autohub plan examples/workflow.json --json --redact-names
autohub audit examples/workflow.json \
  --policy examples/guardrail-policy.json \
  --json --redact-names
```

Planning redaction replaces the workflow name and step identifiers. Audit
redaction replaces the workflow and policy names; audit reports never include
step identifiers or titles. Aggregate graph shape, budgets, decisions, and
finding codes remain visible.

## Export without overwriting

```bash
autohub audit ~/private/workflow.json \
  --policy ~/private/guardrail-policy.json \
  --json --redact-names \
  --output ~/private/reports/preflight-audit.json
```

Exports use private permissions where supported and cannot replace an existing
file.

Read [guardrail-policies.md](guardrail-policies.md) and
[privacy-and-safety.md](privacy-and-safety.md) before using real operational
workflow information.
