---
name: style
description: >
  Enforced Go coding style for this project (production and test code): the
  rulebook to read before writing or editing any .go file, and a runnable
  style-only pass that lists style offenses across a diff, package, or module
  and proposes fixes to apply. Use before touching Go, or to check or fix Go
  style; adding or changing a rule belongs to go:review.
license: MIT
argument-hint: "[TARGET] [packages=a,b] [max_issues=N]
  [depth=light|standard*|full] [plan_first] [fix]"
---

# style

## Usage

```
/style                                  style-check the current git diff (default)
/style ./pkg/foo                        style-check one package
/style ./...                            check the whole module
/style /path/to/project                 check that module (a go.mod dir)
/style ./pkg/foo fix                    apply every offense's fix without asking
/style ./... plan_first                 propose the budget, then stop
/style ./... packages=a,b               restrict a module check to these packages
/style ./... max_issues=15 depth=light  cap offenses; set depth
```

Authoritative Go style rules and the style-only pass that enforces them. Two
uses:

- Reference — when loaded as context before writing Go (the default): apply
  the Production section to `*.go` and the Test section to `*_test.go`; Test
  inherits Production unless a Test rule overrides it.
- Run a pass — when invoked as `/style [target]`: check finished code against
  these rules and propose fixes. Read
  [references/checking.md](references/checking.md) and follow it; per-rule
  detection detail lives in [rules.md](rules.md), opened one entry at a time.

Change the rules only through `go:review` (state a preference, or
`go:review learn` to mine an editing session); never hand-edit them.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see — when citing a rule, name it and the fix, not
its full text.

## Production

### Formatting

- gofmt + goimports always; never hand-format or reorder imports manually.
- Lines fit the limit, counting the `//` prefix and a tab as the tab width —
  both from the module's `.editorconfig`, else 80 and 4; break only when over,
  one logical arg per line with `(` on the call line.
- When a function signature spans multiple lines, put each parameter on its
  own line and open the body with a blank line.
- Collapse a multi-line signature to one line when it fits the limit (through
  the opening `{`, or the full type for func-typed params/fields); re-check
  after a change (a shorter param type, a wider resolved limit) that makes a
  wrapped signature now fit.
- Extract a long or complex format string into a `format` local before the
  call (`fmt.Errorf`, `Sprintf`, `Printf`); prefer it to breaking the call
  across lines to fit the limit.
- Split a string literal too long for one line into per-line `"..."` segments
  joined with `+`, led by an empty `"" +` on the opening line so every segment
  aligns; keep `\n` explicit and never use a raw backtick string for multi-line
  content.
- Separate multi-line switch cases with a blank line; none before the first.

### Naming

- No name stutter: `pkg.Thing`, not `pkg.PkgThing`; exempt a name fixed by an
  external contract when the file pins it with a compile-time assertion
  (`var _ Contract = (*T)(nil)`) and a godoc saying why.
- Receivers are a ~three-letter type abbreviation, not a single letter:
  `pag *page`, `cfg *config`.
- Typed locals reuse their type's receiver name (`pag` for `*page`, `cfg` for
  `*config`) — the name the receiver rule gives it, never a single-letter
  receiver that rule is fixing.
- Name a helper for what it does, not its one caller: a domain-agnostic body
  gets a domain-agnostic name and error text (`fileExists`, not `cached`).

### Functions & methods

- A func whose sole parameter is a local `*T`/`T` belongs on T as a method
  (`pag.f()`, not `f(pag)`); drop the type from its name (`encode`, not
  `encodePage`). Stay a func only when a signature contract (sort, http,
  callback) or deliberate typelessness (`helpers.go`) requires.
- Don't wrap a single expression in a one-line function used at a single call
  site; inline it (Test has the same rule for helpers).
- Export only symbols used or intended outside the package; keep
  package-internal helpers unexported.
- A method returns only its named result; leave presentation (trailing
  newline, padding) to the caller.
- No naked returns in non-trivial functions.
- Order a function body so cheap, fallible checks (config reads, validation)
  run before expensive or side-effecting work; fail fast before the heavy work.

### Declarations & files

- Group related consts into one `const (...)` block with a headline comment
  naming the group; give a member its own comment only when its name and type
  don't already say what it is. Reserve standalone `const` for a value with no
  relatives.
- Put the package godoc comment in the file named after the package (`foo.go`
  in package `foo`) when one exists; don't keep a separate `doc.go` for it.
- Keep package-wide top-level declarations (exported consts/vars) in the
  package-named file, not a separate topic-named file; same principle as the
  package-godoc rule above.
- Domain-agnostic, typeless helpers (`fileExists`, `isDigits`) live in
  `helpers.go`, their tests in `helpers_test.go` — mirrors `all_test.go`.
- Declare an empty slice as `var s []T` (nil) or `make([]T, 0)` (non-nil),
  never `s := []T{}`.

### Godoc & comments

- Comments are full sentences: capital start, terminal period.
- Godoc prose is grammatically correct English: articles, subject-verb
  agreement, restrictive "that" vs "which".
- Comments explain the code; never trace it to a spec — no requirement/ticket
  ids in code comments (`// CLI-4`, `// JIRA-123`).
- Every exported symbol and the package have godoc; a const-group headline
  covers members whose name and type say it all.
- Godoc states only what the signature can't; never restate the obvious.
- In godoc prose name the type, not the receiver variable.
- On interface-implementing methods, never restate the interface's contract;
  document only behavior beyond it, or nothing.
- Use godoc cross-references for exported symbols only: `[Type]`,
  `[pkg.Symbol]`; name unexported identifiers in plain text.
- nolint: no space `//nolint:name`; line-level at end of line; func-scoped as
  the last godoc line after an empty `//`; comma-join multiple (`a,b`).

### Errors

- Wrap errors with `%w` and add context; never swallow the error.
- Handle each error exactly once.
- Reuse an already-declared `err` with `=`; only the first check in a scope
  uses `:=`.
- Discard an intentionally-ignored return explicitly with `_` (`_, _ =
  fmt.Fprintf(w, ...)`); never leave it bare, so the discard reads as
  deliberate. `_` on an error a caller needs is still a swallow.
- Export sentinel errors as `ErrXxx`; unexported as `errXxx`.
- Keep wrap context short and meaningful; no `failed to ...` prefixes.
- Match errors with `errors.Is`/`errors.As`, never `==`.

### Output & environment

- Never write output (errors included) to stdout/stderr from library, leaf, or
  mid-level functions; return an error (`%w`) or output as a value.
- A function that needs an environment variable takes `*ring.Ring` and reads it
  via `rng.EnvGet`/`EnvLookup`; never `os.Getenv`.

### API design

- `context.Context` is the first parameter when used; never store it in a
  struct.
- Respect `ctx.Err()`; stop work and propagate cancellation.
- Accept interfaces, return concrete types; keep interfaces small.
- Assert implementations at compile time: `var _ Iface = (*T)(nil)` near the
  top of the file.
- Make the zero value useful or at least safe.
- No work in `init()`; no package-level mutable state or singletons.

### Docs & examples

- Provide `Example*` for non-trivial public APIs; they must pass `go test`;
  skip `main`, `internal`, and test-only packages.
- A reusable package ships a `README.md` (or a package-godoc overview):
  purpose, import path, and one runnable usage example; skip `main`,
  `internal`, and test-only packages.

## Test

### Structure

- Structure every test body with the three comment markers, in order:
  `--- Given ---` arranges, `--- When ---` performs the single action under
  test, `--- Then ---` asserts. They are literal comment lines
  (`// --- Given ---`), not prose, and the rules below constrain them.
- Table-driven subtests via `t.Run`; one case per table row.
- When a table row exceeds the line limit, break it one element per line,
  positional in field order — never add field-name keys.
- Keep the table-test loop body branch-free — every row runs the same
  assertions; move any case needing different assertions to its own test.
- Build a non-trivial `--- When ---` argument (composite literal, multi-step
  value) in `--- Given ---`; keep literals, variables, dereferences, field
  reads and simple calls inline unless the call would exceed the line limit;
  never move the call under test out of `--- When ---`.
- Use `t.Context()`, never `context.Background()`; pass it inline in the
  `--- When ---` call, and hoist `ctx := t.Context()` only when used more than
  once or inlining exceeds the line limit, then as the first `--- Given ---`
  line.
- Omit the `--- Given ---` marker when the subtest has no arrange step;
  never leave an empty `--- Given ---` section.
- Declare those `--- Given ---` argument variables in the same left-to-right
  order the `--- When ---` call uses them; keep a variable's setup next to its
  declaration.
- Separate distinct topics within a `--- Given ---`/`--- Then ---` block with a
  blank line; group statements by the subject they set up or verify; no blank
  line between consecutive same-subject assertions. A subject includes every
  statement that configures it (files written into a fixture dir and their
  content values, a chdir into it, env set on a ring); consecutive standalone
  declarations of distinct subjects run together, multi-line literals and one
  built from the previous (`items := []T{tgt}`) included. The subject is the
  value being set up or asserted about, not the call that produced it:
  everything returned by one `--- When ---` call is one subject, so an
  `assert.NoError` and the `assert.Equal` checking that call's result take no
  blank line between them, nor do assertions on a receiver, argument or output
  the call mutated, nor a `--- Then ---` local or comment; in `--- Then ---`
  only a second action (a further call on the result, such as `Execute`) takes
  one. Check every such block with two or more subjects: label each statement
  with its subject first, then flag each missing blank line around a
  multi-statement subject and each blank line inside a subject.
- In `foo_test.go` with a matching `foo.go`, test functions follow the
  declaration order of their subject in `foo.go`; `Test_Foo` precedes
  `Test_Foo_tabular`; files without a 1-to-1 name match are exempt.

### Naming

- Test function names are `Test_Func` and `Test_Type_Method`; add `_tabular`
  for table tests.
- Subtest names use only `[a-zA-Z0-9 _-]`; keep them flat, no `/`.
- Keep subtest names terse — name the condition or trigger, not a full
  sentence.
- Error-path subtest names start with `error - ` then the failure condition;
  don't restate "returns error".
- Name the actual value `have` and the expected value `want`, never `got`;
  reassign `want` for sequential expectations; only when two expected values
  are live in the same assertion region, suffix as `wXxx` (same for
  `have`/`hXxx`).
- `have` is the value under test (the `--- When ---` result); it overrides
  receiver-mirroring. Given subjects and secondary Then values keep descriptive
  names.

### Assertions

- Keep assertion style consistent with the project's chosen library.
- Assert on output text unique to the expected result, never a token shared
  with other outputs (the program name, a common prefix); the assertion must
  fail if the wrong branch printed. Prefer whole-string `Equal` when the output
  is small and fixed; reach for `Contain` only on a distinctive substring.
- Assert an error's distinctive cause, not a wrapper prefix shared by sibling
  paths; a dispatch test must observe an outcome only that branch yields.
- Match several substrings of one error with one `ErrorRegexp("a.*b")`, not
  stacked `ErrorContain` calls.
- Hoist a literal or a readback (file read, path join) into a local only to
  keep the line within the limit; when the inlined form fits, inline it at each
  use even if repeated.
- Hoist a multi-line structured-data literal (JSON, YAML) passed to a call into
  a pretty-printed backtick raw-string local; don't inline it or split it across
  `+`-joined segments to fit the line limit.

### Helpers & fixtures

- Test helpers call `t.Helper()`.
- The packages these rules name: `tester` and `assert` come from
  `github.com/ctx42/testing/pkg/{tester,assert}`; `ring` from
  `github.com/ctx42/ring/pkg/ring`; `oskit` from
  `github.com/ctx42/testkit/pkg/oskit` — a different module, so it needs its
  own `require` entry. Read the package's own imports first: a project pinning
  different paths wins over this list.
- Test helpers must use `tester.T` to allow testing with `tester.Spy`.
- Use `tester.Spy` (not raw `*testing.T`) when testing test helpers.
- Don't wrap a single expression in a test helper; inline it. If a helper only
  centralizes a repeated literal (e.g. a fixture path), extract a `const`.
- Simple test helpers shared within a package live in `all_test.go`; do not
  scatter them across individual `_test.go` files.
- In arrange/readback code where the error is not under test, unwrap
  value-plus-error with `must.Value`/`must.Values` instead of assigning then
  `assert.NoError`; keep the explicit check only where the error itself is the
  assertion (the `--- When ---` call).
- Use oskit filesystem helpers in arrange/readback (`oskit.Create`, `Write`,
  `MkdirAll`, `ReadFile`/`ReadFileStr`), not `os.*` wrapped in `assert.NoError`
  (nor `os.ReadFile` plus error handling and a `string(...)` conversion).
- Set an environment variable for code under test with `rng.EnvSet`, never
  `t.Setenv`.

### Coverage

- Every new func/method (exported or not) ships with tests in the same change.
- When a test guards a struct's field count, a new field must both bump the
  count and gain an assertion in the same change — never bump the count alone.
- Cover error paths and edge cases, not just the happy path.
- Don't chase coverage: skip tests of `//go:build ignore` tools and of a test
  helper's trivial error branches that need platform tricks (a fake binary on
  `PATH`, `chmod 0`, a removed working directory); never add a production
  override (env var, hook, parameter) only so a test can reach a branch.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/go/style.md`, the
sibling winning a conflict — a read-only install writes the second, and what it
learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule — general, naming nothing from
the project at hand (its files, tests, tickets) — to the sibling when this
directory is writable, else to the fallback, creating it, and report where.