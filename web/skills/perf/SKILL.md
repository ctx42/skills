---
name: perf
description: >
  Makes a running web app faster one measured, committed fix at a time:
  profiles its UI in a visible Chrome at a 4x CPU slowdown and fixes slow
  interactions, long tasks, layout shift, memory leaks, wasted requests, and
  bundle bloat without changing what users see. Use to speed up or profile a
  web app, page, or interaction, front end or back end.
argument-hint: "[auto] [loop] [max <n>] [<focus>]"
license: MIT
---

# perf

## Usage

```
/web:perf                   measure the app, build the top fix, stop for commit, drop, or a prompt
/web:perf auto              the same, committing without stopping
/web:perf loop              one change after another until the stop rule
/web:perf auto loop max 5   unattended, at most 5 commits
/web:perf <focus>           do what the focus asks to the part it names or a screenshot shows
```

`auto`, `loop`, and `max <n>` are leading keywords in any order; the first
other token starts the focus, free text to the end. A pasted image, or an image
path in the focus, shows the part. `max <n>` counts commits only — drops and
discarded failures do not count — and needs `loop`: given without it, say
"`max` needs `loop`" and stop before any other step. Without `loop` a run makes
at most one change, committed, dropped, or discarded. No focus measures the
whole app. The CPU slowdown is fixed at 4x; no keyword changes it.

Arguments: $ARGUMENTS

Report tersely: no preamble or narration; state each fact once. Never push,
amend, rebase, or touch a commit the run did not make.

The goal is code that runs faster or uses less memory, never at the cost of
architecture, readability, or testability (section 5).

## 1. Start — before any edit

Check in order. The first that fails is named as the missing prerequisite and
the run stops, editing and committing nothing:

1. The working directory is a web app's source tree: markup, styles, or
   scripts the app serves, beside a manifest or dev config (`package.json`, a
   framework or bundler config, a `Makefile` target that serves it).
2. A dev server is reachable. Never start one, even when the config says how.
   Take candidate URLs from the dev config (a script's `--port`,
   `server.port`, `.env` `PORT`, compose ports, the framework's default),
   cross-check them with the listening ports (`ss -ltnp`), and probe each with
   `curl -sS -o /dev/null -w '%{http_code}'`. Nothing listening: stop. One
   match: that URL. Several, or ports listening but none matching the config:
   ask which URL in the step 9 message, not before it.
3. Chrome DevTools MCP is available (`new_page`, `emulate`, `click`,
   `evaluate_script`, `list_network_requests`, `take_heapsnapshot`) and its
   window is visible: open the URL with `new_page`; a `navigator.userAgent`
   containing `HeadlessChrome` means headless — say to restart the MCP server
   without `--headless`.
4. The craft plugin is installed: `craft:cm` is in your skill list.

Then:

5. Record the start commit (`git rev-parse HEAD`) and the dirty files
   (`git status --porcelain`). Make a scratch directory outside the repo
   (`mktemp -d`); every build, trace, snapshot, and capture of the run goes
   there, never into the tree.
6. Back end: the server answering the app's API (the dev config's proxy
   target, or the origin of the API requests the page makes), if its source is
   in this repo. Back-end edits are on only when its dev setup live-reloads
   (air, nodemon, `node --watch`, `tsx watch`, `uvicorn --reload`, a file
   watcher wrapping the server); otherwise every back-end idea goes to
   Recommendations.
7. Build: the repo's build command (a `package.json` `build` script, a
   `Makefile` target). It runs only with its output pointed at the scratch
   directory (`vite build --outDir <scratch>/build`, the bundler's equivalent
   flag) — a plain build empties the project's output directory, deleting
   tracked files and replacing what a server may embed. No build command, or
   no way to redirect its output: skip bundle findings and say so under Not
   measured.
8. Find the project's checks as `craft:fix-all` finds them — `AGENTS.md`,
   `CLAUDE.md`, `CONTRIBUTING.md`, a `Makefile`, the package manifest: build,
   test, lint, format, e2e included — and run them once on the untouched tree.
   A check already red there is known: name it in the message below, and
   leave it out of every gate (run the others by name) — it never blocks a
   commit.
9. Send one message and wait: the detected URL, open in the Chrome window,
   whether back-end edits are on or off and why, and a request to log in there
   if the app needs it, then reply (or give the right URL). When the user's
   instructions or the harness forbid committing, the same message asks leave
   to commit every change of this run, as `craft:fix-all` does. A reply
   without that leave: list the ranked findings the run would act on, write no
   report, and stop before any edit — never edit and leave the change
   uncommitted instead. An app with no login proceeds on the reply. The start
   asks nothing else.

## 2. Measure

Every measurement runs under `emulate` with `cpuThrottlingRate: 4` — each
`emulate` call replaces all settings, so pass it every time — and no network
throttling. Interactions, a view's load (its long tasks and layout shift),
and API calls are measured on the dev server; bundle size only from the
scratch build, never from the dev server. How to take each
number: [references/measure.md](references/measure.md).

Scope: with no focus, every page reachable from the app's navigation (its
shared header, sidebar, menus, and footer); with a focus, only the views that
show the focused part. Play with each view the way a user reads it: navigate,
sort, filter, page, search, expand, scroll long lists, open and close dialogs
without submitting. Never click logout, nor trigger a write — a POST, PUT,
PATCH, or DELETE — unless the focus names that flow. Watch the network log
after every action; a write seen outside a named flow means that control is
never used again this run and goes under Not measured.

Findings — a timed one exists only while past its threshold:

- Slow interaction: INP over 200 ms.
- Long task: over 50 ms during an interaction or a view's load.
- Layout shift: CLS over 0.1.
- Leak: a view whose heap size in bytes, after a forced GC, grows by more than
  50 KB on every one of 5 navigate-away-and-back cycles; smaller growth is the
  browser's own bookkeeping, and a heap that levels off is no leak. A heap
  snapshot then names what is retained (detached nodes, listeners, timers).

A counted one is a finding at every instance:

- A duplicate request: the same method and URL twice in one view's load.
- Sequential independent calls: one starts after another ends though it needs
  nothing from that response.
- A route or library in the first-load bundle that could load lazily.
- A library imported whole when it offers per-function entry points.

Noise: a timed metric is measured 5 times and its median used; a counted one
once. A change is kept only when its after median beats the before median by
more than the spread (max − min) of the 5 before runs; for a counted metric any
reduction counts. A leak is measured by one series of 5 cycles, before and
after; a leak fix is kept when the after series is no longer a leak. A change
with a benchmark (section 5) is also kept when the benchmark, 5 runs each way,
passes that test and the browser median is not worse by more than its spread.
It need not clear the threshold in one go. A change with no
gain beyond that is discarded and listed under Dropped, "no measurable gain" —
a focus instruction included.

Before choosing a change, search the source for `PERF:` comments
(`grep -rn 'PERF:'`, skipping dependency and build dirs). A `PERF:` comment is
the only binding previous decision: it states what never to do at the code it
sits on. Never act against one unless the focus asks for what it forbids
(section 4); a finding it
forbids goes to Recommendations, citing the comment. Test assertions and
earlier commits do not bind. A `UX:` comment governs what users see, which no
commit here changes, so it never blocks a fix (section 10 flags it).

Rank, top first:

1. Timed findings, the worst ratio of value to threshold first; a leak ranks
   above every other timed finding.
2. Network waste: duplicate requests and sequential calls.
3. Bundle findings.
4. Within a tier, shared chrome (header, navigation, footer, a layout every
   page uses) and the landing page before deeper pages; ties go to the
   smaller change.

## 3. Back end

Back-end code in this repo may change, its API included, only when start step
6 turned back-end edits on. APIs outside the repo are never changed: what would
help there (a field, a batch call, caching headers) goes to Recommendations as
feedback for their owners.

Merge two calls into one endpoint only when all hold: the view makes both on
every load; they run one after the other, or are always fired together; their
data describes one resource (a list and its counts or statuses). Never add an
endpoint bundling unrelated resources for one page. Keep an old endpoint while
anything else in the repo calls it; remove it in the same commit once nothing
does. Anything outside this rule goes to Recommendations. With back-end edits
off, a pair the rule allows that still runs one after the other at the end
goes there under Back end without live reload; one fired together does not.

After a back-end edit, measure only once the reloaded server answers: the
listening process's PID (`ss -ltnp`) has changed and the API responds. No
restart within 60 s means the build failed or nothing reloaded — treat it as a
red check (section 6, step 6).

## 4. Focus

A focus — any text after the keywords — names a part of the UI or shows it in a
screenshot, with what the user wants; one naming only a part measures that
part. The description is an instruction. It beats a `PERF:` comment, which the
same commit removes, its body saying so. It may require a visible change it
names explicitly (pagination, virtualization, a debounce), which then carries
picture pairs (section 6, step 2). The instruction is the run's first change;
with `loop`, the run then keeps improving that part by the normal rules. With
a focus, no commit touches code outside the focused part and what serves it; a
fix that would goes to Recommendations.

## 5. What a change may be

- **Nothing the user sees changes.** Pagination, virtualization, debounce
  delays, new loading placeholders, and reordered content go to
  Recommendations unless a focus names them. Content appearing sooner is the
  goal, not a change. Proof: the visible-change check in
  [references/measure.md](references/measure.md#visible-change-check) passes
  on every view the change touches.
- **Tests.** Every code path a change adds — a cache and its invalidation, a
  merged endpoint, a lazy boundary — gets unit or integration tests in the
  same commit.
- **Benchmarks.** A gain in code that runs in isolation (a Go function or
  handler, a pure JS or TS function) also gets a benchmark in the project's
  tool — Go `Benchmark…` with `b.ReportAllocs()`, Vitest `bench`, or the
  stack's equivalent. Write it first, run it on the unchanged code, then on
  the change; both results go in `Perf-Measure:`. A gain seen only in the
  browser (fewer requests, a smaller bundle, less re-rendering) is proved by
  the browser measurement.
- **Never, for speed:** duplicate or inline logic, bypass a layer (a handler
  querying storage directly, a component calling an API a store owns), add
  global mutable state, weaken or delete a test, or hand-roll what the
  framework provides (`computed`, `useMemo`, lazy routes, async components).
- Before committing, reread the diff against the project's conventions
  (`AGENTS.md`, `CLAUDE.md`, the linters). A gain that needs one of these
  rules broken goes to Recommendations, naming the rule.

## 6. Change cycle

One commit per performance change. One rule applied in several places is one
commit; unrelated changes never share a commit. Per change:

1. Pick the top-ranked finding not dropped this run, not forbidden by a
   `PERF:` comment (a focus instruction beats one, section 4), allowed by
   sections 3 to 5, and touching no file the start found dirty (that one goes
   to Recommendations, naming the file — a focus instruction included).
2. Before any edit, take the 5 before measurements of the finding's metric and
   the visible-change check's two before captures of each view the change will
   touch. A visible change a focus named also deletes every untracked
   `dev/perf/*.png`; its pictures come at step 5. One pair is
   `dev/perf/before.png` and `dev/perf/after.png`; several are `before-1.png`
   and `after-1.png` on, numbered as in the message. No other change writes
   into `dev/perf/`.
3. Make the smallest change that fixes the finding, with its tests and any
   benchmark (section 5).
4. Reload (wait for the back end, section 3) and take the 5 after
   measurements. No gain beyond the noise: discard the change (restore its
   files, delete its new files) and list it under Dropped, "no measurable
   gain".
5. Run the visible-change check; a mismatch discards the change and lists the
   idea under Recommendations as a visible change. A focus-named visible
   change skips it and shoots its pictures, after first: per touched view,
   scroll to the first element the change adds (a pager, a placeholder, a
   "load more" button), else to where it removed content, and
   `take_screenshot` with `filePath`;
   then `git stash push -u -- <the change's files>`, reload, shoot `before`
   at the same scroll, and `git stash pop`.
6. Run the project's checks on exit status, never on piped or filtered output.
   A check red that was green at the start gets one repair; still red: under
   `auto`, discard the change and list it under Dropped with the failing
   check; interactive, show the failure at the stop.
7. Interactive: stop (section 8). `auto`: commit.
8. Commit: unstage everything (`git restore --staged .`), stage the change's
   files and pictures by path (`git add -f -- <paths>`, so an ignored `dev/`
   still ships them), `git rm -q --` every tracked `dev/perf/*.png` this
   commit did not write, and write the message (section 7). Then, in one
   command, re-run the checks gated on exit status
   (`make check >out 2>&1 || exit 1`), compare `git diff --cached --name-only`
   with that list, and `git commit -F -`. A red re-run commits nothing and
   returns to step 6.

## 7. Commit message

Invoke `craft:cm` at `mini` on the staged diff for the summary and body. After
its body, before any footer it wrote, append the fields wrapped at 72 columns,
continuation lines indented two spaces:

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

`Perf-Finding:` the metric, its threshold, and where it breaks;
`Perf-Change:` what changed; `Perf-Measure:` before -> after with the method,
plus a benchmark's ns/op and allocs/op before and after; `Perf-Pictures:` each
pair's view and state, numbered as the files, only on a commit carrying
pictures. A `docs(perf): never …` commit carries `Perf-Finding:` alone. Never
add a trailer beyond what `cm` allows.

## 8. Interactive stops

Without `auto`, stop once per change, after building, measuring, and checking
it. A change with no gain beyond the noise never reaches a stop; it is dropped.

```
Change 2 — Devices: search input runs a 180 ms long task per keystroke
Change: dedupe tags with a Set instead of a nested scan
Measure: long task 180 -> 30 ms, median of 5 at 4x CPU; bench 9.1 -> 0.4 ms/op
Checks: pass
Reply: commit · drop · or say what to change
```

- `commit`: commit it (section 6, step 8). While a check is red, say so and
  stop again instead.
- `drop`: restore the tree as it was before the change, pictures included;
  its finding is not taken up again this run, by that change, part of it, or
  any other fix; a user wanting a different fix replies with a prompt, not
  `drop`. Drops are remembered for the current run only.
- Anything else is a prompt: rework the change, re-measure, re-run the
  visible-change check and the checks, and stop again, with no commit in
  between.
- A reply saying "never …" also writes a `PERF: never …` comment, in the file's
  comment syntax, at the code concerned: into that change's commit, or on a
  drop into its own commit adding that comment alone — summary
  `docs(perf): never <x>`, no body, `Perf-Finding:` only. That commit counts
  toward `max` like any other; without `loop`, the drop still ends the run.
- A reply asking to stop ends the run.

## 9. Loop and stop rule

With `loop`, after each commit or drop, re-measure the views the change touched
and take the next finding. Stop when no remaining finding past its threshold,
or counted, is one the run may fix — counting only findings not dropped, not
forbidden, and not blocked by sections 3 to 5 or a dirty file — or when the run
has made `max` commits. No cap by default. Before stopping on the stop rule,
measure the whole scope once more: a fix can move cost elsewhere, and a new
finding there continues the loop. Without `loop`, stop after one change,
committed, dropped, or discarded. Once stopped, list every finding left
under Recommendations, whatever kept the run from it; ideas dropped or
discarded this run go under Dropped.

## 10. Report

Read every count and hash off `git log <start>..HEAD`, never from memory.
Interactive runs end with the same report.

```
2 commits, 1 dropped; stopped: stop rule

| Commit  | Summary                                       | Before -> After   |
|---------|-----------------------------------------------|-------------------|
| a1b2c3d | perf(devices): insert the device rows at once | INP 610 -> 140 ms |

Dropped
- Settings: memoize the form — no measurable gain

Recommendations
- External API: the asset service has no batch lookup; one call per device
- Back end without live reload: merge /api/devices and /api/device-status
- Visible change: virtualize the 2000-row device list (long task 120 ms)

Not measured
- Bundle: no build command
- Settings save: a write flow, not in the focus
```

`N` counts the commits `git log <start>..HEAD` lists; `M` counts drops and
discarded failures. The reason is `stop rule`, `max reached`, `single run`, or
`user`. Recommendations group under: External API, Own API outside the merge
rule, Back end without live reload, Visible change, Code quality (naming the
rule a gain would break); one that contradicts a `UX:` comment names that
comment's location. Size each table column from its longest cell before
writing the table. Omit an empty section.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/web/perf.md` (pass `~` as is,
the file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable. A missing file needs no comment. On a correction or self-caught
mistake, append a one-line rule — general, naming nothing from the project at
hand (its files, tests, tickets) — to the sibling when this directory is
writable, else to the fallback, creating it, and report where.
