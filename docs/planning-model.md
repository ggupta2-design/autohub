# Planning model

AutoHub treats a workflow as a directed graph. Each step is a node and every
`depends_on` entry is an incoming edge. The planner uses a deterministic
variant of Kahn's topological-sort algorithm:

1. Select all remaining steps whose dependencies are complete.
2. Sort those identifiers lexicographically into the next execution wave.
3. Mark the wave complete and repeat.
4. If steps remain but none are ready, reject the graph as cyclic.

This makes reports reproducible regardless of the order in which steps appear
in the JSON manifest. Steps in a wave are eligible for parallel execution by a
future executor, but AutoHub 0.1 never runs them.

## Bounds

Each step permits one initial attempt plus zero through five retries. Timeouts
range from 1 through 3,600 seconds. A workflow contains at most 100 steps.
Interval triggers range from five minutes through one year.

The maximum-attempt summary is the sum of allowed attempts across steps. The
maximum-timeout budget multiplies each step timeout by its allowed attempts and
then sums those values. It is intentionally conservative and does not model
parallel elapsed time, backoff, queueing, setup, cleanup, or external latency.

## Failure semantics

`continue_on_error` is retained in the plan for a future executor. It does not
weaken dependency validation and does not allow planning to skip missing or
cyclic prerequisites. Because this milestone is execution-free, AutoHub makes
no claim about rollback, idempotency, side effects, or retry safety.
