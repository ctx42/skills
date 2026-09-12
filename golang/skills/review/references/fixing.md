# review fix path

Read when asked to apply findings, fix, or refactor. Every behavioral code
change ships with tests in the same change — new behavior gets new tests,
changed behavior gets updated tests — written to `golang:style`'s Test rules
(`have`/`want`, never `got`). Pure no-ops (renames, comment edits) are exempt.

## Never print diffs of applied fixes

The edits are already on disk; the user reviews them in git or their editor.
Report each change in one line (`file:sym — what changed`) plus the test/gate
result — never paste the changed code, a before/after block, or a diff.
Red/green proof output (below) is not a diff — report it.

## Refactors: enumerate before editing

Before a rename, signature change, or interface change, use the `LSP` tool to
find everything the edit must touch — `findReferences` for every call site,
`goToImplementation` for every implementer — so the definition and all its
dependents change together. LSP only locates code; edits still go through
Edit/Write. Re-query after writing, since a pre-edit result goes stale. The
test gate (below) remains the proof that no caller broke. No Go language
server → fall back to grep to enumerate call sites.

## Logical bugs: prove before fixing

For any correctness, concurrency, or performance finding — a behavioral bug at
any severity (pure style, doc, and naming are exempt) — reproduce it before
touching the fix:

1. Write a test (or a benchmark for performance) and run it against the
   current code to show it fails; capture the red output.
2. Apply the fix and show the same test/benchmark now passes.
3. Report both states — the bug was real and the fix resolves it.

A bug is always reported, whether or not it can be proven. If it genuinely
cannot be reproduced by a test or benchmark (unreachable branch, untestable
side effect, disproportionate scaffolding), do not apply the fix: report the
bug, state that a fix is available but cannot be proven, say why, and let the
user decide.

For a non-bug change where a test is merely coverage and is impossible or
cost-prohibitive, do not skip it silently: warn the user, name the change left
untested, and say why.

## Test gate

Run the whole-module suite, not just the changed package:

- Before editing, run `go test ./... -race` for a green baseline. If it is
  already red, stop and report the pre-existing failures; do not edit.
- After editing, run `go test ./... -race` again. The job is not done until it
  passes for the whole module; a failing or unrun suite means not done — never
  report success without it.

## Big fix jobs: plan, chunk, consult

When the fix job is broad — findings span several packages or large LOC — do
not edit straight through:

1. Write an ordered plan to a gitignored scratch file
   (`tmp/review-fix-plan.md`): one entry per chunk, each naming the package
   (or file) it covers, the findings to fix there, and status boxes (fixed /
   tests green). A chunk is one package; split a large package (many findings
   or big files) into file-level chunks and note the split. Show the plan and
   get a go-ahead before chunk 1.
2. Work chunks in order. Per chunk: apply its fixes under the rules above, run
   the test gate so the chunk ends green, and tick its plan boxes.
3. Consult after each chunk that produced edits or a decision — report what
   changed (one line per fix, no diff) and the green result, then wait for a
   go-ahead. Auto-continue only a chunk that needed no fixes. Never proceed
   past an unmade decision.

## Committing

Never `git commit`: commits belong to the user. Keep each chunk a
self-contained, separately committable change and say when one is ready;
commit only if the user explicitly asks, and never with a red or unrun suite.
