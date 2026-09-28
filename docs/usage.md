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

## Redact operational names

```bash
autohub plan examples/workflow.json --json --redact-names
```

This replaces the workflow name with `[redacted]` and step identifiers with
stable `step-001` labels. It does not hide graph shape, action categories,
timeouts, retries, or trigger metadata.

## Export without overwriting

```bash
autohub plan ~/private/workflow.json \
  --json --redact-names \
  --output ~/private/reports/execution-plan.json
```

Exports use private permissions where supported and cannot replace an existing
file. Status 0 means validation succeeded or an enabled workflow was planned.
Status 1 means a valid but disabled workflow was planned. Status 2 means the
manifest, dependency graph, or output request was invalid.

Read [privacy-and-safety.md](privacy-and-safety.md) before using real
operational workflow information.
