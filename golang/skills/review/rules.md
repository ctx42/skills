# review deep rules

Deeper notes for the non-obvious `style` rules: why they exist, a short
example, and how to detect a violation. Keyed to the terse rule in
`../style/SKILL.md`. Not every rule needs an entry — only those where
rationale or detection helps. Grows via `/review add`.

## Contents

- Extract format strings into a `format` local (Production)
- Split a long string literal with a leading `"" +` (Production)
- Use godoc cross-references (Production)
- No godoc on interface-implementing methods (Production)
- nolint directive format (Production)
- Wrap with %w, hide with %v (Production)
- ErrXxx sentinels (Production)
- Hoist a literal expected value into `want` (Test)
- Test helpers in all_test.go (Test)
- Test order mirrors source order (Test)
- Useful or safe zero value (Production)

## Extract format strings into a `format` local (Production)

Why: when a printf-style call (`fmt.Errorf`, `Sprintf`, `Printf`, …) runs past
80 cols, hoisting the format string into a `format` local is cleaner than
breaking the call across lines — the args stay on one line and the string is
named. Applies to the whole `fmt` printf family, not just `Sprintf`.
Detect: a multi-line-wrapped `fmt.Errorf`/`Sprintf`/`Printf` call whose only
reason to wrap is length; or an inline format string long/complex enough to
obscure the args.

```go
// avoid — call broken across lines just to fit:
return fmt.Errorf(
	"cannot parse toolchain version %q", runtime.Version(),
)

// prefer:
format := "cannot parse toolchain version %q"
return fmt.Errorf(format, runtime.Version())
```

## Split a long string literal with a leading `"" +` (Production)

Why: a raw backtick string for multi-line content must start at column 0,
breaking the surrounding indentation, and hides trailing whitespace. Quoted
per-line segments joined with `+` keep the block indented and make every `\n`
explicit. The leading `"" +` puts the first real segment on its own line so
all segments align vertically instead of the first one trailing the `:=`.
Detect: a multi-line backtick string embedded in indented code; or quoted
segments where the first sits on the `:=` line and the rest hang below it
misaligned.

```go
// avoid — first segment trails the assignment, rest misalign:
content := "host: example\n" +
	"account: a@ex.com\n"

// prefer:
content := "" +
	"host: example\n" +
	"account: a@ex.com\n"
```

## Use godoc cross-references (Production)

Why: `[Type]`/`[pkg.Symbol]` render as links and stay greppable; bare names rot
on rename.
Detect: prose naming another in-package symbol without brackets ("source for
Makefile code" → "source for [Makefile] code"). Skip the comment's own leading
name and lowercase concepts ("a target"). When editing a comment, apply to the
whole comment, not just the line you came for.

## No godoc on interface-implementing methods (Production)

Why: the interface declaration is the canonical doc; repeating it on each
implementation duplicates text that rots.
Detect: a method whose signature matches an implemented interface and that
carries a full godoc comment. The only allowed comment is a one-line reference.

```go
// implements [io.WriterTo].
func (e *Encoder) WriteTo(w io.Writer) (int64, error) { ... }
```

## nolint directive format (Production)

Why: `nolint` is a machine directive like `//go:build`. The no-space form
`//nolint:name` is the canonical, portable spelling: gofmt-stable, greppable,
and accepted by every golangci-lint version. Spaced forms (`// nolint`,
`//nolint: x`) are tolerated by some versions but not guaranteed — don't rely
on them.
Detect: a space anywhere in the directive, or a directive on the wrong line.

```go
x := unsafeCall() //nolint:gosec

// Decode parses p.
//
//nolint:gocognit
func Decode(p []byte) (T, error) { ... }
```

## Wrap with %w, hide with %v (Production)

Why: `%w` keeps the cause inspectable via `errors.Is`/`errors.As`; `%v`
flattens it. Use `%v` only to deliberately hide the cause.
Detect: `fmt.Errorf("... %v", err)` where callers likely need to match the
cause; `==` comparison of a wrapped error.

## ErrXxx sentinels (Production)

Why: exported, matchable error values; the `Err` prefix is the Go convention.
Detect: exported error vars without the `Err` prefix; errors compared with `==`
instead of `errors.Is`.

## Hoist a literal expected value into `want` (Test)

Why: an assertion wrapped only to fit a long literal reads worse than naming the
value; a `want` local keeps the call on one line and names the expectation.
Detect: an assertion call broken across lines solely because a string/composite
literal argument overflows.

```go
// avoid — call wrapped just to fit the literal:
assert.Equal(t,
	"flag provided but not defined: -unknown\n", tst.Stderr())

// prefer:
want := "flag provided but not defined: -unknown\n"
assert.Equal(t, want, tst.Stderr())
```

## Test helpers in all_test.go (Test)

Why: shared test helpers (e.g. `saveVars`, fixture builders) placed in
individual `_test.go` files are easy to miss and may be duplicated. A single
`all_test.go` file in the package is the canonical home — one place to look,
one place to maintain.
Detect: a helper function (no `Test`/`Bench`/`Example` prefix, not in a
`*test` package) defined in a `_test.go` file that is not named `all_test.go`
and is called from more than one other test file, or whose scope is clearly
package-wide rather than local to one test. Also flag the reverse: a helper in
`all_test.go` with no caller — the compiler ignores unused package-level funcs,
so dead helpers must be caught here and removed.

## Test order mirrors source order (Test)

Why: a reader navigating between `foo.go` and `foo_test.go` expects to find the
test for a function near where the function sits in the source; mismatched order
forces mental re-mapping and hides missing coverage.
Applies only when `foo_test.go` has a 1-to-1 name match with `foo.go`. Files
like `all_test.go` are exempt.
Subject extraction: strip the `Test_` prefix and take everything up to the
first `_tabular` suffix — `Test_Foo` and `Test_Foo_tabular` both map to `Foo`.
When multiple tests share a subject, the plain variant (`Test_Foo`) must precede
the tabular variant (`Test_Foo_tabular`).
Detect: walk the test file top-to-bottom, extract each subject, record its
first position in `foo.go`; flag any subject whose position is less than the
previous subject's position.

```go
// foo.go order: A, B, C
// bad foo_test.go order:
func Test_A(t *testing.T) { ... }
func Test_C(t *testing.T) { ... } // C before B — violation
func Test_B(t *testing.T) { ... }
func Test_B_tabular(t *testing.T) { ... }

// good foo_test.go order:
func Test_A(t *testing.T) { ... }
func Test_B(t *testing.T) { ... }
func Test_B_tabular(t *testing.T) { ... }
func Test_C(t *testing.T) { ... }
```

## Field-count guard forces new-field coverage (Test)

Why: `assert.Fields(t, N, T{})` is a tripwire — it fails when `T` gains or loses
a field so the author is forced to update the test's per-field assertions.
Bumping `N` to make it compile/pass without adding an assertion for the new
field silences the tripwire and defeats its only purpose.
Detect: a diff that changes the `N` in `assert.Fields` (or adds a struct field)
without adding an assertion referencing the new field in the same change.

## Useful or safe zero value (Production)

Why: callers can use `var x T` without a constructor, or at least not crash.
Detect: methods that panic on a zero-valued receiver; types that require an
init call before any method is safe.
