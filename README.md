# AutoHub

AutoHub is a local-first command-line tool for validating automation workflow
manifests and compiling them into deterministic, dependency-aware execution
plans.

The first milestone focuses on safe planning fundamentals:

- strict, versioned JSON workflow definitions;
- validated step identifiers, action types, timeouts, and retry limits;
- missing-dependency, self-dependency, and cycle detection;
- deterministic topological execution waves;
- bounded worst-case attempt and timeout summaries;
- readable and JSON planning reports;
- private, non-overwriting report exports;
- no workflow execution, network requests, credentials, or hosted accounts.

AutoHub is being built as part of an eight-week automation-project challenge.
Public examples contain fictional workflows only. Real operational workflows and
private paths must remain in private local files.

## Quick start

```bash
python -m pip install -e .

autohub validate examples/workflow.json
autohub plan examples/workflow.json
autohub plan examples/workflow.json \
  --json --redact-names \
  --output ~/private/reports/execution-plan.json
```

Validation and planning never execute workflow actions. An enabled plan returns
status 0, a valid disabled plan returns 1, and invalid input or an unsafe output
request returns 2. Exports cannot overwrite existing files.

See the [usage guide](docs/usage.md), [planning model](docs/planning-model.md),
and [privacy and safety guide](docs/privacy-and-safety.md).

## Status

AutoHub 0.1.0 provides strict workflow validation and deterministic,
dependency-aware dry-run planning for Python 3.10 through 3.13.
