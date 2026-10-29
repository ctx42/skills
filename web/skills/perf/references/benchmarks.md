# Benchmarks

How `perf` proves a gain in code that runs in isolation (SKILL.md section 5):
a Go function or handler, a pure JS or TS function.

- Write the benchmark in the project's tool — Go `Benchmark…` with
  `b.ReportAllocs()`, Vitest `bench`, or the stack's equivalent.
- Write it first, run it on the unchanged code, then on the change; both
  results, with ns/op and allocs/op, go in `Perf-Measure:`.
- Keep rule: the change is also kept when the benchmark, 5 runs each way,
  beats its before median by more than the spread of the 5 before runs, and
  the browser median is not worse by more than its spread. It need not clear
  the browser threshold in one go.
- A gain seen only in the browser (fewer requests, a smaller bundle, less
  re-rendering) gets no benchmark; the browser measurement proves it.
