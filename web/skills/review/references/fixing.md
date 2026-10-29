# review fix path

Read when asked to apply findings, fix, or refactor. Every behavioural code
change ships with tests in the same change — new behaviour gets new tests,
changed behaviour updated ones — written to `web:style`'s Test rules. Pure
no-ops (renames, comment edits) are exempt. Run every command from the
frontend root unless it is a Go one.

## Never print diffs of applied fixes

The edits are on disk; the user reviews them in git or the editor. Report
each change in one line (`file:symbol — what changed`) plus the gate result —
never the changed code, a before/after block, or a diff. Red/green proof
output (below) is not a diff — report it.

## Refactors: enumerate before editing

Before a rename, a moved export, or a changed prop, emit, or store member,
find everything the edit must touch with the `LSP` tool (references, and
template uses `LSP` misses: grep the kebab-case and camelCase names in `.vue`
files) so the definition and its users change together. Re-query after
writing.

## Logical bugs: prove before fixing

For a correctness or contract finding — a behavioural bug at any severity
(style, docs, and naming are exempt) — reproduce it before touching the fix:

1. Write a Vitest test (a Playwright one only for what happy-dom cannot show)
   and run it alone against the current code to show it fails; capture the
   red output.
2. Apply the fix and show the same test passes.
3. Report both states.

A leak is proved by observing the leaked resource: spy on
`window.removeEventListener` (or the library's `destroy`) and assert the call
after unmounting, or count the listeners a fake target holds. A contract fix
on the Go side is proved by the Go handler's test, red then green, with the
TS side's normalizer test beside it.

A bug is always reported, whether or not it can be proven. If no test can
reproduce it, do not apply the fix: report the bug, state that a fix is
available but cannot be proven, say why, and let the user decide.

## Test gate

- Before editing, run `bun run check` (and `go test ./...` from the
  repository root when the fixes touch Go) for a green baseline. Already red:
  check `git status` first; with uncommitted changes, rerun on `HEAD` in a
  clean worktree. Red there too: stop and report the pre-existing failures,
  editing nothing.
- After editing, run the same commands again; the job is not done until they
  pass. When the project defines `bun run test` (unit, build, e2e), run it once
  before reporting the last chunk ready.
- Gate on exit status, never on piped or filtered output.

## Big fix jobs: plan, chunk, consult

When the fixes span several directories or many lines, write an ordered plan
to a gitignored scratch file (`tmp/review-fix-plan.md`), one chunk per
directory (the contract fixes their own chunk), with status boxes; show it and
get a go-ahead before chunk 1. Per chunk: apply, run the gate, tick the boxes,
report one line per fix and the result, and wait for a go-ahead. Auto-continue
only past a chunk that needed no fixes.

## Committing

Never `git commit`: commits belong to the user. Keep each chunk a
self-contained, separately committable change and say when one is ready.
Aggregate style-only fixes into one change; keep each behavioural fix, with
its red/green test, a separate change.
