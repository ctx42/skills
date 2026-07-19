# style

The project's Go style authority, in two roles:

- Rulebook — a living, token-optimized style guide that you and AI agents read
  while **writing** Go. Production and test code have separate rule sets.
- Style pass — invoked with a target, it checks **finished** Go against those
  rules, lists offenses, and proposes fixes to apply. It is style-only: no bug,
  edge-case, or logic review (that is `golang:review`).

The rule list is maintained **only** through `golang:review` — describe what you
want in plain words and it becomes a durable rule, or run `golang:review learn`
to turn a whole editing session's feedback into rules. Do not hand-edit
`SKILL.md` for routine changes.

## Make agents follow it automatically

For agents to apply the rules "when editing Go files", paste this directive into
the target **project's** `CLAUDE.md`:

```md
## Go style

Before creating or editing any `*.go` file, read the `style` skill and
follow it: the `Production` section for non-`_test.go` files, the `Test`
section for `_test.go` files.
```

## Run a style pass

```
/style                        # style-check the current git diff
/style ./pkg/foo              # one package
/style ./...                  # the whole module
/style ./pkg/foo fix          # apply every offense's fix without asking
```

Targets match `golang:review`: no argument checks the current diff; a package
path/import checks that package; `./...` or a module root checks every package.
A large module (> ~6 packages) fans out one subagent per package and merges.

Budget controls (same as review): `packages=a,b`, `max_issues=N` (default 25),
`depth=light|standard|full` (default standard), `plan_first`. A broad target
with no budget auto-switches to plan-first.

By default the pass lists offenses and asks which to apply; `fix` applies all,
`plan_first` stops after the list. Applying runs the module test suite green and
never prints diffs or commits.

Loading `/style` with no target just surfaces the current rules into context.

## Relationship to review

- `style` = the rules (read while writing Go) **and** the style-only pass.
- `review` = the done-time quality gate: it delegates the style dimension to
  `style` and adds correctness, edge-case, and error-handling review on top. One
  ruleset, invoked from both.

## Evaluations

### 1. Production rules on a `*.go` file

**Request:** An agent is about to edit `service.go` after reading style.

**Expected behavior:**
- Applies the **Production** section: gofmt + goimports, ≤ 80-col lines, `%w`
  error wrapping with short context, godoc on exported symbols.
- Does not apply Test-only rules to the production file.

### 2. Test rules on a `*_test.go` file

**Request:** An agent writes `service_test.go`.

**Expected behavior:**
- Applies the **Test** section on top of Production: `Test_Func` /
  `Test_Type_Method` naming, `_tabular` for table tests, `t.Run` subtests,
  `t.Helper()` in helpers, `tester.Spy` when testing helpers.
- Honors the subtest-name charset `[a-zA-Z0-9 _-]`, flat, no `/`.

### 3. Style pass lists offenses and proposes fixes

**Request:** `/style ./pkg/foo` on a package with a single-letter receiver and a
godoc on an interface-implementing method.

**Expected behavior:**
- Resolves the target, lists the files in scope, and reads `references/
  checking.md`; reasons only for detection (no gofmt/vet/linter run).
- Reports style offenses only — no bug, edge-case, or logic findings — grouped
  Blocker / Should-fix / Nit, each with `file:line`, the rule id, and a minimal
  fix; ends with a clean/fix-first verdict and per-severity counts.
- Then asks which offenses to apply rather than editing unprompted; `fix` would
  apply all.

### 4. Rules change only through review

**Request:** A user asks to add a new style rule.

**Expected behavior:**
- The rule is added via `/review` (rule-edit mode), not by hand-editing
  `SKILL.md`.

### 5. Terse output

**Request:** `/style ./pkg/foo`.

**Expected behavior:**
- No preamble or step narration ("Let me read the rules…"); opens with the
  offenses.
- States each offense once; no closing summary that re-lists offenses the user
  can already see.
