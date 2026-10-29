---
name: e2e
description: >
  Raises Playwright end-to-end coverage of a Vue 3 + TypeScript frontend one
  route at a time: finds every route and interactive control no spec drives,
  writes specs against the built server and its fake upstream, extends the
  Go fake when a route needs data or an endpoint it lacks, and proves each
  spec can fail. Use to add missing e2e tests, cover a route, a spec, or a
  user flow, or find what the end-to-end suite never exercises.
license: MIT
argument-hint: "[route=NAME|PATH | SPEC.spec.ts | flow=\"TEXT\" | all*]
  [max=N]"
---

# e2e

## Usage

```
/web:e2e                          all routes (default): per route, plan-first
/web:e2e route=settings           one route by name or path; no plan gate
/web:e2e route=/sites/:id         the same, by path
/web:e2e e2e/app.spec.ts          the routes and controls that spec touches, plan-first
/web:e2e flow="pick a site, open a device, go back to its site"   one named flow; no plan gate
/web:e2e max=4                    cap tests added this run
```

Executing skill: it reads the router, the pages, and the specs, writes specs
in `e2e/`, extends the fake upstream and its tests when a route needs it,
builds, and runs Playwright. Unlike `web:review` it acts on the code. Unit
coverage is `web:cover`'s.

**Governing rule — coverage is per route, from specs that drive it.** A route
is covered when a spec navigates to it and asserts what it shows; each
interactive control on it is covered when a spec operates it and asserts the
effect. A route a spec only passes through, or a control it never operates,
is a gap. The route — never the spec file — is the unit of work.

Sources of truth:
- `../style/references/test.md` and `../style/references/production.md`
  (on-demand: before writing a spec — read both files whole: the Test rules,
  "End-to-end (Playwright)" above all, and every Production rule Test
  inherits) — obey them in every spec; do not restate them.
- `go:style`, invoked as a skill (on-demand: before editing any `.go` file of
  the fake) — obey it in every Go change and its tests.
- The Playwright config and the existing specs — the projects, servers,
  ports, and region helpers to reuse.

## Start

1. Resolve the frontend root as `../style/references/checking.md` does, and
   read the Playwright config: its `testDir`, its `webServer` entries (the
   app server and the fake upstream it starts), and its projects. A project
   that needs credentials or a live external service is never run; name it
   in the report and work only with the projects that run against the fake.
2. Run the baseline: `bun run check` from the frontend root, `go test ./...`
   from the repository root, the build the app server needs (`bun run
   build`, or what the config's comments say), and `bunx playwright test
   --project=<fake project>` with each project that runs on the fake — the
   same gates Verify runs at the end. Red: stop and report the failures,
   editing nothing. Playwright browsers missing: stop and say how to install
   them.

## Target

Read the tokens in any order: a reserved word is a mode or flag, `key=value` is
a control, and anything else is the target. `route=` and `flow=` name the
target, not a control.

- route — `route=<name>` (a route name in the router) or `route=<path>` (its
  path pattern). Just that one; run straight, then report.
- spec — a spec file: the routes and controls its tests touch. Plan-first.
- flow — `flow="<text>"`: one user journey across routes, written as one
  test. Run straight.
- all (default) — every route in the router, in its order. Plan-first.

State the resolved kind and the route set before reading the specs.

## Controls

A `key=value` that names no control here, or a word left over once the modes,
the target, and any text the skill takes are read: say it was not recognized,
name the ones that exist, and run with the defaults as if it were absent —
unless dropping it would widen what the run changes; then ask. A target that
resolves to nothing: say so and ask — never guess what to work on.

- `max=N` — hard cap on tests added (one per new `test`); report what
  is left.

## Inventory

For each route in scope, read its page component and the components it
renders, and list:

- the route itself, reached by URL, with what it shows;
- each control a user operates that changes what the page shows or where it
  goes: form fields, pickers, toggles, sort headers, buttons (a retry, a
  dialog's open and close), keyboard shortcuts the page registers, links to
  other routes;
- the shared layout once, not per route: each of its navigation links is one
  control.

A spec drives a control when it operates it (click, fill, select, press) and
then asserts the effect; a locator that only reads it does not. Map each
existing test's steps to the controls by their role and accessible name.
State each gap as `route — control`.

## Per-route loop

For each route, in order. **Never start route B until route A's specs are
written and proven.**

1. Inventory the route and map the existing specs (above).
2. Classify every gap:
   - coverable — the fake upstream serves what it needs, or a per-test
     `page.route` can (a failed answer for a retry, a slow one for a
     spinner);
   - needs the fake — an endpoint or records the fake lacks: extend the fake
     (Fake, below), then cover it;
   - un-coverable — needs a real external service, credentials, or an
     effect no browser shows (an email sent); report with the reason.
3. Write one test per flow, adding to the spec file the route's neighbours
   live in, else a new `e2e/<area>.spec.ts`. Reuse the region helpers; add
   one, documented, when a region needs it. Stop at `max`.
4. Prove each new test, one at a time: run it green; then break the behaviour
   it drives — stash the handler's change, or revert the control's effect in
   the source — rebuild, run it red, restore, rebuild, run it green again.
   A test that stays green with its behaviour broken asserts nothing: fix it
   before the next. Record the red line for the report.

## Plan (spec / all)

Run loop step 1 and step 2's classification for every route in scope, then
present, per route in order: `route — controls driven/total`, the route itself
reached or not; the proposed tests (`spec file` and the route and controls
each drives), under `max` only as many as it allows, with the coverable gaps
left over listed after them; the fake changes the needs-the-fake gaps call
for; and the un-coverable gaps, each as `route — control — reason`. Wait for
approval, then run steps 3–4 route by route.

## Delegated by web:audit

Delegation is recognized from the invocation, never guessed: `web:audit` says
it is invoking for gaps only and passes the route set. A run not told so is not
delegated, and runs its target kind as usual.

Run Start step 1 only, then for every route in the set run the Inventory, map
the existing specs, and classify each gap as Per-route loop step 2 does; return
only the lines below — not Output's labels or its `web:review` pointer — and
stop:
- per route: `file:line route — reached|not reached; controls driven/total`,
  the line being the route's entry in the router;
- each gap as `route — control (writes|recovers|other) — coverable|needs the
  fake|un-coverable (reason)`: `writes` for a control that submits, saves, or
  deletes data, `recovers` for one that retries or leaves an error state, and
  `writes` for one that does both;
- every command run.

No Start baseline, no build, no Playwright or Go run, no spec or fake written,
no Verify, no fan-out — the audit only reads, and a worker cannot dispatch one.

## Fake

When a route needs an endpoint or records the fake upstream lacks:

1. Invoke `go:style` before the first `.go` edit.
2. Extend the fake — its handler and its fixed data — the least that serves
   the route: a new path, new records, a new field. Never change a record an
   existing spec or test asserts on; add new ones.
3. Add Go tests for what the fake now serves, in the fake's test file, per
   `go:style`.
4. Never change the app server or the frontend to suit the fake; a route the
   fake cannot serve without that is a gap to report, not a change to make.
5. Run `go test ./...` from the repository root; it must pass.

## Verify

End of run: `bun run check` from the frontend root, `go test ./...` when Go
changed, and `bun run test` (or the build and every fake-backed project) —
all must pass. A run that edited nothing has nothing to verify: say so.

## Output

Use the labels below verbatim.

- Baseline: each gate the Start step ran and its result, before any edit.
- Route coverage: per route in scope, `route — controls driven before →
  after` (for example `settings — 0/1 → 1/1`), and the route itself
  reached or not.
- Tests added: `spec file:test title` + the route and controls it drives,
  with the red line its proof produced.
- Fake changes: `file:symbol — what it now serves`, and the Go tests added.
- Gaps left: `route — control — reason` (the cap, deferred, or
  un-coverable).
- Projects not run: each with why (credentials, a live service).
- Tests added this run, counted, and under a cap, what is left.

Every number is read off the finished specs and the last Playwright run,
never carried from the work. Report tersely: no preamble or narration; state
each fact once. Suggest running `web:review` on the new specs.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/web/e2e.md` (pass `~` as is, the
file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable; this block never moves or merges lessons. A missing file needs no
comment. On a correction or self-caught mistake, append a one-line rule —
general, naming nothing from the project at hand (its files, tests, tickets) —
to the sibling when this directory is writable (creating it even when only the
fallback holds lessons so far; both stay read), else to the fallback, creating
it, and report where. A lesson write is not a project write: a read-only or
no-change run still makes it.
