# review

The done-time Go quality gate. Run it after the edits and the feature are
finished. It reviews the changed Go code against:

- the `style` rules (the canonical terse list),
- the deeper criteria in `rules.md` (why / example / how to detect),
- general correctness: bugs, edge cases, and error handling.

It reasons about the code only — it does not run gofmt, vet, linters, or tests.
It reports findings; it does not change code unless you ask.

It also owns the rule list: describe a preference in plain words and it becomes
a durable rule in `style`. Or run `/review learn` to turn the feedback you gave
across a whole editing session into rules.

## Usage

```
/review                                    # review the current git diff
/review ./pkg/foo                          # review one package
/review ./...                              # review the whole module
/review /path/to/project                   # review that module (go.mod dir)
/review add "no naked returns in tests"    # add or refine a rule
/review remove "the compile-time check rule"
/review learn                              # mine this session's feedback into rules
```

Targets: no argument reviews the current diff; a package path/import reviews
that package; `./...` or a module root reviews every package. Small targets are
reviewed in context; a large module (> ~6 packages) fans out one review
subagent per package and merges the results.

### Budget controls

Example invocations:

```
/review ./... max_issues=15 depth=light
/review ./pkg/foo depth=exhaustive
/review ./... plan_first          # plan + top findings, then stop
/review ./... packages=parser,lexer
```

- `max_issues=N` — cap on findings (default 25).
- `depth=light|standard|exhaustive` — default standard.
- `plan_first` — short prioritized plan first, then stop for approval.
- `packages=a,b` — restrict to these packages.

A broad target with no budget auto-switches to plan-first and proposes
defaults before doing the full pass.

## Relationship to style

- `style` = the terse rules, read while **writing** Go (loaded per edit).
- `review` = reads those same rules and checks **finished** code against
  them, plus a deeper correctness review. One ruleset, two moments.

## Evaluations

### 1. Review the current diff (default, reason-only)

**Request:** `/review` with a staged diff that ignores an error and wraps
another with `fmt.Errorf` using `%v`.

**Expected behavior:**
- Resolves the target to the current diff and lists the files in scope.
- Reasons only — runs no gofmt, vet, linter, or `go test`.
- Reports findings grouped Blocker / Should-fix / Nit, each with `file:line`,
  the rule id or dimension (`style: %w`, `correctness`), and a minimal fix;
  ends with a ship/fix-first verdict and per-severity counts.

### 2. Broad target auto-switches to plan-first

**Request:** `/review ./...` on a module of many packages, no budget given.

**Expected behavior:**
- Detects the broad target, switches to `plan_first`, proposes defaults
  (`max_issues=25`, `depth=standard`, the package list), and stops for approval
  before the full pass.
- For > ~6 packages, fans out one subagent per package and merges into one
  ranked report capped at `max_issues`.

### 3. Rule-edit mode

**Request:** `/review add "no naked returns in tests"`.

**Expected behavior:**
- Recognizes a rule edit, turns it into a terse imperative one-liner in the
  existing style, scoped to Test.
- Detects any duplicate/conflicting rule and waits for confirmation before
  writing to `style`; shows the before/after diff.

### 4. Learn from the session

**Request:** `/review learn` after a session where the user renamed a helper for
clarity and asked to convert an `f(p *T)` function into a method.

**Expected behavior:**
- Scans the session's Go feedback and pairs each with the diff hunk that
  resolved it; proposes only generalizable rules (method-over-func,
  behavior-named helper), each with its provenance and a before/after example.
- Drops task-specific one-offs; dedupes against existing `style` rules.
- Waits for the user to pick before writing; on confirmation writes the `style`
  line (+ keyed `rules.md` entry) and shows the diff.

### 5. Terse output

**Request:** `/review ./pkg/foo`.

**Expected behavior:**
- No preamble or step narration ("Let me read the rules…"); opens with the
  findings.
- States each finding once and reports budget usage; no closing summary that
  re-lists findings the user can already see.
