---
name: style
description: >
  Enforced Go coding style for this project. Read before writing or editing
  any .go file. Production code (non-_test.go) and test code (_test.go) follow
  different rules. Maintained only via /review, never ad hoc.
license: MIT
---

# style

Authoritative Go style rules. Apply the **Production** section to `*.go` and
the **Test** section to `*_test.go`. Test code inherits Production unless a
Test rule overrides it. Do not hand-edit this file ad hoc — change rules with
`/review`.

Report tersely: when citing a rule, name it and the fix; don't restate the
rule's full text or narrate.

## Production

- gofmt + goimports always; never hand-format or reorder imports manually.
- Lines <=80 cols including the `//` prefix; break only when over, one
  logical arg per line with `(` on the call line.
- When a function signature spans multiple lines, put each parameter on its
  own line and open the body with a blank line.
- Collapse a multi-line signature to one line when it fits <=80 (through the
  opening `{`, or the full type for func-typed params/fields).
- Extract a long or complex format string into a `format` local before the
  call (`fmt.Errorf`, `Sprintf`, `Printf`); prefer it to breaking the call
  across lines to fit <=80.
- Split a string literal too long for one line into per-line `"..."` segments
  joined with `+`, led by an empty `"" +` on the opening line so every segment
  aligns; keep `\n` explicit, never a raw backtick string for multi-line content.
- Comments are full sentences: capital start, terminal period.
- Comments explain the code; never trace it to a spec — no requirement/ticket
  ids in code comments (`// CLI-4`, `// JIRA-123`).
- No name stutter: `pkg.Thing`, not `pkg.PkgThing`; exempt a name fixed by an
  external contract when the file pins it with a compile-time assertion
  (`var _ Contract = (*T)(nil)`) and a godoc saying why.
- Group related consts into one `const (...)` block with a headline comment
  naming the group; keep each member's own godoc. Reserve standalone `const`
  for a value with no relatives.
- Every exported symbol and the package have godoc.
- No godoc on interface-implementing methods.
- Use godoc cross-references: `[Type]`, `[pkg.Symbol]`.
- Wrap errors with `%w` and add context; never swallow the error.
- Handle each error exactly once.
- Never write output (errors included) to stdout/stderr from library/leaf/mid-level
  functions; return an error (`%w`) or output as a value.
- Discard an intentionally-ignored return explicitly with `_` (`_, _ =
  fmt.Fprintf(w, ...)`); never leave it bare, so the discard reads as deliberate.
- Export sentinel errors as `ErrXxx`; unexported as `errXxx`.
- Keep wrap context short and meaningful; no `failed to ...` prefixes.
- Match errors with `errors.Is`/`errors.As`, never `==`.
- `context.Context` is the first parameter when used; never store it in a struct.
- Respect `ctx.Err()`; stop work and propagate cancellation.
- Accept interfaces, return concrete types; keep interfaces small.
- No naked returns in non-trivial functions.
- Assert implementations at compile time: `var _ Iface = (*T)(nil)` near the
  top of the file.
- Make the zero value useful or at least safe.
- No work in `init()`; no package-level mutable state or singletons.
- nolint: no space `//nolint:name`; line-level at end of line; func-scoped as
  the last godoc line after an empty `//`; comma-join multiple (`a,b`).
- Provide `Example*` for non-trivial public APIs; they must pass `go test`.
- A reusable package ships a `README.md` (or `doc.go` package overview):
  purpose, import path, and one runnable usage example; skip `main`,
  `internal`, and test-only packages.

## Test

- Table-driven subtests via `t.Run`; one case per table row.
- Keep the table-test loop body branch-free — every row runs the same
  assertions; move any case needing different assertions to its own test.
- Call `t.Helper()` in test helpers.
- Test helpers must use `tester.T` to allow testing with `tester.Spy`.
- Keep assertion style consistent with the project's chosen library.
- Assert on output text unique to the expected result, never a token shared
  with other outputs (the program name, a common prefix); the assertion must
  fail if the wrong branch printed. Prefer whole-string `Equal` when the output
  is small and fixed; reach for `Contain` only on a distinctive substring.
- Hoist a literal expected value into a `want` local rather than wrap an
  assertion call past 80 cols.
- Every new func/method (exported or not) ships with tests in the same change.
- When a test guards a struct's field count, a new field must both bump the
  count and gain an assertion in the same change — never bump the count alone.
- Cover error paths and edge cases, not just the happy path.
- Subtest names use only `[a-zA-Z0-9 _-]`; keep them flat, no `/`.
- Error-path subtest names start with `error - ` then the failure condition;
  don't restate "returns error".
- Prepare every value passed to the `--- When ---` call in `--- Given ---`;
  never construct an argument inline in the call.
- Declare those `--- Given ---` argument variables in the same left-to-right
  order the `--- When ---` call uses them; keep a variable's setup next to its
  declaration.
- Name tests `Test_Func` and `Test_Type_Method`; add `_tabular` for table tests.
- Use `tester.Spy` (not raw `*testing.T`) when testing test helpers.
- Simple test helpers shared within a package live in `all_test.go`; do not
  scatter them across individual `_test.go` files.
- In `foo_test.go` with a matching `foo.go`, test functions follow the
  declaration order of their subject in `foo.go`; `Test_Foo` precedes
  `Test_Foo_tabular`; files without a 1-to-1 name match are exempt.
