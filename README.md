# AutoHub

AutoHub is a local-first command-line tool for validating automation workflows,
compiling deterministic dependency plans, enforcing reusable guardrail policies,
comparing versions, auditing bounded portfolios, reviewing changes, and analyzing dependency topology before approval.

AutoHub 0.7 provides:

- strict, versioned workflow and policy JSON schemas;
- validated identifiers, action types, dependencies, timeouts, and retries;
- deterministic topological execution waves and bounded plan budgets;
- guardrail policies for steps, waves, attempts, timeouts, enabled state,
  allowed actions, and continue-on-error behavior;
- read-only comparisons of validated workflow versions;
- aggregate added, removed, modified, unchanged, and downstream-impact counts;
- signed plan-budget deltas that omit step-level values;
- bounded shallow or recursive workflow folder discovery;
- portfolio audits with invalid-file isolation and aggregate policy findings;
- path-free reports that omit workflow and file identities;
- combined change reviews with semantic deltas and current-policy evidence;
- conservative decisions that never automatically approve changed workflows;
- aggregate dependency depth, width, fan-in, fan-out, and downstream exposure;
- topology reports that retain no step identities or per-step values;
- read-only integrity audits for duplicate titles, redundant dependencies, and disconnected components;
- aggregate integrity reports with stable codes and no step-level disclosure;
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
autohub analyze-topology examples/workflow.json --json --redact-names
autohub audit-integrity examples/workflow.json --json --redact-names

autohub validate-policy examples/guardrail-policy.json
autohub audit examples/workflow.json \
  --policy examples/guardrail-policy.json

autohub compare ~/private/workflow-v1.json ~/private/workflow-v2.json \
  --json --redact-names \
  --output ~/private/reports/workflow-comparison.json
```

Validation, planning, topology analysis, integrity auditing, policy auditing, comparison, portfolio review, and change review never execute workflow actions.
An unchanged comparison returns status 0, a valid changed comparison returns 1,
and invalid input or an unsafe output request returns 2. Exports cannot
overwrite existing files.

See the [usage guide](docs/usage.md),
[workflow comparison guide](docs/workflow-comparisons.md),
[change review guide](docs/change-reviews.md),
[portfolio audit guide](docs/portfolio-audits.md),
[guardrail policy guide](docs/guardrail-policies.md),
[planning model](docs/planning-model.md),
[topology analysis guide](docs/topology-analysis.md),
[integrity audit guide](docs/integrity-audits.md), and
[privacy and safety guide](docs/privacy-and-safety.md).

## Status

AutoHub 0.7.0 provides strict validation, deterministic dependency planning,
privacy-safe topology and integrity analysis, policy-driven audits, version comparisons,
bounded portfolio audits, and conservative change reviews
for Python 3.10 through 3.13.
