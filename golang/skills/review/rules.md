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
- No name stutter (Production)
- Example functions for public APIs (Production)
- Reusable package ships a README (Production)
- Wrap with %w, hide with %v (Production)
- ErrXxx sentinels (Production)
- Assert on distinctive output, not shared tokens (Test)
- Hoist a literal expected value into `want` (Test)
- Test helpers in all_test.go (Test)
- Test order mirrors source order (Test)
- Field-count guard forces new-field coverage (Test)
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

## No name stutter (Production)

Why: `pkg.PkgThing` or `m.MetaGet` makes the reader say the qualifier twice;
dropping the redundant prefix is the Go convention and reads cleaner.
Exemption: a member name is load-bearing when it is fixed by a contract outside
the package — a method set some other type is asserted against, or names invoked
by string via `text/template`, reflection, or (de)serialization — because
renaming it breaks those callers with no local compile error. Do not flag such a
name when the file pins the set with a compile-time assertion (`var _ Contract =
(*T)(nil)`, often against a locally-declared mirror interface) plus a godoc
explaining the external contract.
Detect: a member name repeating its type or package qualifier (`Meta.MetaGet`,
`client.ClientDo`). Before flagging, look in the same file for a `var _ ... =`
assertion or an interface whose method set contains the name; if one is present
with a rationale comment, treat the name as intentional and skip it. Absent any
such pin, flag it as before.

```go
// Not stutter — the prefix is pinned by an external contract:
type metaContract interface {
	MetaGet(key string) any
	// ...
}

var _ metaContract = Meta(nil) // Renames break external callers; fail here.
```

## Example functions for public APIs (Production)

Why: `Example*` functions are compiled and executed by `go test`, so unlike
prose in a doc comment they cannot silently rot; they render on pkg.go.dev as
the canonical usage; and writing one exercises the public API from a caller's
seat, exposing awkward signatures before users hit them.
Detect: a non-trivial exported symbol — a constructor, a primary entry point,
anything needing non-obvious setup — with no matching `Example`, `ExampleT`, or
`ExampleT_method` in the package's `_test.go` files. Skip trivial getters,
setters, and self-evident one-liners. The common trigger is new public API in a
diff with no accompanying example.

```go
// Package under review exports NewClient; a runnable example doubles as docs
// and a compile-checked usage test:
func ExampleNewClient() {
	c := goldkit.NewClient("host")
	fmt.Println(c.Ping())
	// Output: pong
}
```

## Reusable package ships a README (Production)

Why: godoc documents the API symbol by symbol, but a reader landing on the
repository or on pkg.go.dev first needs orientation — what the package is for,
how to import it, and one worked example to copy. A package with thorough
godoc can still be opaque without that overview.
Detect: a package meant for outside consumption (not `main`, `internal`, or
test-only) whose directory has no `README.md` and no `doc.go` package-overview
comment beyond a one-line synopsis; or one present but missing the essentials —
stated purpose, import path, and at least one runnable usage snippet. Scope to
the module root and each public sub-package; do not demand a README per file.

## Wrap with %w, hide with %v (Production)

Why: `%w` keeps the cause inspectable via `errors.Is`/`errors.As`; `%v`
flattens it. Use `%v` only to deliberately hide the cause.
Detect: `fmt.Errorf("... %v", err)` where callers likely need to match the
cause; `==` comparison of a wrapped error.

## ErrXxx sentinels (Production)

Why: exported, matchable error values; the `Err` prefix is the Go convention.
Detect: exported error vars without the `Err` prefix; errors compared with `==`
instead of `errors.Is`.

## Assert on distinctive output, not shared tokens (Test)

Why: an assertion is only as good as its discriminating power. Checking that
output *contains* a token shared by several outputs — the program name, a
`cfsync:` prefix, a word in both the version banner and the usage text — passes
even when the wrong branch ran, so it proves almost nothing. The assertion must
be able to fail if the code printed the wrong thing. `assert.NotEqual(t, "",
out)` (merely "something was printed") is the degenerate case: it can never
distinguish correct output from garbage.
Detect: `Contain` on a token that also appears in a sibling test's expected
output; assertions against the binary/package name; `NotEqual(t, "", ...)` or
`len(out) > 0` as the only content check. Prefer whole-string `Equal` when the
output is small and fixed; otherwise pick a substring unique to the wanted
branch (`"cfsync dev\n"`, not `"cfsync"`).

```go
// avoid — "cfsync" is in both the version banner and the usage text:
assert.Contain(t, "cfsync", tst.Stdout())

// prefer — only the version branch prints exactly this:
want := "cfsync dev\n"
assert.Equal(t, want, tst.Stdout())
```

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
