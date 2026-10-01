# style pass

Read when `style` is invoked as a command (`/style ...`). The pass checks code
against the style rules only — formatting, naming, structure, godoc, test shape;
bugs, edge cases, and logic errors are `go:review`'s job.

Read the invocation from `$ARGUMENTS`; its first token is the target.

## Contents

- Target
- Budget & scope
- Principles
- Workflow
- Offense list
- Fixing
- Scale
- Delegated by go:review

## Target

The first token selects what to check:
- empty — run `git diff HEAD`; if that is empty, fall back to the diff vs the
  base branch (staged + unstaged).
- not a path at all — `add`, `change`, `remove`, or prose about the rules
  themselves is a rulebook edit, not a target: redirect to `go:review`
  (see SKILL.md) rather than resolving it as a directory that does not exist.
  Anything else unrecognized: say so and ask, do not guess a target.
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
- `plan_first` — propose the budget and the package list, then stop for the
  user's answer, checking nothing until it comes. Not "list the offenses and
  stop before applying": the default pick step already asks before applying, so
  that reading would make the flag do nothing.
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
6. When a line overflows the limit, name the overflowing piece as a local — a
   `format` string, a split literal, a `want` value — rather than wrapping the
   call.

## Workflow

1. Resolve the target, the budget, and the line settings — `max_line_length`
   and `tab_width` from the module root's `.editorconfig`, else 80 and 4,
   resolved once for the whole run; open the `rules.md` entry only when that
   file does not settle them. List the packages/files in scope.
2. Check each file against the rules in `SKILL.md` — Production for `*.go`,
   Test for `*_test.go` — reasoning from the Principles above. Open a keyed
   `rules.md` entry only when about to flag its rule; never preload the file.
   Read the entry, not the file: `grep -n` its Contents key to find the line,
   then read that range. `cat rules.md` is the thing this rule exists to
   prevent — it is the single largest file the pass can pull in, most of it
   about rules the target does not break.
3. Before reporting an offense whose truth reaches beyond the file (a rename's
   call sites, no-godoc-on-an-interface-method, an unused symbol), confirm it
   with the `LSP` tool (`findReferences`, `goToImplementation`, `hover`) rather
   than asserting from the visible code. Skip at `depth=light`. No language
   server → fall back to grep and note reduced confidence.
4. Reason only for detection: do not run gofmt, goimports, vet, or linters —
   judge by reading. `LSP` is allowed (read-only navigation).
5. List the offenses (below), then fix per Fixing.

## Offense list

Open with one line naming the resolved target, the files in scope, and the
resolved line settings (`limit N, tab W (from <path>|default)`), then the
offenses. That line is the report's first fact, not preamble — it is what makes
the list checkable, since a reader cannot tell an empty result from an
unresolved target without it, nor an over-width call from one the settings
allow.

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
- the rule id (e.g. `wrap-errors-w`, `no-name-stutter`).
- the minimal fix.

Rule ids are not coined per run, and "the exact rule phrase" is not an id —
asked for one, twelve workers turned the same `%w` rule into
`Wrap errors with %w and add context…`, `style: %w`, and a lower-cased variant.
An id is a bare slug: no `style:` prefix, no backticks, no capitals.

Derive it in these steps, which every worker must apply identically or the
merge cannot fold:

1. Take the rule's `SKILL.md` line. A `rules.md` entry does not change this —
   deriving from the entry's Contents key and from the line gives two ids for
   one rule, so the line is always the source and the entry is only where the
   detail lives.
2. Split on `;` first: a line carrying two rules separated by a semicolon is
   two rules with two ids, reported as two offenses. Never split on "and",
   which joins clauses of one rule as often as it joins two.
3. Drop everything that is not a word: punctuation, backticks, and the code
   inside them, except where the code *is* the word. Two forms qualify: a token
   that is only letters after its punctuation (`%w` → `w`), and a dotted
   identifier, which contributes the part before the first dot and nothing else
   (`context.Context` → `context`, `errors.Is` → `errors`). Taking the part
   after the dot instead turns one rule into `match-errors-is` for a worker who
   read `errors.Is` first and `match-errors-as` for one who read `errors.As`.
4. Drop these words wherever they fall: *a an the is are be to of in on at by
   with for from and or its it this that*. Nothing else is dropped —
   "significant" was doing that job and eleven workers read it one way while
   the twelfth read it another. Negations stay: `no-work-init` and
   `work-init` would name opposite rules, so dropping *no* is how two rules
   collide on one id.
5. Collapse a word that repeats the word just before it (`errors errors` →
   `errors`), then take the first three words that remain, lowercase, join with
   hyphens.

*Wrap errors with `%w` and add context…* → `wrap-errors-w`. *Lines fit the
limit…* → `lines-fit-limit`. *Receivers are a ~three-letter type abbreviation* →
`receivers-three-letter-type`. *`context` is the first parameter…* →
`context-first-parameter`. *No work in `init()`; no package-level mutable
state…* → `no-work-init` and `no-package-level-mutable`.

Under `fanout`, the parent derives the id for every rule it is dispatching
against and sends that list with each worker's brief. Workers use the list and
coin nothing; a rule they hit that is not on it comes back with the line quoted
and no id, for the parent to key. This is what "fix the id, do not reconcile at
the end" needs in order to be performable: twelve workers deriving
independently produced one spelling for three rules and two for the fourth,
which is a merge that has already failed.

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
  only the picked ones. `fix` applies all. A plan-first run — the flag, or the
  automatic one a broad target triggers — reaches here only after the user has
  answered the plan, and that answer agreed the budget, not the fixes: the pick
  step still runs. Before the answer there is no offense list to apply at all,
  because nothing has been checked yet.
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
  `SKILL.md`, this reference, the `depth`, and the parent's rule-id list, and
  opens `rules.md` entries per need like the parent), then merge into one
  report re-ranked to the global `max_issues`. The id list is every rule the
  depth puts in scope, which at `standard` and `full` is the whole rulebook —
  well over a hundred ids. That size is expected and is not a reason to trim
  it: the parent cannot know which rules a package breaks until the package is
  checked, and a worker that meets a rule missing from its list has to come
  back with a quoted line and no id. Report which packages were checked and
  which were skipped; never silently truncate.

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
  `max_issues`. Sum the raw total from the worker reports when you write it
  down — a fan-out's "N offenses across M packages, K unreported" is the one
  number the reader cannot re-derive without the worker output, and a merge
  that reported 48 where the workers summed to 45 got it by carrying a figure
  rather than adding one. If a rule id arrives in two spellings, the merge has already
  failed — fix the id, do not reconcile at the end.

## Delegated by go:review

Delegation is recognized from the invocation, not guessed: `review` says it is
invoking for offenses only and passes the target and budget. There is no flag —
a run that was not told it is delegated is not delegated, and asks the user
which offenses to apply as usual.

When `go:review` invokes `style` to report offenses only, run steps 1–4 for
the target/budget it passes and output the offense list, then stop — do not run
Fixing. `review` merges these offenses with its correctness findings and owns
fix application.
