# Changelog

All notable changes to AutoHub are documented here.

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

AutoHub 0.1 never executes workflow actions, runs arbitrary commands, accesses networks, reads credentials, or sends data.
