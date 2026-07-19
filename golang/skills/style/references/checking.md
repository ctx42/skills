# style pass

Read when `style` is invoked with a target. This pass checks code against the
style rules **only** — formatting, naming, structure, godoc, test shape. It does
not hunt bugs, edge cases, or logic errors; that is `golang:review`.

Read the invocation from `$ARGUMENTS`; `$1` is the first token (the target).

## Target

`$1` selects what to check:
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

Default to plan-first for a broad target (whole module, many packages, large
LOC) with no budget: propose defaults (the caps above, the package list) and ask
before applying anything.

## Workflow

1. Resolve the target and budget; list the packages/files in scope.
2. Check each file against the rules in `SKILL.md` — Production for `*.go`, Test
   for `*_test.go`. Reason from `rules.md`'s **Principles**; open a keyed
   `rules.md` entry only when about to flag its rule, never preload the file.
3. Before reporting an offense whose truth reaches beyond the file (a rename's
   call sites, no-godoc-on-an-interface-method, an unused symbol), confirm it
   with the `LSP` tool (`findReferences`, `goToImplementation`, `hover`) rather
   than asserting from the visible code. Skip at `depth=light`. No language
   server → fall back to grep and note reduced confidence.
4. Reason only for detection: do not run gofmt, goimports, vet, or linters —
   judge by reading. `LSP` is allowed (read-only navigation).
5. List the offenses (below), then fix per **Fixing**.

## Offense list

Group by severity **Blocker / Should-fix / Nit**. Each offense:
- `file:line` — the offense in one line.
- the rule id (e.g. `style: %w`, `style: no-stutter`).
- the minimal fix.

Stop at `max_issues`, highest-severity first; say how many offenses went
unreported. End with a one-line verdict (clean / fix-first) and per-severity
counts.

## Fixing

Style fixes are non-behavioral (formatting, naming, comments, structure), so the
bug-reproduction protocol does not apply — the test gate is the proof.

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
  these rules, `rules.md`, the `depth`, and a share of `max_issues`), then merge
  into one report re-ranked to the global `max_issues`. Report which packages
  were checked and which were skipped; never silently truncate.

## Delegated by golang:review

When `golang:review` invokes `style` to report offenses only, run steps 1–4 for
the target/budget it passes and output the offense list, then **stop** — do not
run **Fixing**. `review` merges these offenses with its correctness findings and
owns fix application.
