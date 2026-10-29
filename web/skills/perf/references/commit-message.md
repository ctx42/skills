# Commit message

How `perf` writes and makes a change commit (SKILL.md section 6, step 8, and
section 7). Read before the first commit.

## Fields

Invoke `craft:cm` at `mini` on the staged diff for the summary and body. After
its body, before any footer it wrote, append the fields wrapped at 72 columns,
continuation lines indented two spaces, as the example below shows:

`Perf-Finding:` the metric, its threshold, and where it breaks; `Perf-Change:`
what changed; `Perf-Measure:` before -> after with the method, and any
benchmark's; `Perf-Pictures:` each pair's view and state, numbered as the files,
only on a commit carrying pictures. A `docs(perf): never …` commit carries
`Perf-Finding:` alone. Never add a trailer beyond what `cm` allows.

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

## Committing

Unstage everything (`git restore --staged .`), stage the change's files and
pictures by path (`git add -f -- <paths>`, so an ignored `dev/` still ships
them), `git rm -q --` every tracked `dev/perf/*.png` this commit did not write,
and write the message (Fields). Then, in one command, re-run the targeted
checks, each gated on exit status (`<check> ><scratch>/out 2>&1 || exit 1`), a
known test check on its failing test names instead (SKILL.md section 1, step
8), compare `git diff --cached --name-only` with that list, and
`git commit -F -`. A red re-run commits nothing and returns to SKILL.md section
6, step 4, one repair per change in all.
