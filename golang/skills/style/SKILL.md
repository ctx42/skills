---
name: style
description: >
  Enforced Go coding style for this project; production code (non-_test.go)
  and test code (_test.go) follow different rules. Read before writing or
  editing any .go file.
license: MIT
---

# style

Authoritative Go style rules. Apply the **Production** section to `*.go` and
the **Test** section to `*_test.go`. Test code inherits Production unless a
Test rule overrides it. Do not hand-edit this file ad hoc — change rules with
`/review` (state a preference, or `/review learn` to mine an editing session).

Report tersely: when citing a rule, name it and the fix; don't restate the
rule's full text or narrate.

## Production

### Formatting

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
- Separate multi-line switch cases with a blank line; none before the first.

### Naming

- No name stutter: `pkg.Thing`, not `pkg.PkgThing`; exempt a name fixed by an
  external contract when the file pins it with a compile-time assertion
  (`var _ Contract = (*T)(nil)`) and a godoc saying why.
- Receivers are a ~three-letter type abbreviation, not a single letter:
  `pag *page`, `cfg *config`.
- A local of type `T` reuses `T`'s receiver name (`pag` for `*page`, `cfg` for
  `*config`).
- Name a helper for what it does, not its one caller: a domain-agnostic body
  gets a domain-agnostic name and error text (`fileExists`, not `cached`).

### Functions & methods

- A func whose sole parameter is a local `*T`/`T` belongs on T as a method
  (`pag.f()`, not `f(pag)`); drop the type from its name (`encode`, not
  `encodePage`). Stay a func only when a signature contract (sort, http,
  callback) or deliberate typelessness (`helpers.go`) requires.
- Don't wrap a single expression in a one-line function used at a single call
  site; inline it (Test has the same rule for helpers).
- A method returns only its named result; leave presentation (trailing
  newline, padding) to the caller.
- No naked returns in non-trivial functions.
- Order a function body so cheap, fallible checks (config reads, validation)
  run before expensive or side-effecting work; fail fast before the heavy work.

### Declarations & files

- Group related consts into one `const (...)` block with a headline comment
  naming the group; keep each member's own godoc. Reserve standalone `const`
  for a value with no relatives.
- Put the package godoc comment in the file named after the package (`foo.go`
  in package `foo`) when one exists; don't keep a separate `doc.go` for it.
- Keep package-wide top-level declarations (exported consts/vars) in the
  package-named file, not a separate topic-named file; same principle as the
  package-godoc rule above.
- Domain-agnostic, typeless helpers (`fileExists`, `isDigits`) live in
  `helpers.go`, their tests in `helpers_test.go` — mirrors `all_test.go`.

### Godoc & comments

- Comments are full sentences: capital start, terminal period.
- Godoc prose is grammatically correct English: articles, subject-verb
  agreement, restrictive "that" vs "which".
- Comments explain the code; never trace it to a spec — no requirement/ticket
  ids in code comments (`// CLI-4`, `// JIRA-123`).
- Every exported symbol and the package have godoc.
- Godoc states only what the signature can't; never restate the obvious.
- In godoc prose name the type, not the receiver variable.
- No godoc on interface-implementing methods.
- Use godoc cross-references: `[Type]`, `[pkg.Symbol]`.
- nolint: no space `//nolint:name`; line-level at end of line; func-scoped as
  the last godoc line after an empty `//`; comma-join multiple (`a,b`).

### Errors

- Wrap errors with `%w` and add context; never swallow the error.
- Handle each error exactly once.
- Reuse an already-declared `err` with `=`; only the first check in a scope
  uses `:=`.
- Discard an intentionally-ignored return explicitly with `_` (`_, _ =
  fmt.Fprintf(w, ...)`); never leave it bare, so the discard reads as deliberate.
- Export sentinel errors as `ErrXxx`; unexported as `errXxx`.
- Keep wrap context short and meaningful; no `failed to ...` prefixes.
- Match errors with `errors.Is`/`errors.As`, never `==`.

### Output & environment

- Never write output (errors included) to stdout/stderr from library/leaf/mid-level
  functions; return an error (`%w`) or output as a value.
- A function that needs an environment variable takes `*ring.Ring` and reads it
  via `rng.EnvGet`/`EnvLookup`; never `os.Getenv`.

### API design

- `context.Context` is the first parameter when used; never store it in a struct.
- Respect `ctx.Err()`; stop work and propagate cancellation.
- Accept interfaces, return concrete types; keep interfaces small.
- Assert implementations at compile time: `var _ Iface = (*T)(nil)` near the
  top of the file.
- Make the zero value useful or at least safe.
- No work in `init()`; no package-level mutable state or singletons.

### Docs & examples

- Provide `Example*` for non-trivial public APIs; they must pass `go test`.
- A reusable package ships a `README.md` (or `doc.go` package overview):
  purpose, import path, and one runnable usage example; skip `main`,
  `internal`, and test-only packages.

## Test

### Structure

- Table-driven subtests via `t.Run`; one case per table row.
- When a table row exceeds the line limit, break it one element per line,
  positional in field order — never add field-name keys.
- Keep the table-test loop body branch-free — every row runs the same
  assertions; move any case needing different assertions to its own test.
- Prepare every value passed to the `--- When ---` call in `--- Given ---`;
  never construct an argument inline in the call.
- Declare those `--- Given ---` argument variables in the same left-to-right
  order the `--- When ---` call uses them; keep a variable's setup next to its
  declaration.
- Separate distinct topics within a `--- Given ---`/`--- Then ---` block with a
  blank line; group statements by the subject they set up or verify.
- In `foo_test.go` with a matching `foo.go`, test functions follow the
  declaration order of their subject in `foo.go`; `Test_Foo` precedes
  `Test_Foo_tabular`; files without a 1-to-1 name match are exempt.

### Naming

- Name tests `Test_Func` and `Test_Type_Method`; add `_tabular` for table tests.
- Subtest names use only `[a-zA-Z0-9 _-]`; keep them flat, no `/`.
- Keep subtest names terse — name the condition or trigger, not a full sentence.
- Error-path subtest names start with `error - ` then the failure condition;
  don't restate "returns error".
- Name the actual value `have` and the expected value `want`, never `got`; when
  several of each coexist in one scope, suffix as `hXxx`/`wXxx` naming the value.
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
- Hoist an expected literal into a `want` local only to keep the assertion
  within 80 cols; inline it when the call already fits.
- Hoist a multi-line structured-data literal (JSON, YAML) passed to a call into
  a pretty-printed backtick raw-string local; don't inline it or split it across
  `+`-joined segments to fit the line limit.

### Helpers & fixtures

- Call `t.Helper()` in test helpers.
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

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/golang/style.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
