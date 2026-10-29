# Go style — Production

Rules for every `*.go` file, `*_test.go` included: Test inherits these unless
a rule in `test.md` overrides one. Keyed detection detail lives in the skill's
`rules.md`, opened one entry at a time.

## Contents

- Formatting
- Naming
- Component names
- Functions & methods
- Declarations & files
- Godoc & comments
- Errors
- Output & environment
- API design
- Docs & examples

## Formatting

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

## Naming

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
- Name a predicate for the test it makes: `IsXxx` when the whole value must
  qualify, `HasXxx` when one part suffices; an empty value fails an `IsXxx`
  check.

## Component names

- SQL query functions end in `Qry` (`XxxQry`, `XxxInsertQry`); a filter or
  query-parameter struct ends in `Query`, never `Qry`.
- Name the aggregate store interface `DataStore` and a per-entity one
  `<Entity>Store`.
- Name a service-layer interface `Service` and its implementation `Svc`.
- An HTTP API area's constructor is `NewEndpoints`, its handler methods
  `XxxHandler`, and each route has an exported `HN<Name>` name constant.
- A generated mock's file is `<snake_iface>_mock.go`; a test-support package
  is the package name plus `test` (`foo` → `footest`).
- A CLI command is a constructor `XxxCmd()` in `xxx_cmd.go` with an exported
  handler named `Xxx`, the constructor's name minus `Cmd`; shared flag helpers
  are `FlgXxx`; program-wide constants are `ProgramName`, `CfgFilePath`, and
  `CfgKeyPrefix`.
- Name a package's config key constants `Cfg<Name>`, its struct `Config`, and
  its constructor `NewConfig`.

## Functions & methods

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

## Declarations & files

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

## Godoc & comments

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

## Errors

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
- SQL query functions wrap driver errors with `xrr.Wrap` and an `aux` metadata
  field naming `<pkg>.<Func>`, in place of a `%w` wrap, never both.

## Output & environment

- Never write output (errors included) to stdout/stderr from library, leaf, or
  mid-level functions; return an error (`%w`) or output as a value.
- A function that needs an environment variable takes `*ring.Ring` and reads it
  via `rng.EnvGet`/`EnvLookup`; never `os.Getenv`.

## API design

- `context.Context` is the first parameter when used; never store it in a
  struct.
- Respect `ctx.Err()`; stop work and propagate cancellation.
- Accept interfaces, return concrete types; keep interfaces small.
- Assert implementations at compile time: `var _ Iface = (*T)(nil)` near the
  top of the file.
- Make the zero value useful or at least safe.
- No work in `init()`; no package-level mutable state or singletons.

## Docs & examples

- Provide `Example*` for non-trivial public APIs; they must pass `go test`;
  skip `main`, `internal`, and test-only packages.
- A reusable package ships a `README.md` (or a package-godoc overview):
  purpose, import path, and one runnable usage example; skip `main`,
  `internal`, and test-only packages.
