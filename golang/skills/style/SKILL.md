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

## Production

- gofmt + goimports always; never hand-format or reorder imports manually.
- Lines <=80 cols including the `//` prefix; break only when over, one
  logical arg per line with `(` on the call line.
- When a function signature spans multiple lines, put each parameter on its own line.
- Collapse a multi-line func signature to one line when the whole signature fits <=80 (through the opening `{`, or the full type for func-typed params/fields).
- When a function signature spans multiple lines, open the body with a blank line.
- Extract a long or complex format string into a `format` local before the
  call (`fmt.Errorf`, `Sprintf`, `Printf`); prefer it to breaking the call
  across lines to fit <=80.
- Split a string literal too long for one line into per-line `"..."` segments
  joined with `+`, led by an empty `"" +` on the opening line so every segment
  aligns; keep `\n` explicit, never a raw backtick string for multi-line content.
- Comments are full sentences: capital start, terminal period.
- Comments explain the code; never trace it to a spec — no requirement/ticket
  ids in code comments (`// CLI-4`, `// JIRA-123`).
- No name stutter: `pkg.Thing`, not `pkg.PkgThing`.
- Every exported symbol and the package have godoc.
- No godoc on interface-implementing methods.
- Use godoc cross-references: `[Type]`, `[pkg.Symbol]`.
- Wrap errors with `%w` and add context; never swallow or log-and-return.
- Handle each error exactly once.
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

## Test

- Table-driven subtests via `t.Run`; one case per table row.
- Call `t.Helper()` in test helpers.
- Test helpers must use `tester.T` to allow testing with `tester.Spy`.
- Keep assertion style consistent with the project's chosen library.
- When a literal expected value would push an assertion call past 80 cols, hoist it into a `want` local on the line before instead of wrapping the call.
- Every new func/method (exported or not) ships with tests in the same change.
- When a test guards a struct's field count (`assert.Fields`), a new field must both bump the count and gain an assertion covering it in the same change — never bump the count alone.
- Cover error paths and edge cases, not just the happy path.
- Subtest names use only `[a-zA-Z0-9 _-]`; keep them flat, no `/`.
- Error-path subtests — the `--- When ---` call returns a non-nil error asserted in `--- Then ---` — start with `error - ` then the failure condition; don't restate "returns error".
- Prepare every value passed to the `--- When ---` call in `--- Given ---`; never construct an argument inline in the call.
- Declare those `--- Given ---` argument variables in the same left-to-right order the `--- When ---` call uses them; keep a variable's setup next to its declaration.
- Name tests `Test_Func` and `Test_Type_Method`; add `_tabular` for table tests.
- Use `tester.Spy` (not raw `*testing.T`) when testing test helpers.
- Simple test helpers shared within a package live in `all_test.go`; do not scatter them across individual `_test.go` files.
- In `foo_test.go` with a matching `foo.go`, test functions follow the declaration order of their subject in `foo.go`; `Test_Foo` precedes `Test_Foo_tabular`; files without a 1-to-1 name match are exempt.
