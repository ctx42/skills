# review deep rules

The reviewer reasons from the **Principles** below; the terse rule of record for
every convention lives in `../style/SKILL.md`. The keyed entries here add only
what a capable reviewer can't infer from that one-line rule — a non-obvious
detection heuristic or an exemption. Consult an entry when you're about to flag
its rule; don't preload the file. Grows via `/review add`.

## Contents

**Principles** — earn every token · name for what it is · separate groups ·
output & errors at the right layer · keep functions pure · assertions must fail ·
name the overflow.

Keyed entries:

- No name stutter (Production)
- Method over a single-receiver-arg func (Production)
- Name a helper for behavior, not its caller (Production)
- No godoc on interface-implementing methods (Production)
- Use godoc cross-references (Production)
- Example functions for public APIs (Production)
- Reusable package ships a README (Production)
- Output belongs to the entry point, not leaf functions (Production)
- Name the overflow (Production + Test)
- Blank line between distinct groups (Production + Test)
- Three-letter receivers and matching locals (Production)
- Don't wrap a one-liner in a test helper (Test)
- Assert on distinctive output, not shared tokens (Test)
- must.Value for error not under test (Test)
- Test helpers in all_test.go (Test)
- Test order mirrors source order (Test)
- Field-count guard forces new-field coverage (Test)

## Principles

Reason from these; reach for a keyed entry only for a rule's non-obvious detail.

1. **Earn every token.** Flag text the signature, the reader, or the terse rule
   already carries: godoc that paraphrases the name/params, a doc comment
   duplicating an interface, a helper wrapping one expression, a `want` that
   saves no width, an `x, err :=` + `assert.NoError` dance where the error isn't
   under test. Trim to the non-obvious or cut it.
2. **Name for what a thing is or does, not where it sits** — no qualifier
   stutter (`pkg.PkgThing`), a method over a func taking one receiver-typed arg,
   a helper named for its behavior not its caller, `ErrXxx` sentinels, typed
   receivers and matching locals.
3. **Separate distinct multi-line groups with a blank line** — switch cases,
   test topic groups, const groups. Group by subject, not by statement type.
4. **Handle output and errors at the right layer.** A leaf returns values and
   errors; the command entry point owns the streams and the exit code. Wrap with
   `%w` (hide the cause with `%v` only deliberately), match with
   `errors.Is`/`errors.As` never `==`, handle each error exactly once.
5. **Keep functions pure and reusable** — return the computed value; leave
   presentation (trailing newline, padding) and destination (stdout/stderr) to
   the caller.
6. **An assertion must be able to fail.** Pin the output or error cause unique to
   the wanted branch, never a token shared across sibling paths.
7. **When a line overflows 80 cols, name the overflowing piece** as a local — a
   `format` string, a split literal, a `want` value — rather than wrapping the
   call across lines.

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

## Method over a single-receiver-arg func (Production)

Why: `p.cacheFile()` reads as an operation on the page; `cacheFile(p)` reads as
an outside procedure that happens to need one. A method groups behavior with the
type, shortens call sites, and lets a chain collapse — `p.encode()` then
`p.write(path)` beats threading a value through free functions. The receiver
names the type, so drop any type suffix from the name (`encodePage` → `encode`)
per No name stutter.
Exemption: the arg is one of several equals (no clear receiver); the func must
match a signature (sort, http handler, callback); or it is deliberately typeless
(→ `helpers.go`).
Detect: an unexported func with a single local-type parameter and no
signature-contract reason to stay a func. Convert to a method, update callers to
`p.f()`, rename its test to `Test_T_f`.

## Name a helper for behavior, not its caller (Production)

Why: `cached(path)` implies cache semantics, but a plain `os.Stat` existence
check is domain-agnostic; the caller-derived name misleads and blocks reuse.
`fileExists` states the contract. Generalize incidental wrap text too
("checking cache file" → "checking file"). Boolean predicates read third-person
singular: `fileExists`, not `fileExist`.
Detect: a helper named for a caller/domain (`cached`, `writeConfig`) whose body
touches only stdlib fs/string/math ops, no domain type.

## No godoc on interface-implementing methods (Production)

Why: the interface declaration is the canonical doc; repeating it on each
implementation duplicates text that rots. The only allowed comment is a one-line
reference.
Detect: a method whose signature matches an implemented interface and that
carries a full godoc comment.

```go
// implements [io.WriterTo].
func (e *Encoder) WriteTo(w io.Writer) (int64, error) { ... }
```

## Use godoc cross-references (Production)

Why: `[Type]`/`[pkg.Symbol]` render as links and stay greppable; bare names rot
on rename.
Detect: prose naming another in-package symbol without brackets ("source for
Makefile code" → "source for [Makefile] code"). Skip the comment's own leading
name and lowercase concepts ("a target"). When editing a comment, apply to the
whole comment, not just the line you came for.

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
func ExampleNewClient() {
	c := goldkit.NewClient("host")
	fmt.Println(c.Ping())
	// Output: pong
}
```

## Reusable package ships a README (Production)

Why: godoc documents the API symbol by symbol, but a reader landing on the
repository or on pkg.go.dev first needs orientation — what the package is for,
how to import it, and one worked example to copy.
Detect: a package meant for outside consumption (not `main`, `internal`, or
test-only) whose directory has no `README.md` and no `doc.go` package-overview
comment beyond a one-line synopsis; or one present but missing the essentials —
stated purpose, import path, and at least one runnable usage snippet. Scope to
the module root and each public sub-package; do not demand a README per file.

## Output belongs to the entry point, not leaf functions (Production)

Why: whether a message is an error or a normal result, and whether it goes to
stdout or stderr, is a policy decision — one that belongs to the single place
that also owns the process exit code (the command's `Main`/entry point). A leaf
or mid-level function that prints hard-codes that policy, can't be reused in a
context that wants the output elsewhere (a server, a test, a different stream),
and splits error handling across two layers. This is stricter than "never
log-and-return": it forbids *any* stdout/stderr write from non-entry functions,
not just logging an error you also return.

Return the output text (or a small result value) alongside `error`; the entry
point writes results to stdout, errors to stderr, and maps the error to an exit
code. Do not pass `os.Stdout`/`os.Stderr`/a writer into a function so it can
report its own errors — passing a sink for streamed *data* is fine, reporting
*errors/results* through it is not.

```go
// avoid — leaf decides stream and swallows the return into an exit code:
func run(cfg *Config) int {
	if err := do(cfg); err != nil {
		fmt.Fprintf(os.Stderr, "run: %s\n", err)
		return 1
	}
	return 0
}

// prefer — leaf returns; Main decides:
func run(cfg *Config) (string, error) {
	out, err := do(cfg)
	if err != nil {
		return "", fmt.Errorf("run: %w", err)
	}
	return out, nil
}
```

Detect: `fmt.Fprint*`/`fmt.Print*`/`log.*` to `os.Stdout`/`os.Stderr` (or an
injected writer used for error/result reporting) anywhere but the command entry
point; a function returning an `int` exit code instead of an `error`; a
function that both prints an error and returns (or absorbs) it.

## Name the overflow (Production + Test)

Why: when a call or literal pushes past 80 cols, hoisting the overflowing piece
into a named local reads cleaner than breaking the call across lines — the args
stay on one line and the value gets a name. Three forms:

- a printf-family format string → a `format` local (the whole `fmt` family:
  `Errorf`, `Sprintf`, `Printf`, …, not just `Sprintf`);
- a long string literal → per-line `"..."` segments joined with `+`, led by an
  empty `"" +` on the opening line so every segment aligns vertically and each
  `\n` stays explicit; never a raw backtick string for multi-line content in
  indented code (it must start at column 0 and hides trailing whitespace);
- a long expected value in a test → a `want` local.

Inverse: don't hoist when the inlined call already fits <=80 — a `want` that
saves no width is needless indirection.
Detect: a call wrapped only to fit length; a multi-line backtick string in
indented code; quoted segments where the first trails the `:=` and the rest hang
below it misaligned.

```go
// format local:
format := "cannot parse toolchain version %q"
return fmt.Errorf(format, runtime.Version())

// string literal — leading "" + aligns every segment:
content := "" +
	"host: example\n" +
	"account: a@ex.com\n"

// want local — names the expectation, keeps the assert on one line:
want := "flag provided but not defined: -unknown\n"
assert.Equal(t, want, tst.Stderr())
```

## Blank line between distinct groups (Production + Test)

Why: multi-line groups serving different subjects read as one wall when run
together; a blank line between them makes each scannable. Group by the subject,
not by statement type. Applies to multi-line switch cases (none before the
first; one-line cases need no spacing) and to statement groups inside a
`--- Given ---`/`--- Then ---` block (assert the return, then inspect a recorded
request, then check auth).
Detect: three-plus consecutive statements splitting into distinct subjects (a
fresh `:=` target read/asserted, a different value under inspection) with no
blank line between the groups; multi-line switch cases with no blank between.

```go
// test block — return value, request, auth each their own group:
assert.NoError(t, err)
assert.Contain(t, "ok (v3)", have)

req := srv.Request(0)
assert.Equal(t, "/api/v2/pages/1", req.URL.Path)

user, pass, ok := req.BasicAuth()
assert.True(t, ok)
```

## Three-letter receivers and matching locals (Production)

Why: `p` carries no type information; a fixed `pag`/`cfg` reads as its type
everywhere, and reusing it for locals names one value the same in production
and test.
Detect: a single-letter receiver; a local of type `*T`/`T` named other than the
type's receiver abbreviation.

```go
// avoid:               // prefer:
func (p *page) ...      func (pag *page) ...
p := &page{...}         pag := &page{...}
```

In tests the value under test is still `have`, not the type name — the have/want
rule wins over receiver-mirroring.

## Don't wrap a one-liner in a test helper (Test)

Why: a helper whose whole body is one expression adds a name and an indirection
without hiding any complexity — the call site reads no worse inlined. The one
benefit a thin wrapper sometimes carries is centralizing a repeated literal (a
golden-fixture path, a magic filename); a `const` does that without the function.
Detect: a `func(...) T { t.Helper(); return oneExpr }` in a `_test.go` file.
Inline it at every call site. If it existed only to avoid repeating a literal,
declare that literal as a `const` and inline the expression.

```go
// avoid — helper wraps a single expression at 5 call sites:
func pageBody(t tester.T, d pageData) []byte {
	t.Helper()
	return goldkit.Create(t, "testdata/page.tpl.yml", d).Body()
}

// prefer — const for the shared path, expression inlined:
const pageTpl = "testdata/page.tpl.yml"
body := goldkit.Create(t, pageTpl, d).Body()
```

## Assert on distinctive output, not shared tokens (Test)

Why: an assertion is only as good as its discriminating power. Checking that
output *contains* a token shared by several outputs — the program name, a
`cfsync:` prefix, a word in both the version banner and the usage text — passes
even when the wrong branch ran, so it proves almost nothing. `assert.NotEqual(t,
"", out)` (merely "something was printed") is the degenerate case: it can never
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

Applies to errors too: a wrapper prefix (`"reading config"`) passes for any
failure in that stage. Assert the cause's unique substring, or pin wrapper and
cause with one `ErrorRegexp`. A dispatch test is the same trap — if `--test`
and `--pull` both fail at config-load, `"reading config"` proves neither ran;
drive it to an X-only outcome.

```go
// avoid — every load failure produces this wrapper:
assert.ErrorContain(t, "parsing config", err)

// prefer — pins wrapper and the invalid-YAML cause in one match:
assert.ErrorRegexp(t, "parsing config.*cannot start any token", err)

// avoid — stacked contains for one error:
assert.ErrorContain(t, "encoding page 7", err)
assert.ErrorContain(t, "invalid character", err)

// prefer — one regexp:
assert.ErrorRegexp(t, "encoding page 7.*invalid character", err)
```

## must.Value for error not under test (Test)

Why: in the `--- Given ---` arrange step and the `--- Then ---` readback, a
value-plus-error call is plumbing — the error is not what the test asserts, so
`x, err := f(); assert.NoError(t, err)` is three lines of noise around one
value. `must.Value(f())` / `must.Values(f())` (`ctx42/testing/pkg/must`) panic
on error, failing the test at that line with the same effect and less ceremony.
The boundary is the assertion target: the error returned by the `--- When ---`
call *is* the thing under test — keep `out, err := f(...)` and assert on `err`
there. Never swap the subject call for `must`.
Detect: a `_, err :=`/`x, err :=` outside the When step immediately followed by
`assert.NoError(t, err)` where `err` is not otherwise inspected; the value feeds
setup or a later assertion. Leave the When call's error check alone.

```go
// avoid — error is plumbing, not the assertion:
want, err := p.MarshalJSON()
assert.NoError(t, err)

// prefer:
want := must.Value(p.MarshalJSON())
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
```

## Field-count guard forces new-field coverage (Test)

Why: `assert.Fields(t, N, T{})` is a tripwire — it fails when `T` gains or loses
a field so the author is forced to update the test's per-field assertions.
Bumping `N` to make it compile/pass without adding an assertion for the new
field silences the tripwire and defeats its only purpose.
Detect: a diff that changes the `N` in `assert.Fields` (or adds a struct field)
without adding an assertion referencing the new field in the same change.
