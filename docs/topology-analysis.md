# Workflow topology analysis

AutoHub can inspect the dependency structure of a validated workflow without
executing any action or exposing step identities.

## Analyze a workflow

```bash
autohub analyze-topology ~/private/workflow.json
autohub analyze-topology ~/private/workflow.json \
  --json --redact-names \
  --output ~/private/reports/topology.json
```

The analysis reports:

- step and dependency-edge counts;
- root and leaf step counts;
- dependency depth and parallel-wave counts;
- maximum parallel width;
- maximum direct fan-in and fan-out;
- the number of steps with dependents;
- the largest transitive downstream exposure.

Downstream steps are deduplicated, including in diamond-shaped graphs. Metrics
are independent of manifest step order.

## Interpretation

Dependency depth is the number of deterministic execution waves, not a runtime
duration estimate. Fan-in counts direct prerequisites; fan-out counts direct
dependents. Maximum downstream exposure counts all unique transitive dependents
of the most connected upstream step.

These measurements indicate structural review scope. They do not predict
failure probability, performance, availability, or business impact, and they
do not label any step as safe or unsafe.

## Privacy and safety

The result stores no step identifiers, titles, descriptions, dependency values,
or per-step metrics. Use `--redact-names` to replace the workflow name.
Aggregate graph shape may still reveal operational design, so exports should
remain private.

Analysis is read-only and local. It does not change the manifest, execute steps,
access referenced data, schedule work, or make network requests. Exports cannot
overwrite existing files.
