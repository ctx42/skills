# style pass

Read when `style` is invoked as a command (`/style ...`). The pass checks code
against the style rules only — formatting, naming, structure, godoc, test shape;
bugs, edge cases, and logic errors are `golang:review`'s job.

Read the invocation from `$ARGUMENTS`; its first token is the target.

## Contents

- Target
- Budget & scope
- Principles
- Workflow
- Offense list
- Fixing
- Scale
- Delegated by golang:review

## Target

The first token selects what to check:
- empty — run `git diff HEAD`; if that is empty, fall back to the diff vs the
  base branch (staged + unstaged).
- a package — a path like `./pkg/foo` or an import path; check that package's
  `.go` files.
- a module / many packages — `./...`, a directory containing `go.mod`, or an
  explicit "module"; check every package in the module.

State the resolved target and the exact file set before checking.

## Budget & scope

Read these from `$ARGUMENTS` (any order, after the target):
- `packages=a,b` — restrict to these packages within the target.
- `max_issues=N` — cap on offenses reported (default 25).
- `depth=light|standard|full` — default `standard`. `light` reports only
  high-impact offenses; `full` checks every rule exhaustively.
- `plan_first` — list the offenses and stop for approval before applying any.
- `fix` — apply every listed offense's fix without asking (skips the pick step).

Default to plan-first for a broad target with no budget: propose defaults (the
caps above, the package list) and ask before applying anything. Broad means the
run would fan out — more than ~6 packages, the same threshold Scale uses. A
module of three small packages is `./...` and still not broad: check it in this
context and use the normal pick step, which asks before applying anyway.

Plan-first is propose-then-stop: the defaults and the package list, and no
check until the user answers. It is not check-everything-then-present — that
spends the whole run before the budget it is asking about has been agreed.

## Principles

Reason from these while checking; they generalize the `SKILL.md` rules to cases
no single line spells out.

1. Earn every token: flag text the signature, the reader, or the rule already
   carries — godoc paraphrasing the name or params, a doc comment duplicating
   an interface, a helper wrapping one expression, a `want` that saves no
   width, an `x, err :=` + `assert.NoError` dance where the error isn't under
   test.
2. Name a thing for what it is or does, not where it sits: no qualifier
   stutter, a method over a func taking one receiver-typed arg, a helper named
   for its behavior not its caller, `ErrXxx` sentinels, typed receivers and
   matching locals.
3. Separate distinct multi-line groups with a blank line — switch cases, test
   topic groups, const groups; group by subject, not by statement type.
4. Handle output and errors at the right layer: a leaf returns the computed
   value and its errors; the entry point owns the streams, the exit code, and
   presentation (trailing newline, padding).
5. An assertion must be able to fail: pin the output or error cause unique to
   the wanted branch, never a token shared across sibling paths.
6. When a line overflows 80 cols, name the overflowing piece as a local — a
   `format` string, a split literal, a `want` value — rather than wrapping the
   call.

## Workflow

1. Resolve the target and budget; list the packages/files in scope.
2. Check each file against the rules in `SKILL.md` — Production for `*.go`,
   Test for `*_test.go` — reasoning from the Principles above. Open a keyed
   `rules.md` entry only when about to flag its rule; never preload the file.
3. Before reporting an offense whose truth reaches beyond the file (a rename's
   call sites, no-godoc-on-an-interface-method, an unused symbol), confirm it
   with the `LSP` tool (`findReferences`, `goToImplementation`, `hover`) rather
   than asserting from the visible code. Skip at `depth=light`. No language
   server → fall back to grep and note reduced confidence.
4. Reason only for detection: do not run gofmt, goimports, vet, or linters —
   judge by reading. `LSP` is allowed (read-only navigation).
5. List the offenses (below), then fix per Fixing.

## Offense list

Open with one line naming the resolved target and the files in scope, then the
offenses. That line is the report's first fact, not preamble — it is what makes
the list checkable, since a reader cannot tell an empty result from an
unresolved target without it.

Group by severity Blocker / Should-fix / Nit. Severity is a property of the
rule, not of the instance or the reader's taste: the same rule broken in two
packages is the same severity in both, and a worker that finds switch spacing a
Nit in four packages and Should-fix in two has graded the code rather than the
rule. Decide it once, the same way every time:

- Blocker — the code is wrong or will mislead: a swallowed or `%v`-wrapped
  error, a data race the style rules forbid, an exported symbol with no godoc,
  a name that states the opposite of what the code does.
- Should-fix — the rule is broken and a reader pays for it, but nothing is
  incorrect: naming, stutter, receiver conventions, test structure, ordering.
- Nit — mechanical and local: spacing, comment wording, import grouping.

A rule that fits none cleanly takes the nearest tier and says so in the
offense, rather than being graded afresh each time it appears.

Each offense:
- `file:line` — the offense in one line.
- the rule id (e.g. `style: %w`, `style: no-stutter`).
- the minimal fix.

Rule ids are not coined per run, and "the exact rule phrase" is not an id —
asked for one, twelve workers turned the same `%w` rule into
`Wrap errors with %w and add context…`, `style: %w`, and a lower-cased variant.
Derive it mechanically so every worker lands on the same string:

- The rule has a `rules.md` entry → its Contents key, slugged: *No name stutter*
  → `no-name-stutter`.
- It does not → the first three significant words of its `SKILL.md` line,
  lowercased, hyphenated, punctuation and articles dropped: *Wrap errors with
  `%w`…* → `wrap-errors-w`; *Lines <=80 cols…* → `lines-80-cols`.

Two shapes break that recipe and need a stated answer, or the same rule gets
two ids and the merge fails:

- The line opens with code, so the first words are an identifier. Read the
  identifier as one word and take two more prose words after it: *`context` is
  the first parameter…* → `context-first-parameter`, not `contextcontext`.
- The line carries two rules joined by a semicolon or `and`. Each half is its
  own id, derived from its own first three words: *No work in `init()`; no
  package-level mutable state…* → `no-work-init` and
  `no-package-level-mutable`. Report them as separate offenses; one id covering
  two rules cannot be folded or cut correctly.

One offense is one rule broken in one file, however many times it is broken
there — list every site on the offense, do not repeat the offense per site.
Twelve workers reporting a receiver rule as one offense in some packages and
one per site in others makes every count noise, and a cap applied to sites
rather than rules spends itself on whichever rule happens to repeat most.

Stop at `max_issues`, highest-severity first; say how many offenses went
unreported. End with a one-line verdict (clean / fix-first) and per-severity
counts.

## Fixing

Style fixes are non-behavioral (formatting, naming, comments, structure), so no
failing-test reproduction is needed — the test gate is the proof.

- Default: present the offenses as a numbered list and ask which to apply; apply
  only the picked ones. `fix` applies all; `plan_first` stops after the list.
- For a rename or signature change, enumerate call sites with `LSP`
  (`findReferences`, `goToImplementation`) before editing so definition and
  dependents change together.
- Run `go test ./... -race` for a green baseline before editing; if already red,
  stop and report. Run it again after — the job is not done until it passes.
- Never print diffs of applied fixes: report each as one line (`file:sym — what
  changed`) plus the gate result. Never `git commit`.
- Big job (offenses span many packages / large LOC): write an ordered plan to a
  gitignored scratch file (`tmp/style-fix-plan.md`), one chunk per package with
  status boxes; get a go-ahead, work chunks in order, gate per chunk, consult
  after each changed chunk.

## Scale

- Single package or small module (<= ~6 packages): check in this context.
- Larger module (> ~6 packages): fan out one subagent per package (each gets
  `SKILL.md`, this reference, and the `depth`, and opens `rules.md` entries per
  need like the parent), then merge into one report re-ranked to the global
  `max_issues`. Report which packages were checked and which were skipped;
  never silently truncate.

  Workers do not get a share of `max_issues` — they report every offense they
  find, and the cap is applied once, at the merge, across the whole set. A
  per-worker budget drops findings before anything can rank them, so a package
  with many nits evicts another package's blocker while the global cap still
  has room.

  The merge folds by rule id before it cuts: one rule broken in twelve packages
  is one finding listing twelve packages, not twelve findings. Cut at
  `max_issues` after folding. Unfolded, two blockers repeated across a module
  consumed a whole default cap of 25 while the rule broken in *every* package
  fell outside it — the worst finding in the run, unreported.

  Every worker checks the same rules: the Production section, plus Test for
  `_test.go`. Each reports which rules it checked, and the merge says so. Left
  to choose, twelve workers on byte-identical code detected zero-value safety
  in ten, cross-references in four, and returned per-package totals from 3 to
  10 for the same file — a spread that looks like a finding about the packages
  and is really a finding about the workers.

  The merge is only performable if workers agree on ids and severity, which is
  what the rubric and the id rule above are for: merging means concatenating,
  sorting by severity then rule id, collapsing exact duplicates, and cutting at
  `max_issues`. If a rule id arrives in two spellings, the merge has already
  failed — fix the id, do not reconcile at the end.

## Delegated by golang:review

Delegation is recognized from the invocation, not guessed: `review` says it is
invoking for offenses only and passes the target and budget. There is no flag —
a run that was not told it is delegated is not delegated, and asks the user
which offenses to apply as usual.

When `golang:review` invokes `style` to report offenses only, run steps 1–4 for
the target/budget it passes and output the offense list, then stop — do not run
Fixing. `review` merges these offenses with its correctness findings and owns
fix application.
