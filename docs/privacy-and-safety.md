# Privacy and execution safety

AutoHub 0.6 is a local planning, preflight-audit, workflow-comparison,
portfolio-audit, change-review, and dependency-topology analysis tool. It validates workflow manifests and guardrail policies,
builds execution plans, evaluates aggregate policy properties, compares
validated versions, and reviews bounded folders. It does not execute steps,
read referenced business data, run commands, schedule jobs, send notifications,
make network requests, or require credentials.

## Sensitive workflow and policy data

Workflow names, filenames, paths, policy names, step identifiers, dependency
structures, timing limits, trigger intervals, comparison deltas, and policy
thresholds can reveal internal operations. Keep real manifests, policies, plans,
audits, and exports outside this public repository. Public examples use
fictional names only.

Use `--redact-names` when a plan, audit, comparison, portfolio report, or
change review, or topology report must be
reviewed outside its private working directory. Portfolio reports never include
workflow names, filenames, paths, step identifiers, titles, descriptions, or
per-file results. Redaction additionally replaces the policy name. Change reviews omit step identities and values and can replace both workflow
names and the policy name. Topology reports retain only aggregate graph metrics
and can replace the workflow name. Aggregate counts, changed field labels, plan deltas,
and finding codes remain visible and may still be sensitive.

Do not place passwords, tokens, API keys, personal data, customer records, or
secret values in manifests or policies. Their strict schemas intentionally have
no arbitrary command, environment-variable, URL, payload, or credential fields.

## File and folder safety

Individual workflow versions and policy inputs must be regular bounded UTF-8
JSON files. Symbolic links are rejected. A portfolio root must be a real
directory and cannot be a symbolic link. Discovery skips linked files and
directories, does not follow links during recursion, sorts files
deterministically, and enforces an explicit maximum before auditing.

Report exports use owner-only permissions where supported, create parent
directories as needed, and never overwrite existing files or symbolic links.
These controls do not encrypt files or verify parent-directory permissions. Use
approved encrypted storage and operating-system access controls for private
workflows and policies.

## Planning and policy limits

AutoHub validates supported action labels, dependency references, unique step
identifiers, cycle freedom, timeout bounds, retry bounds, trigger structure,
and a maximum of 100 steps. A guardrail policy can impose stricter step, wave,
attempt, timeout, continue-on-error, enabled-state, and action constraints.

The timeout budget is a conservative sum of every allowed attempt, not a
prediction of elapsed wall-clock time. Finding counts are aggregate signals,
not proof that an individual step is safe or unsafe.

## Portfolio audit boundary

Folder audits isolate malformed workflow files so one bad file does not hide
other results. The report discloses invalid-file counts but not validation error
details or source identities. JSON files that are not workflows count as
invalid, so keep policies and unrelated JSON outside the audited root.

A ready portfolio means every discovered workflow was valid and fit the
selected local policy. An empty folder is a valid empty audit. Neither result
proves that undiscovered, excluded, linked, or non-JSON files are safe.

## Topology analysis boundary

Topology reports omit step identifiers, titles, descriptions, dependency
values, and per-step measurements. Aggregate depth, width, fan-in, fan-out, and
downstream exposure can still reveal operational complexity. Keep real reports
private even when names are redacted.

Structural measurements describe a validated dependency graph. They do not
predict runtime duration, failure likelihood, performance, business impact, or
whether a step is safe. AutoHub does not assign risk scores or make approval
decisions from topology alone.

## Change review boundary

A policy-ready proposed version is not automatically safe or approved. A
semantic change always produces `review_required`, even when every guardrail
passes. AutoHub cannot verify authorization, business intent, data handling,
external dependencies, regulatory obligations, or runtime behavior. A person
or separately authorized system must make the approval decision.

Status 0 is reserved for unchanged, policy-ready input. Changed and blocked
reviews both return status 1 so an automation gate cannot confuse policy
compliance with approval. Reviews never edit, execute, schedule, or publish a
workflow.

## Decision and comparison boundaries

A ready preflight decision means that a valid deterministic plan fits the
selected local policy. It does not prove data quality, external availability,
authorization, regulatory compliance, or execution safety.

A comparison aligns steps internally by identifier, but reports only aggregate
counts, safe field labels, and signed plan deltas. It does not reveal
identifiers, titles, descriptions, dependency values, trigger values, or
individual timing values. The downstream-impact count identifies review scope;
it does not predict runtime behavior or approve a change.
