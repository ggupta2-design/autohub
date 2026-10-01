# Bounded workflow portfolio audits

AutoHub can review a folder of workflow definitions against one local guardrail
policy without executing any workflow. The audit is deterministic, read-only,
and designed for automation gates.

## Run an audit

Keep the policy outside the audited folder so it is not treated as a workflow:

```bash
autohub audit-folder ./private-workflows \
  --policy ./policies/conservative.json \
  --json \
  --redact-names
```

By default AutoHub inspects only JSON files directly inside the folder and
allows at most 100 files. Subfolders require explicit opt-in:

```bash
autohub audit-folder ./private-workflows \
  --policy ./policies/conservative.json \
  --recursive \
  --max-files 250 \
  --output ./private-reports/portfolio.txt
```

The root cannot be a symbolic link. Linked files and linked directories are
skipped, recursive traversal never follows links, and discovery order is stable.
The maximum file count is checked before any workflow is audited.

## Results and exit statuses

Malformed workflows are isolated so one bad file cannot hide the rest of the
portfolio. Reports contain only aggregate counts and finding codes:

- discovered, audited, ready, blocked, and invalid counts;
- total stable policy findings;
- no workflow names, filenames, paths, step IDs, titles, or descriptions.

Exit status `0` means every discovered workflow was valid and ready. Status
`1` means one or more workflows were blocked or invalid. Status `2` means
the command itself could not run safely, such as an invalid policy, linked root,
invalid bound, exceeded file limit, or protected output collision.

An empty folder is a successful empty audit. AutoHub does not create, modify,
execute, schedule, enable, or disable workflows during this operation.
