# Workflow version comparisons

AutoHub compares two validated workflow manifests locally without executing or
modifying either version. The baseline represents the previously reviewed
workflow and the current file represents the proposed revision.

## What is compared

Comparison reports aggregate:

- changed workflow metadata field names;
- added, removed, modified, and unchanged step counts;
- modified step-field counts;
- downstream-impacted step counts;
- signed changes in steps, dependency waves, maximum attempts, and worst-case
  timeout budget.

Step order and dependency-list order are not semantic changes. Step identifiers
are used internally to align versions but never appear in comparison reports.
Step titles and before-or-after field values are also omitted.

## Downstream impact

A directly added, removed, or modified step is considered impacted. AutoHub then
walks each version's dependency graph and counts downstream steps whose behavior
could be affected. The result is an aggregate review scope, not a guarantee
that every counted step will change at runtime.

## Status codes

- status 0: both versions are valid and no semantic change was found;
- status 1: both versions are valid and at least one semantic change was found;
- status 2: an input, graph, or output request was invalid.

A changed status is informational. It does not approve or reject the revision.

## Privacy

Use `--redact-names` to remove workflow names. Even without this option, the
report excludes step identifiers, titles, descriptions, dependency values,
trigger values, and individual timing or retry values. Aggregate counts and
signed plan deltas may still reveal operational structure and should be stored
privately.

AutoHub does not send reports, access source-control history, or contact any
external service.
