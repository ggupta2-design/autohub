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

## Analyze dependency topology

```bash
autohub analyze-topology ~/private/workflow.json
autohub analyze-topology ~/private/workflow.json \\
  --json --redact-names \\
  --output ~/private/reports/topology.json
```

Topology analysis reports aggregate depth, width, roots, leaves, dependency
edges, direct fan-in and fan-out, and transitive downstream exposure. It stores
no step identities or per-step values and does not execute the workflow. Status
0 means analysis completed; status 2 means an input or output request was
invalid.

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
autohub compare ~/private/workflow-v1.json ~/private/workflow-v2.json \
  --json --redact-names
```

The audit validates both files, builds the deterministic plan, and evaluates its
aggregate properties against the selected policy. Status 0 means ready, status
1 means blocked by one or more policy findings, and status 2 means an input or
output request was invalid. A blocked decision never changes the workflow.

## Compare workflow versions

```bash
autohub compare ~/private/workflow-v1.json ~/private/workflow-v2.json
autohub compare ~/private/workflow-v1.json ~/private/workflow-v2.json \
  --json --redact-names
```

Comparison validates both manifests and reports aggregate metadata, structural,
downstream-impact, and plan-budget changes. Status 0 means no semantic change,
status 1 means a valid change was found, and status 2 means an input or output
request was invalid. Neither source file is modified.

## Review a proposed workflow change

```bash
autohub review-change \\
  ~/private/workflow-v1.json ~/private/workflow-v2.json \\
  --policy ~/private/guardrail-policy.json \\
  --json --redact-names
```

Change review combines semantic comparison with a policy audit of the proposed
version. Status 0 means unchanged and policy-ready. Status 1 means a valid
change requires human review or the proposed version is policy-blocked. Status
2 means an input or output request was invalid. Passing policy never grants
automatic approval and neither workflow is modified or executed.

## Audit a workflow folder

```bash
autohub audit-folder ~/private/workflows \\
  --policy ~/private/guardrail-policy.json \\
  --json --redact-names

autohub audit-folder ~/private/workflows \\
  --policy ~/private/guardrail-policy.json \\
  --recursive --max-files 250
```

Folder audits discover JSON manifests deterministically, isolate malformed
files, and aggregate ready, blocked, invalid, and finding counts. Recursion is
opt-in, symbolic links are not followed, and the explicit file limit is checked
before auditing. Status 0 means the portfolio is ready, status 1 means at least
one workflow is blocked or invalid, and status 2 means the command could not run
safely. Reports omit filenames, paths, workflow names, and per-file details.

## Redact operational names

```bash
autohub plan examples/workflow.json --json --redact-names
autohub analyze-topology examples/workflow.json --json --redact-names
autohub audit examples/workflow.json \
  --policy examples/guardrail-policy.json \
  --json --redact-names
```

Planning redaction replaces the workflow name and step identifiers. Topology
redaction replaces the workflow name; topology reports never contain step
identifiers. Audit
redaction replaces the workflow and policy names. Portfolio redaction replaces
the policy name; portfolio reports never include workflow names. Change-review
redaction replaces both workflow names and the policy name. Comparison
redaction replaces both workflow names. Audit and comparison reports never include step
identifiers or titles. Aggregate graph shape, budgets, decisions, finding
codes, and comparison deltas remain visible.

## Export without overwriting

```bash
autohub audit ~/private/workflow.json \
  --policy ~/private/guardrail-policy.json \
  --json --redact-names \
  --output ~/private/reports/preflight-audit.json
```

Exports use private permissions where supported and cannot replace an existing
file.

Read [guardrail-policies.md](guardrail-policies.md),
[workflow-comparisons.md](workflow-comparisons.md),
[change-reviews.md](change-reviews.md),
[portfolio-audits.md](portfolio-audits.md), and
[privacy-and-safety.md](privacy-and-safety.md) before using real operational
workflow information.
