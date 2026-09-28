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

## Status

AutoHub 0.1.0 is under active development.
