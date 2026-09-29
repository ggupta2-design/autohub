# AutoHub

AutoHub is a local-first command-line tool for validating automation workflow
manifests, compiling deterministic dependency plans, and evaluating those plans
against reusable guardrail policies.

AutoHub 0.2 provides:

- strict, versioned workflow and policy JSON schemas;
- validated step identifiers, action types, timeouts, and retry limits;
- missing-dependency, self-dependency, and cycle detection;
- deterministic topological execution waves;
- bounded worst-case attempt and timeout summaries;
- policy limits for steps, waves, attempts, timeouts, enabled state, allowed
  actions, and continue-on-error behavior;
- stable, aggregate preflight finding codes;
- name-redacted Markdown and JSON audit reports;
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

autohub audit examples/workflow.json \
  --policy examples/guardrail-policy.json \
  --json --redact-names \
  --output ~/private/reports/preflight-audit.json
```

Validation, planning, and auditing never execute workflow actions. A ready audit
returns status 0, a policy-blocked audit returns 1, and invalid input or an
unsafe output request returns 2. Exports cannot overwrite existing files.

See the [usage guide](docs/usage.md),
[guardrail policy guide](docs/guardrail-policies.md),
[planning model](docs/planning-model.md), and
[privacy and safety guide](docs/privacy-and-safety.md).

## Status

AutoHub 0.2.0 provides strict workflow validation, deterministic dependency
planning, and policy-driven preflight audits for Python 3.10 through 3.13.
