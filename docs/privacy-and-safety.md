# Privacy and execution safety

AutoHub 0.2 is a local planning and preflight-audit tool. It validates workflow
manifests and guardrail policies, builds execution plans, and evaluates their
aggregate properties. It does not execute steps, read referenced business data,
run commands, schedule jobs, send notifications, make network requests, or
require credentials.

## Sensitive workflow and policy data

Workflow names, policy names, step identifiers, dependency structures, timing
limits, trigger intervals, and policy thresholds can reveal internal
operations. Keep real manifests, policies, plans, and audit exports outside this
public repository. Public examples use fictional names only.

Use `--redact-names` when a plan or audit must be reviewed outside its private
working directory. A redacted audit replaces workflow and policy names and
never includes step identifiers or titles. Aggregate graph shape, budgets,
decisions, and finding codes remain visible and may still be sensitive.

Do not place passwords, tokens, API keys, personal data, customer records, or
secret values in manifests or policies. Their strict schemas intentionally have
no arbitrary command, environment-variable, URL, payload, or credential fields.

## File safety

Workflow and policy inputs must be regular bounded UTF-8 JSON files. Symbolic
links are rejected. Report exports use owner-only permissions where supported,
create parent directories as needed, and never overwrite existing files or
symbolic links.

These controls do not encrypt files or verify parent-directory permissions.
Use approved encrypted storage and operating-system access controls for private
workflows and policies.

## Planning and policy limits

AutoHub validates supported action labels, dependency references, unique step
identifiers, cycle freedom, timeout bounds, retry bounds, trigger structure,
and a maximum of 100 steps. A guardrail policy can impose stricter step, wave,
attempt, timeout, continue-on-error, enabled-state, and action constraints.

The timeout budget is a conservative sum of every allowed attempt, not a
prediction of elapsed wall-clock time. Finding counts are aggregate signals,
not proof that an individual step is safe or unsafe.

## Decision boundary

A ready preflight decision means that a valid deterministic plan fits the
selected local policy. It does not prove data quality, external availability,
authorization, regulatory compliance, or execution safety. Review every
workflow before connecting it to a system that can change data or communicate
externally.
