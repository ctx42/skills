# Go style — deep rules

Keyed detection detail for the rules in `SKILL.md` (same directory). An entry
adds only what a capable reviewer can't infer from the one-line rule — an
exemption or a detection heuristic — in two short sentences. Open an entry only
when about to flag its rule; never preload the file. Grows via
`golang:review add`.

## Contents

- No name stutter (Production)
- Method over a single-receiver-arg func (Production)
- Name a helper for behavior, not its caller (Production)
- No godoc on interface-implementing methods (Production)
- Use godoc cross-references (Production)
- Example functions for public APIs (Production)
- Reusable package ships a README (Production)
- Package godoc lives in the package-named file (Production)
- Output belongs to the entry point, not leaf functions (Production)
- Read the environment through the ring (Production + Test)
- Name the overflow (Production + Test)
- Break an over-width table row positionally (Test)
- Don't wrap a one-liner in a test helper (Test)
- Assert on distinctive output, not shared tokens (Test)
- must.Value for error not under test (Test)
- Test helpers in all_test.go (Test)
- Test order mirrors source order (Test)
- Field-count guard forces new-field coverage (Test)

## No name stutter (Production)

Exemption: a name fixed by a contract outside the package — a method set another
type is asserted against, or a name invoked by string via `text/template`,
reflection, or (de)serialization — since renaming it breaks those callers with
no local compile error. Detect: a member repeating its type or package
qualifier (`Meta.MetaGet`, `client.ClientDo`) with no same-file `var _ ... =`
pin or interface carrying the name plus a rationale comment.

## Method over a single-receiver-arg func (Production)

Exemption beyond the body's contract and typeless cases: the arg is one of
several equals with no clear receiver. Detect: an unexported func with a single
local-type parameter; convert it, update callers to `pag.f()`, and rename its
test to `Test_T_f`.

## Name a helper for behavior, not its caller (Production)

Boolean predicates read third-person singular (`fileExists`, not `fileExist`);
generalize incidental wrap text too ("checking cache file" → "checking file").
Detect: a helper named for its caller or domain (`cached`, `writeConfig`) whose
body touches only stdlib fs/string/math ops and no domain type.

## No godoc on interface-implementing methods (Production)

The only allowed comment is a one-line reference: `// implements
[io.WriterTo].` Detect: a full godoc on a method whose signature matches an
interface the type implements (confirm with `goToImplementation`).

## Use godoc cross-references (Production)

The comment's own leading name and lowercase concepts stay plain. Detect: prose
naming another in-package exported symbol without brackets, or brackets around
an unexported identifier; when editing a comment, fix the whole comment.

## Example functions for public APIs (Production)

Non-trivial means a constructor, a primary entry point, or anything needing
non-obvious setup; trivial getters, setters, and self-evident one-liners are
exempt. Detect: such a symbol with no matching `Example`, `ExampleT`, or
`ExampleT_method` in the package's `_test.go` files — typically new public API
in a diff with no accompanying example.

## Reusable package ships a README (Production)

Scope to the module root and each public sub-package; never demand one per
file. Detect: a package meant for outside consumption whose directory has
neither a `README.md` nor a `doc.go` overview beyond a one-line synopsis, or
one missing the essentials (purpose, import path, one runnable snippet).

## Package godoc lives in the package-named file (Production)

Relation: the README rule accepts a `doc.go` overview as a README substitute
only when no package-named file exists to host it. Detect: a `doc.go` whose
sole content is the package doc comment while a package-named file exists —
move the comment there and delete `doc.go`.

## Output belongs to the entry point, not leaf functions (Production)

Stricter than "never log-and-return": stream choice and exit code are policy
owned by the single entry point (`Main`), so a non-entry function returns text
or a result value plus `error` and writes nothing — passing a writer for
streamed data is fine, passing `os.Stdout`/`os.Stderr` so a function can report
its own errors or results is not. Detect: `fmt.Fprint*`/`fmt.Print*`/`log.*` to
a process stream (or an injected reporting writer) outside the entry point; a
function returning an `int` exit code instead of `error`; a function that both
prints an error and returns or absorbs it.

## Read the environment through the ring (Production + Test)

The ring (`*ring.Ring`) is the injected process environment, so `os.Getenv`
reaches around that seam and forces tests onto the global `t.Setenv`; in tests
call `rng.EnvSet` after constructing the ring, capturing any
working-directory-relative fixture path into a local first, since it mutates
the ring in place. Detect: `os.Getenv`/`os.LookupEnv` in a function that has
(or could take) a `*ring.Ring`; `t.Setenv` in a test whose subject reads env
through a ring.

## Name the overflow (Production + Test)

A raw backtick string is banned for multi-line content in indented code because
it must start at column 0 and hides trailing whitespace. Detect: a call wrapped
only to fit the width; a multi-line backtick string in indented code; `+`-joined
segments where the first trails the `:=` and the rest hang misaligned below it;
a short string local whose literal fits inline at every use.

## Break an over-width table row positionally (Test)

A row is data whose field order the anonymous struct above already fixes, so
keys add noise; this runs against the Go habit of keying multi-line struct
literals, so never "fix" a positional row back to keys. Detect: a multi-line
table-row literal using `field: value` keys, or a single-line row past the width
limit that should wrap.

## Don't wrap a one-liner in a test helper (Test)

Detect: a `func(...) T { t.Helper(); return oneExpr }` in a `_test.go` file;
inline it at every call site, and if it existed only to avoid repeating a
literal, declare that literal as a `const`.

## Assert on distinctive output, not shared tokens (Test)

`assert.NotEqual(t, "", out)` or `len(out) > 0` as the only content check is
the degenerate case — it never distinguishes correct output from garbage.
Detect: `Contain` on a token that also appears in a sibling test's expected
output (the program name, a shared wrapper prefix such as `"reading config"`);
assertions against the binary or package name; a dispatch test whose asserted
outcome more than one branch yields.

## must.Value for error not under test (Test)

`must.Value`/`must.Values` (`ctx42/testing/pkg/must`) panic on error, failing
the test at that line. Detect: an `x, err :=` outside the `--- When ---` step
immediately followed by `assert.NoError(t, err)` with `err` not otherwise
inspected; never swap the `--- When ---` call itself for `must`.

## Test helpers in all_test.go (Test)

The compiler ignores unused package-level funcs, so a dead helper in
`all_test.go` is caught only here. Detect: a helper (no `Test`/`Bench`/`Example`
prefix) defined in a `_test.go` file other than `all_test.go` and called from
more than one test file, or clearly package-wide in scope; also a helper in
`all_test.go` with no caller.

## Test order mirrors source order (Test)

Subject extraction: strip the `Test_` prefix and take everything up to the
first `_tabular` suffix, so `Test_Foo` and `Test_Foo_tabular` both map to
`Foo`. Detect: walk the test file top to bottom, record each subject's first
position in `foo.go`, and flag any subject positioned before the previous one.

## Field-count guard forces new-field coverage (Test)

The guard is `assert.Fields(t, N, T{})`: it fails when `T` gains or loses a
field so the author must update the per-field assertions. Detect: a diff that
changes `N` (or adds a struct field) without adding an assertion referencing the
new field in the same change.
