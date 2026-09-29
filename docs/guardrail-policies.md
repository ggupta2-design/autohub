# Guardrail policies

AutoHub guardrail policies define local, reusable limits for a workflow plan.
They are evaluated after strict workflow validation and deterministic dependency
planning. Auditing is read-only and never executes an action.

## Policy fields

Every policy uses schema version 1 and must contain exactly these fields:

- `name`: a normalized label of at most 100 characters;
- `require_enabled`: whether disabled workflows must be blocked;
- `maximum_steps`: allowed total steps, from 1 through 100;
- `maximum_waves`: allowed dependency waves, from 1 through 100;
- `maximum_attempts`: allowed worst-case attempts, from 1 through 600;
- `maximum_timeout_seconds`: allowed worst-case timeout budget, from 1 through
  2,160,000 seconds;
- `allow_continue_on_error`: whether any step may continue after failure;
- `allowed_actions`: a unique, non-empty subset of `collect`, `validate`,
  `transform`, and `export`.

Unknown fields and unsupported schema versions are rejected. Policy files are
bounded to 64 KiB, must be UTF-8 JSON, and cannot be symbolic links.

## Stable findings

Audits return a deterministic sequence of aggregate finding codes:

- `WORKFLOW_DISABLED`
- `STEP_LIMIT_EXCEEDED`
- `WAVE_LIMIT_EXCEEDED`
- `ATTEMPT_LIMIT_EXCEEDED`
- `TIMEOUT_BUDGET_EXCEEDED`
- `CONTINUE_ON_ERROR_DISALLOWED`
- `ACTION_NOT_ALLOWED`

A ready result contains no findings. A blocked result contains codes and
aggregate counts, never step identifiers or titles.

## Interpretation

A ready decision means only that the validated plan fits the selected local
policy. It does not prove that an external system is available, that source data
is correct, or that executing the workflow would be safe. AutoHub 0.2 does not
execute workflows or contact external systems.
