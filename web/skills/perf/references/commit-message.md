# Commit message

The shape of a change commit (SKILL.md section 7): `craft:cm`'s summary and
body, then the fields, wrapped at 72 columns, continuation lines indented two
spaces.

```
perf(devices): insert the device rows at once

Each appended row read offsetHeight, forcing a layout per row, so
sorting 2000 devices blocked the page.

Perf-Finding: sorting the device list takes INP 610 ms at 4x CPU
  (good <= 200 ms)
Perf-Change: build the rows in a fragment and insert them once
Perf-Measure: INP 610 -> 140 ms, median of 5 at 4x CPU (before
  spread 40 ms)
```
