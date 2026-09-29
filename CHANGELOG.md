# Changelog

All notable changes to AutoHub are documented here.

## 0.2.0 — 2026-09-29

AutoHub 0.2 adds policy-driven, read-only workflow preflight audits.

- Validate strict, versioned local guardrail policies.
- Bound steps, dependency waves, attempts, and worst-case timeout budgets.
- Require enabled workflows and control allowed action categories.
- Detect disallowed continue-on-error behavior.
- Produce deterministic ready or blocked decisions with stable finding codes.
- Keep audit findings aggregate and omit step identifiers and titles.
- Support name-redacted text and JSON reports.
- Export private audit reports without overwriting existing files.
- Provide automation-friendly policy validation and audit exit statuses.
- Preserve the execution-free, credential-free, local-first boundary.

## 0.1.0 — 2026-09-28

AutoHub 0.1 introduces a local-first, read-only automation planning workflow.

- Validate strict, versioned JSON workflow manifests.
- Model manual and interval triggers with explicit bounds.
- Reject duplicate, missing, self-referential, and cyclic dependencies.
- Compile deterministic dependency waves with bounded retry and timeout totals.
- Render human-readable and JSON plans with optional workflow and step-name redaction.
- Export reports atomically with private permissions and without overwriting files.
- Provide automation-friendly validation and planning CLI exit statuses.
- Document privacy, execution, and planning boundaries.
- Test the supported Python 3.10–3.13 matrix in continuous integration.

AutoHub never executes workflow actions, runs arbitrary commands, accesses
networks, reads credentials, or sends data.
