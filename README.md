# AutoHub

AutoHub is a local-first command-line tool for validating automation workflows,
compiling deterministic dependency plans, enforcing reusable guardrail policies,
and comparing workflow versions before approval.

AutoHub 0.3 provides:

- strict, versioned workflow and policy JSON schemas;
- validated identifiers, action types, dependencies, timeouts, and retries;
- deterministic topological execution waves and bounded plan budgets;
- guardrail policies for steps, waves, attempts, timeouts, enabled state,
  allowed actions, and continue-on-error behavior;
- read-only comparisons of validated workflow versions;
- aggregate added, removed, modified, unchanged, and downstream-impact counts;
- signed plan-budget deltas that omit step-level values;
- privacy-aware text and JSON reports;
- private, non-overwriting report exports;
- no workflow execution, network requests, credentials, or hosted accounts.

AutoHub is being built as part of an eight-week automation-project challenge.
Public examples contain fictional workflows and policies only. Real operational
files and private paths must remain in private local storage.

## Quick start

```bash
python -m pip install -e .

autohub validate examples/workflow.json
autohub plan examples/workflow.json

autohub validate-policy examples/guardrail-policy.json
autohub audit examples/workflow.json \
  --policy examples/guardrail-policy.json

autohub compare ~/private/workflow-v1.json ~/private/workflow-v2.json \
  --json --redact-names \
  --output ~/private/reports/workflow-comparison.json
```

Validation, planning, auditing, and comparison never execute workflow actions.
An unchanged comparison returns status 0, a valid changed comparison returns 1,
and invalid input or an unsafe output request returns 2. Exports cannot
overwrite existing files.

See the [usage guide](docs/usage.md),
[workflow comparison guide](docs/workflow-comparisons.md),
[guardrail policy guide](docs/guardrail-policies.md),
[planning model](docs/planning-model.md), and
[privacy and safety guide](docs/privacy-and-safety.md).

## Status

AutoHub 0.3.0 provides strict validation, deterministic dependency planning,
policy-driven preflight audits, and privacy-safe workflow version comparisons
for Python 3.10 through 3.13.
