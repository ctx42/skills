---
name: review
description: >
  Done-time Go quality review. Runs after edits and features are complete on the
  current diff, a package, or a whole module. Checks Go code against the
  style rules, the deeper criteria in rules.md, and general correctness
  (bugs, edge cases, error handling). The default review reasons only, running
  no build or test tools; an opt-in fix path applies findings and runs the test
  suite to prove them. Broad fix jobs are planned to a file and applied package
  by package, consulting before each commit. Honors budget controls (packages,
  max_issues, depth, plan_first). Also grows the rule list —
  from a plain-language prompt or by mining the current editing session for your
  feedback.
license: MIT
---

# review

Final-gate review for Go code. Pick the mode from the invocation:

- **Check** (default) — audit finished code.
- **Rule edit** — when the input is a style preference or asks to
  `add`/`change`/`remove` a rule.
- **Learn** — when asked to learn from this session / your feedback; mines the
  current editing session (since the last /clear) for convention feedback and
  proposes rules.

Sources of truth:
- `../style/SKILL.md` — canonical terse rules (Production + Test).
- `rules.md` — deeper rationale / examples / how-to-detect, keyed
  to those rules. Consult it for non-obvious rules.

In every mode, report tersely: no preamble or narration; state each fact once;
don't restate output the user can already see.

## Self-learning

Read this skill's lessons first and obey them: the sibling `LESSONS.md`, plus —
when this skill's directory is not writable (an installed copy) —
`$HOME/.agent-data/ctx42-skills/lessons/golang/review.md`. When the user
corrects you, or you catch your own mistake, append the fix as a one-line rule to
whichever is writable (the sibling in a source checkout, else the `.agent-data`
file, creating it), then report where — so it never recurs.

## Check mode

### Target

Resolve what to review from the invocation:
- **no target** — the current git diff vs the base branch (staged + unstaged).
- **a package** — a path like `./pkg/foo` or an import path; review that one
  package's `.go` files.
- **a module / many packages** — `./...`, a directory containing `go.mod`, or
  an explicit "module"; review every package in the module.

State the resolved target and the exact package/file set before reviewing.

### Budget & scope

Parse and respect these controls from the invocation:
- `packages=a,b` — restrict to these packages within the target.
- `max_issues=N` — hard cap on findings reported (default 25).
- `depth=light|standard|exhaustive` — default `standard`.
- `plan_first` — produce a short prioritized plan plus the top findings, then
  stop for approval before the full pass.

Default to plan-first: if the target is broad (whole module, many packages, or
large LOC) and no budget was given, switch to `plan_first` automatically,
propose defaults (`max_issues=25`, `depth=standard`, the package list), and ask
before the full review.

Depth:
- `light` — only blockers and major maintainability; minimal examples.
- `standard` — balanced coverage of the target.
- `exhaustive` — full deep review; use sparingly.

Stop at `max_issues`; report highest-severity first and say how many findings
were left unreported.

### Workflow

1. Resolve the target and budget (above) and list the packages/files in scope.
2. Read `style`'s `SKILL.md` in full and skim `rules.md`'s **Principles**
   section. Reason from those principles; open a specific keyed `rules.md` entry
   only when about to flag its rule — never preload the whole file.
3. Review each file, in this order:
   - **Rules**: every applicable style rule (Production for `*.go`, Test for
     `*_test.go`); use `rules.md` for detection detail.
   - **Correctness**: bugs, wrong logic, nil/bounds, ignored errors, data races.
   - **Edge cases**: empty/large/concurrent inputs and every error path.
   - **Error handling & API**: wrapping, sentinels, boundaries, easy misuse.
   - **Cross-boundary verify** (`depth=standard`+): before reporting any claim
     that reaches beyond the diff — a symbol is unused, all callers handle an
     error/nil, an interface is fully implemented, a suspect branch is
     reachable — confirm it with the `LSP` tool (`findReferences`,
     `goToImplementation`, `incomingCalls`, `hover`/`goToDefinition`) instead of
     asserting from the visible code. Skip at `depth=light`; reserve for
     findings that actually cross a file/package boundary, not every line. If no
     Go language server is configured the tool errors — fall back to grep/read
     and note the reduced confidence in the finding.
4. Reason only. Do not run gofmt, go vet, golangci-lint, or go test — judge by
   reading the code. The `LSP` tool is permitted: it is read-only semantic
   navigation, not the build/test toolchain, and does not mutate code.
5. Report findings (below). Do not change code unless asked.

### Scale

- **Single package or small module (<= ~6 packages)**: review in this context,
  package by package, highest-risk first.
- **Larger module (> ~6 packages)**: fan out one review subagent per package
  (each gets `style`, `rules.md`, the `depth`, and a share of `max_issues`),
  then synthesize one merged report, re-ranking findings to the global
  `max_issues` cap. Keeps the main context lean.
- Always report which packages were reviewed and which, if any, were skipped.

### Output

Group by severity: **Blocker / Should-fix / Nit**. Each finding:
- `file:line` — the problem in one line.
- The rule id or dimension (e.g. `style: %w`, `correctness`).
- A minimal suggested fix.

End with a one-line verdict (ship / fix-first) and the per-severity counts. For
a module, give the verdict per package plus an overall summary. Report budget
usage: `depth`, packages/files reviewed, and whether you stayed under
`max_issues` (and how many findings went unreported).

### Scope control

Bound the work to the resolved target. If even that is too large, review the
highest-risk packages first and say what you skipped. Never silently truncate.

### Applying fixes

When asked to change code (apply findings, fix, refactor), every code change
ships with accompanying tests in the same change — new behavior gets new tests,
changed behavior gets updated tests. This covers behavioral changes, not pure
no-ops like renames or comment edits.

**Refactors: enumerate before editing.** Before a rename, signature change, or
interface change, use the `LSP` tool to find everything the edit must touch —
`findReferences` for every call site, `goToImplementation` for every implementer
— so the definition and all its dependents change together. The tool only
locates code; the edits themselves still go through Edit/Write, and it performs
no rename for you. Re-query after writing, since a pre-edit result goes stale.
LSP is not the safety net: the `go test ./... -race` gate below remains the
proof that no caller broke. If no Go language server is configured, fall back to
grep to enumerate call sites.

**Logical bugs: prove before fixing.** For any correctness, concurrency, or
performance finding — a behavioral bug at any severity (pure style, doc, and
naming are exempt) — reproduce it before touching the fix:

1. Write a test (or a benchmark for performance) and run it against the
   current code to show it **fails**; capture the red output.
2. Apply the fix and show the same test/benchmark now **passes**.
3. Report both states — the bug was real and the fix resolves it.

A bug is **always reported**, whether or not it can be proven. If it genuinely
cannot be reproduced by a test or benchmark (cost-prohibitive or very hard —
unreachable branch, untestable side effect, disproportionate scaffolding), **do
not apply the fix**: report the bug, state that a fix is available but cannot be
proven by test/benchmark, say why, and let the user decide whether to implement
it.

For a non-bug change where a test is merely coverage and is impossible or
cost-prohibitive, do not skip it silently: **warn the user**, name the change
left untested, and say why.

Run the whole-module suite, not just the changed package:

- **Before editing**, run `go test ./... -race` for a green baseline. If it is
  already red, **stop and report** the pre-existing failures; do not edit.
- **After editing**, run `go test ./... -race` again — in a chunked job (below),
  after each chunk so every chunk ends green. The job is not done until it passes
  for the whole module. A failing or unrun suite means not done — never report
  success without it.

(This gate is for the fix path only; Check mode stays reason-only.)

**Committing.** The fix path may `git commit` applied fixes, but **never without
an explicit consult**. Propose the commit — a conventional-commit summary of the
change — and commit only on approval; the user decides commit-now or defer. Never
commit a red or unrun suite.

**Big fix jobs: plan, chunk, consult.** When the fix job is broad — findings span
several packages or large LOC — do not edit straight through:

1. Write an ordered plan to a gitignored scratch file (`tmp/review-fix-plan.md`):
   one entry per chunk, each naming the package (or file) it covers, the findings
   to fix there, and status boxes (fixed / tests green / committed). A chunk is one
   package; split a large package (many findings or big files) into file-level
   chunks and note the split. Show the plan and get a go-ahead before chunk 1.
2. Work chunks in order. Per chunk: apply its fixes under the rules above, run the
   whole-module gate so the chunk ends green, and tick its plan boxes.
3. Consult after each chunk that produced edits or a decision — show the change and
   the green result, then ask commit-now-or-defer per **Committing**. Auto-continue
   only a chunk that needed no fixes. Never proceed past an unmade decision.

## Rule-edit mode

Triggered when the input is a preference or asks to add/change/remove a rule.

> **Writes must reach the repo.** This mode edits `../style/SKILL.md` and
> `rules.md` in place, relative to the running plugin copy. Rules only stick if
> that copy is the git clone (loaded via `claude --plugin-dir ./golang`), so the
> change can be committed and shared. If this skill is running from a marketplace
> install (a copy under `~/.claude/plugins/cache/`), the edit lands in that
> throwaway copy and is lost on the next update — warn the user and have them
> re-run from the clone before writing.

1. Read `style`'s `SKILL.md`.
2. Turn the input into rule entries shaped per **How a rule entry should
   look** below. If the scope is ambiguous, ask one quick question.
3. Detect duplicate or conflicting rules; show them and the proposed change,
   then **wait** for confirmation before writing. Never silently overwrite a
   conflicting rule.
4. Write the rule to `style`; add a keyed `rules.md` entry only when the
   rule is non-obvious.
5. Show the before/after diff.

## Learn mode

Triggered when asked to learn from the session / your feedback (e.g. `/review
learn`). Turns the corrections you gave while editing Go this session into
durable rules. Same repo-copy caveat and write path as Rule-edit mode.

1. Warn if running from a marketplace copy (see Rule-edit mode) before writing.
2. Gather two signals since the last /clear: (a) feedback you gave on Go code —
   corrections, "do X not Y", requested renames/refactors, accepted or rejected
   suggestions; (b) the diff those turns produced (`git diff` and the session's
   edits). Pair each piece of feedback with the before/after hunk that resolved
   it. The diff corroborates and illustrates feedback — it is not an independent
   source; never mine a rule from code the user never commented on.
3. Keep only **generalizable convention** — a rule that applies beyond the one
   site. Drop task-specific instructions (one-off logic, a lone rename with no
   pattern). When unsure, keep it as a candidate and let the user cut it.
4. Distill each into a terse rule per **How a rule entry should look**, using the
   paired hunk as its before/after example; classify Production/Test/both;
   dedupe against existing `style` rules.
5. Present candidates as a list — each with its provenance (the session moment
   that prompted it), flagging duplicates/conflicts. **Wait** for the user to
   pick which to keep; never write unpicked or conflicting rules.
6. Write the chosen rules via Rule-edit mode's path (steps 4–5): `style` line +
   keyed `rules.md` entry when non-obvious; show the before/after diff.

### How a rule entry should look

- One rule = one concept = one dense imperative line.
- State it generically: name the construct, not the site — no project
  identifiers, domain nouns, or file names in the prose (`the receiver`, not
  `page`).
- Cut every word the rule survives without.
- Scope it Production (`*.go`), Test (`*_test.go`), or both; place it in that
  section, grouped near related rules.
- Examples may show only generic Go syntax (`ErrXxx`, `[Type]`,
  `//nolint:name`); never project-specific identifiers.
- Prefer no example when the prose stands alone; add one only to remove
  ambiguity.
- Deeper rationale or detection detail goes in `rules.md`, keyed to the rule
  and only when non-obvious; keep both files lean.
