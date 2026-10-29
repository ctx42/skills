---
name: review
description: >
  Done-time Go quality review: checks finished code — the current diff, a
  package, or a whole module — against the project style rules and for
  general correctness (bugs, edge cases, error handling). Use after edits or
  a feature are complete, and to add, change, or learn style rules from
  feedback.
license: MIT
argument-hint: "[func=NAME | FILE:LINE | FILE.go | ./pkg | all |
  add|change|remove RULE | learn] [packages=a,b] [max=N]
  [depth=light|standard*|full] [plan_first] [fix]"
---

# review

## Usage

```
/go:review                                       check (default): review the current git diff
/go:review func=Parse                            review one function (func=T.Bar: a method)
/go:review pkg/foo/foo.go:42                     review the function enclosing that line
/go:review pkg/foo/foo.go                        review one file
/go:review ./pkg/foo                             review one package
/go:review all                                   review every package of the module
/go:review /path/to/project                      review that module (a go.mod dir)
/go:review all max=15 depth=light                cap findings; set review depth
/go:review all packages=parser,lexer             restrict to these packages
/go:review all plan_first                        propose the budget, then stop for approval
/go:review ./pkg/foo fix                         review, then apply the findings
/go:review add "no naked returns in tests"       add a style rule
/go:review change "receivers are three letters"  refine an existing style rule
/go:review remove "the compile-time check rule"  remove a style rule
/go:review learn                                 mine this session's feedback into rules
```

Done-time review for Go code. Read the tokens in any order: a reserved word is a
mode or flag, `key=value` is a control, and anything else is the target. `func=`
names the target, not a control. The mode:

- Check (default) — no mode word; audit the target's finished code, then offer
  the rules this session taught (Session rules).
- Rule edit — `add`/`change`/`remove`, everything after it being the rule text,
  reserved words included, or input that is a plain style preference.
- Learn — `learn`; mines the current editing session (since the last /clear)
  for convention feedback and proposes rules.

Sources of truth:
- `go:style` (on-demand: Check mode) — owns the style rules and their
  detection; the whole style dimension is delegated to it.
- `../style/references/production.md`, `../style/references/test.md`,
  `../style/rules.md` (on-demand: Rule-edit/Learn) — the terse Production and
  Test rules and their keyed detection detail; those modes write here.

In every mode, report tersely: no preamble or narration; state each fact once;
don't restate output the user can already see.

## Check mode

### Target

The target token is:
- empty — run `git diff HEAD` (staged and unstaged together) and review that
  working diff; on a branch with no commits, where `HEAD` does not resolve,
  run `git diff --cached` and then `git diff` instead. If the working diff is
  empty, the branch's own work is the target: diff it against the base branch
  (`git diff <base>...HEAD`) and say which of the two you reviewed. On a
  branch with no commits, an empty working diff leaves nothing to review: say
  so and ask for a target. Once this session has made fixes, by this skill or
  any other, committed or not, the empty target is instead the diff from the
  commit before the first fix (`git diff <commit>`), whatever the working diff
  and the base-branch fallback hold: a fix to identity, nil,
  or undo logic regresses the inputs beside it. With no commit before the
  first fix, the no-commits fallback above stands. A named target below runs
  none of these diffs.
- `func=NAME` or `func=T.Bar` — that function or method; `FILE:LINE` — the
  function enclosing that line; `FILE.go` — that file. Review just that code,
  style included; read beyond it only to verify a finding. A name matching in
  more than one package: say which and ask.
- a package — a path like `./pkg/foo` or an import path; review that one
  package's `.go` files.
- `all` — every package in the current module. A package pattern (`./...`,
  `./pkg/...`) or a directory holding `go.mod` stays a path target: review
  every package it matches.

State the resolved target and the exact package/file set before reviewing.

### Budget & scope

Controls and flags, read from `$ARGUMENTS`:
- `packages=a,b` — restrict to these packages within the target.
- `max=N` — hard cap on findings reported (default 25); stop there,
  highest severity first.
- `depth=light|standard|full` — default `standard`. `light` reports only
  blockers and major maintainability with minimal examples; `full` reviews
  everything deeply — use sparingly.
- `plan_first` — propose the budget and the package list, then stop for the
  user's answer. Propose-then-stop, not review-everything-then-present: the
  point is to agree what the run will cost before spending it, and findings
  presented alongside the proposal have already spent it.
- `fix` — after reviewing, apply the findings (see Applying fixes).

A `key=value` that names no control here, or a word left over once the modes,
the target, and any text the skill takes are read: say it was not recognized,
name the ones that exist, and run with the defaults as if it were absent —
unless dropping it would widen what the run changes; then ask. A target that
resolves to nothing: say so and ask — never guess what to work on.

Default to plan-first: if the target is broad and no budget was given, switch
to `plan_first` automatically, propose defaults (the caps above, the package
list), and ask before the full review. Broad means more than ~6 packages, or
comparable LOC in fewer. Whether a broad run fans out is a separate call made
by size (Scale): many packages under ~500 lines of Go in all are reviewed in
this context, and the plan-first proposal says which and why. That is the
same threshold `go:style` uses, deliberately: the two skills share a target and
a budget, and an `all` that is broad to one and not to the other cannot be
delegated coherently. A module of three small packages is `all` and still not
broad.

### Workflow

1. Resolve the target and budget (above) and list the packages/files in scope.
2. Style dimension — invoke `go:style` with the resolved target and budget
   (`packages`, `depth`), instructing it to report offenses only. Take its
   offense list as the style findings; do not re-derive style rules here.

   On the fan-out path each subagent invokes it for its own package, which keeps
   the rulebook out of this context. Reviewing in-context, invoke `go:style`
   with the Skill tool all the same and let its pass read the rule files; never
   read them here as well. The rules its pass reads land in this context: take
   the offenses and do not consult the rules again while judging correctness —
   the two dimensions stay separate in the report even when they share a
   context.

   One defect can be both. A `%v` wrap is a style offense and, where it breaks
   an error chain a caller unwraps, a correctness bug. Report it once, under
   correctness, with the higher of its two grades, and name the style rule it
   also breaks — a reader counting blockers should not meet the same line
   twice.
3. Review each file for what style does not cover, in this order:
   - Correctness: bugs, wrong logic, nil/bounds, ignored errors, data races.
   - Edge cases: empty/large/concurrent inputs and every error path; never
     call one unreachable without reading the callee's doc for every input it
     can receive, a replaceable package-level variable passed in included.
   - Error handling & API: wrapping, sentinels, boundaries, easy misuse.
   - Leaks: search for every acquisition (container, file, goroutine) with no
     release at all, not only for releases done wrong.
   - Never report a form the style rules require as a defect: the `"" +`
     segmented multi-line string is the mandated style (raw strings break
     indentation); never propose a backtick raw string for it.
   - Cross-boundary verify (`depth=standard`+): before reporting a claim that
     reaches beyond the diff — a symbol is unused, all callers handle an
     error/nil, an interface is fully implemented, a suspect branch is
     reachable — confirm it with the `LSP` tool (`findReferences`,
     `goToImplementation`, `incomingCalls`, `hover`/`goToDefinition`) rather
     than asserting from the visible code. Skip at `depth=light`; reserve for
     findings that cross a file/package boundary. No `LSP` tool in this client,
     no language server behind it, or one answering empty for a symbol the
     code visibly uses (an unindexed nested module) → fall back to grep/read
     and note the reduced confidence in the finding.
4. Reason only while reviewing: do not run gofmt, go vet, golangci-lint, or
   go test, `-cover` included — judge coverage by grepping the symbol in
   `*_test.go`, and the rest by reading the code. A shell width measure
   (`awk` line length) is allowed. Say so in the report: one line naming every
   command this pass ran — the `awk` measure and a `grep` count; "none" only
   when nothing ran — and that the style dimension came from `go:style`. A
   reader cannot otherwise tell a review that honored this from one that
   shelled out, and neither can anyone checking the run afterwards. `LSP` is
   allowed (read-only navigation). This governs the review, not the fix:
   applying findings requires the test gate in `references/fixing.md`, which
   proves each bug red then green and runs `go test ./... -race` per chunk.
5. Merge the style offenses with the correctness findings and report (below).
   Do not change code unless asked.

### Scale

- Single package or small module (<= ~6 packages, or more under ~500 lines of
  Go in all): review in this context, package by package, highest-risk first.
- Larger module (> ~6 packages and over ~500 lines, or comparable LOC in
  fewer): fan out one review subagent per package, never several packages to
  one worker (each invokes `go:style` on its package for the style offenses
  and reviews correctness itself, with the `depth`), then synthesize one
  merged report, re-ranking findings to the global `max` cap. Before
  dispatch, derive the `go:style` rule-id and tier list once (per
  `../style/references/checking.md`) and put it in every worker brief; the
  worker's `go:style` run uses that list, never ids or tiers of its own, which
  the merge cannot fold. Workers get no share of the cap — they report
  everything they find, and the cap is applied once at the merge, or a package
  full of nits evicts another package's blocker while the global budget still
  has room. At the merge, regrade every correctness Blocker a worker reports
  against Output's rubric: workers inflate it with a missing test for correct
  code, cosmetic output, and unreached misuse. Check every worker's
  `file:line` against the file before it enters the report.
- If the target is too large, do the highest-risk packages first and name the
  skipped ones in the report; never silently truncate.

### Output

Group by severity: Blocker / Should-fix / Nit. Style offenses keep the tier
`go:style` gave them. Grade a correctness finding by the worst consequence a
reachable input or state produces, naming that input in the finding — one you
cannot tie to an input is at most Should-fix. First match wins:

1. Blocker — a reachable input gives a wrong result, a panic, lost or
   corrupted data, a leak, a data race, a security exposure, or a swallowed
   error a caller depends on; or a test passes while the code is wrong.
2. Should-fix — correct for every current caller but fragile: an edge case no
   caller reaches yet, an error too vague to diagnose, an API easy to misuse, a
   reachable branch with no test, a performance cliff on realistic input.
3. Nit — no behavioural consequence: clarity, dead code, a micro-optimization.

Each finding:
- `file:line` — the problem in one line.
- The rule id or dimension (e.g. `wrap-errors-w`, `correctness`) — a style
  offense keeps the bare id `go:style` derived it under, unprefixed, so a
  finding merged from there is still the same string; one finding that is
  both names both (`correctness`, `wrap-errors-w`), never a paraphrase.
- A minimal suggested fix, checked to do what it claims: read how a helper
  reports failure (`t.Error` is not fatal) before prescribing a fatal or panic
  assertion, and its defaults (environment, working directory, streams)
  before prescribing it as isolation — a test helper can inherit the same
  process state; a tool that does not perform the edit (`go mod tidy` never
  merges single-line `require` statements) gets a manual fix instead. A fix
  making an operation idempotent covers every write it performs, not only the
  one that failed loudly. Never prescribe lazy initialization inside a
  value-receiver method — the field lands on a copy and is lost; prescribe a
  pointer receiver or a constructor the godoc requires. A fix replacing a
  format verb matches named types of a kind (`json.RawMessage`) by reflect
  kind, never by a type-switch case on the base type (`[]byte`, `string`).

End with a one-line verdict (ship / fix-first) and the per-severity counts. For
a module, give the verdict per package plus an overall summary. Report budget
usage: `depth`, packages/files reviewed — counted off the step-1 listing at
report time less any skipped, never estimated — and how many findings went
unreported past `max`.

### Applying fixes

When asked to change code (apply findings, fix, refactor), read
[references/fixing.md](references/fixing.md) first and follow it.

### Session rules

Close every completed Check run with Learn mode's scan, so the session's
corrections become rules without a separate `learn` call: below the finished
report (its verdict and budget line stay put), and after the fixes when `fix`
applies them, if this session holds the user's feedback on Go code, read
[references/rule-editing.md](references/rule-editing.md) and run its Learn steps
1–4 under the heading `Rules this session taught`, then write only what the user
picks; a code-style correction, one given during this run included, is a rule
candidate, never a `LESSONS.md` line as well; a correction of how the review ran
stays a lesson. No feedback, or none surviving step 2, adds nothing to the
report. A `plan_first` stop is not a completed run, and a fan-out worker never
runs it; the session is not its own.

### Delegated by go:audit

Delegation is recognized from the invocation, never guessed: `go:audit` says
it is invoking for findings only and passes the target, `depth`, and, when it
splits the review across workers, the pinned `go:style` rule-id list to use.
Run Check on that target and return the findings in Output's shape, uncapped —
the audit applies `max` once, at its merge — plus every command run,
then stop: no `plan_first` stop (the audit agreed the budget), no `fix`, no
Session rules, and no fan-out (the audit already split the work, and a worker
cannot dispatch one).

## Rule-edit and Learn modes

When either mode triggers, read
[references/rule-editing.md](references/rule-editing.md) first and follow it;
never write a rule without confirmation.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/go/review.md` (pass `~` as is, the
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
