# style

A living, token-optimized Go style guide that both you and AI agents follow
when writing Go. Production code and test code have separate rule sets.

The rule list is maintained **only** through `golang:review` — describe what
you want in plain words and it becomes a durable rule, or run `golang:review
learn` to turn a whole editing session's feedback into rules. Do not hand-edit
`SKILL.md` for routine changes.

## Make agents follow it automatically

This repo is only the source. For agents to apply the rules "when editing Go
files", paste this directive into the target **project's** `CLAUDE.md`:

```md
## Go style

Before creating or editing any `*.go` file, read the `style` skill and
follow it: the `Production` section for non-`_test.go` files, the `Test`
section for `_test.go` files.
```

## Manual use

Run `/style` any time to load the current rules into context.

## Evaluations

style is a reference ruleset other skills read, not a runtime workflow; its
evals assert that the right rules are applied to the right files and that a
manual load stays terse.

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

### 3. Rules change only through review

**Request:** A user asks to add a new style rule.

**Expected behavior:**
- The rule is added via `/review` (rule-edit mode), not by hand-editing
  `SKILL.md`.

### 4. Terse manual load

**Request:** `/style`.

**Expected behavior:**
- Loads the rules with no preamble or narration; does not restate or summarize
  the ruleset back to the user beyond surfacing it.
