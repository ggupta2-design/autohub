# Changelog

All notable changes to AutoHub are documented here.

## 0.4.0 — 2026-10-01

AutoHub 0.4 adds bounded, privacy-safe workflow portfolio audits.

- Discover JSON workflow manifests deterministically in a local folder.
- Keep recursion opt-in and never follow symbolic links.
- Enforce an explicit file limit before auditing begins.
- Isolate malformed workflows so one invalid file cannot hide other results.
- Aggregate ready, blocked, invalid, and stable policy-finding counts.
- Omit workflow names, filenames, paths, and per-file details from reports.
- Support redacted text and JSON reports with protected exports.
- Provide automation-friendly ready, review-required, and invalid statuses.
- Preserve every source file and execute no workflow actions.

## 0.3.0 — 2026-09-30

AutoHub 0.3 adds privacy-safe, read-only workflow version comparisons.

- Compare two strictly validated workflow manifests locally.
- Aggregate added, removed, modified, unchanged, and impacted step counts.
- Identify changed metadata and step-field categories without reporting values.
- Calculate signed step, wave, attempt, and timeout-budget deltas.
- Expand downstream impact through both dependency graphs.
- Ignore non-semantic step and dependency-list ordering.
- Omit step identifiers, titles, descriptions, and before-or-after values.
- Support name-redacted text and JSON reports.
- Export comparison reports privately without overwriting existing files.
- Provide automation-friendly unchanged, changed, and invalid statuses.

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
