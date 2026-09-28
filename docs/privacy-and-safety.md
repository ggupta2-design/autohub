# Privacy and execution safety

AutoHub 0.1 is a local planning tool. It validates workflow manifests and builds
execution plans, but it does not execute steps, read referenced business data,
run commands, schedule jobs, send notifications, make network requests, or
require credentials.

## Sensitive workflow data

Workflow names, step identifiers, dependency structures, timing limits, and
trigger intervals can reveal internal operations. Keep real manifests and plan
exports outside this public repository. The example uses fictional names only.

Use `--redact-names` when a plan must be reviewed outside its private working
directory. Redaction replaces the workflow name and step identifiers, but
actions, graph shape, retry counts, timeouts, and trigger metadata remain
visible and may still be sensitive.

Do not place passwords, tokens, API keys, personal data, customer records, or
secret values in manifests. The schema intentionally has no arbitrary command,
environment-variable, URL, payload, or credential fields.

## File safety

Workflow inputs must be regular bounded UTF-8 JSON files. Symbolic-link inputs
are rejected. Plan exports use owner-only permissions where supported, create
parent directories as needed, and never overwrite existing files or symbolic
links.

These controls do not encrypt files or verify parent-directory permissions.
Use approved encrypted storage and operating-system access controls for private
workflows.

## Planning limits

AutoHub validates supported action labels, dependency references, unique step
identifiers, cycle freedom, timeout bounds, retry bounds, trigger structure,
and a maximum of 100 steps. The calculated timeout budget is a conservative sum
of every allowed attempt, not a prediction of elapsed wall-clock time.

A valid plan does not prove that an eventual executor, integration, or business
process is safe. Review every workflow before connecting it to any system that
can change data or communicate externally.
