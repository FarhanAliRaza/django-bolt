# Profiling & Benchmarking Guide

Django-Bolt has a layered measurement strategy. Different changes are visible at
different altitudes — use the right one for the change you're making:

| Layer | Tool | Proves | Command |
|---|---|---|---|
| Macro HTTP | bombardier | End-to-end RPS + latency distribution | `just save-bench` |
| CPU per request | CodSpeed | Instructions per request on the production path, in each pull request | `just bench-codspeed` |

Suggested proof discipline per optimization PR: `just save-bench` shows the
win survives end-to-end → a before/after flamegraph pair as the narrative
artifact.

## Dispatch-path probes (async bridge cost)

`python/tests/integration/apps/dispatch_probes.py` has one route per dispatch
mechanism (`/t-sync`, `/t-trivial`, `/t-ready`, `/t-sleep0`, `/t-thread`, …).
Point a `runbolt` server at it (`BOLT_API = ["tests.integration.apps.dispatch_probes:api"]`)
and compare per-request latency over a keepalive connection:

- `t_ready − t_trivial` = pure async-bridge cost (no real suspension)
- `t_sleep0 − t_ready` = one suspend/resume cycle

Measure worker-local results at both C=1 and high concurrency with server and
load-generator CPU affinity. Removing the loop-thread hop may reduce latency
while also removing cross-core pipelining between HTTP framing and Python GIL
work. Include `/t-timer` when comparing: positive-delay timers use the
process-wide high-resolution Rust timer dispatcher rather than Tokio's ~1ms
timer wheel.

Attribution tools: `py-spy record --gil` (Task machinery shows up as
`ensure_future`), `strace -f -c -p <pid>` (cross-thread wakeup writes and
`epoll_pwait`s per request). Disable access logging first — the Python logging
stack is large enough (~35-40% of GIL samples) to drown the signal.

## CodSpeed benchmarks

`python/benchmark/http_benchmark.py` sends the requests of `just save-bench` to
the real `runbolt` server, in the pytest process. The `codspeed` job of CI runs
them under CPU simulation in each pull request. It counts the CPU instructions
of all threads, so the count includes the server work for each request. A count
does not change with the load of the machine. Over three runs, each case
stayed within 0.5%. A count is for a round of 100 requests.

The count has limits. It does not include the time in system calls, for
example socket I/O, or the time a thread waits. Each case sends one request at
a time, so it shows no queueing and no contention. The ORM cases read 10 users
from SQLite. Use the count to find a CPU regression. Use bombardier for
throughput and latency under concurrency.

The job also measures walltime on GitHub's `ubuntu-22.04-arm` runner and uploads
the results to CodSpeed. Walltime includes system calls and the time a thread
waits. CodSpeed's macro runners provided dedicated bare-metal hardware tuned
for low noise; GitHub's shared hosts can introduce timing variance. Use CPU
simulation for small CPU regressions, and confirm walltime changes with repeated
runs on the same hardware. Results from the previous CodSpeed macro runner are
not a comparable walltime baseline for the GitHub runner.

The job runs the process on one core with `taskset`. Without a pin, the scheduler
places the client, server and pool threads differently in each run. A case with
a thread pool hop then changes by up to 18% with no code change (#430). Pinning
reduces this variation but does not eliminate shared-host noise. Pin the process
the same way to measure walltime locally:

```bash
taskset -c 3 uv run pytest python/benchmark/http_benchmark.py -p no:django --codspeed --codspeed-mode walltime
```

```bash
just bench-codspeed      # runs each case one time as a check; it measures nothing
```

## Macro HTTP benchmarks

```bash
# needs bombardier: go install github.com/codesenberg/bombardier@latest
just save-bench          # full suite → python/benchmark/BENCHMARK.md; git diff shows the delta
```

For low-noise runs: pin the server (`taskset -c 0-7 python manage.py runbolt …`)
and the load generator to disjoint cores, disable turbo if comparing small
deltas, and take 3+ repetitions — a 2% gate on a single noisy run is
meaningless.

## CPU flamegraphs (Rust + native)

The `profiling` cargo profile (release + debug symbols) exists for this.

```bash
cargo install flamegraph
just build-profiling                       # maturin develop --profile profiling
# terminal 1: run the server under perf
flamegraph -o flame.svg -- python python/example/manage.py runbolt --port 8001
# terminal 2: apply load
bombardier -c 100 -n 200000 http://127.0.0.1:8001/
```

Or attach to a running worker: `perf record -F 997 -g -p <pid> -- sleep 15 &&
perf script | inferno-collapse-perf | inferno-flamegraph > flame.svg`.

For "we moved X to Rust / removed allocation Y" claims, capture a before/after
pair and diff visually — the disappearing frames are the evidence.

## Python-side profiling (py-spy)

```bash
uv tool install py-spy
py-spy record --native -o pyflame.svg --pid <worker-pid> --duration 15
py-spy dump --pid <worker-pid>          # stack snapshot
```

`--native` shows the Rust frames interleaved with Python frames — useful for
seeing GIL-block composition. `py-spy dump` repeatedly during load approximates
GIL hold distribution.

## Allocation counting

For allocation-elimination claims, count allocations per fixed request batch:

```bash
# jemalloc stats (build with the jemalloc feature):
maturin develop --release -- --features jemalloc
# or heaptrack on a single-process server:
heaptrack python python/example/manage.py runbolt --port 8001 --processes 1
bombardier -c 10 -n 10000 http://127.0.0.1:8001/ && kill %1
heaptrack_print heaptrack.*.gz | head -50
```

Report allocations/request before vs after — this proves the mechanism even
when the RPS delta drowns in noise.
