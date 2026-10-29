# Go style — Test

Rules for `*_test.go` files, on top of `production.md`: a test file obeys
both, and a rule here overrides the Production rule it contradicts. Keyed
detection detail lives in the skill's `rules.md`, opened one entry at a time.

## Contents

- Structure
- Naming
- Assertions
- Helpers & fixtures
- Coverage

## Structure

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

## Naming

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

## Assertions

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
- Compare a time carrying an offset but no named zone with `assert.Time`
  against a named-zone `time.Date`, never `assert.Exact`, which compares zone
  names; give `assert.Exact` a string `want` only for UTC, as it parses strings
  to UTC.

## Helpers & fixtures

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
- Build fixed test times with `time.Date`, never by parsing a string literal;
  table rows hold `time.Time` fields, not strings the loop body parses.
- Use named zones (`Europe/Warsaw`) for non-UTC test times: the package's
  exported zones when it has them, else ones defined in `all_test.go`
  (`var waw = must.Value(time.LoadLocation("Europe/Warsaw"))`);
  `time.FixedZone` only when no named zone fits.
- Define trivial fixtures (`errTest = errors.New("test error")`, a zone)
  unexported in the package's `all_test.go`, exported only for an external
  `_test` package; import one from another module only when a helper returns
  it and the test asserts on it.

## Coverage

- Every new func/method (exported or not) ships with tests in the same change.
- When a test guards a struct's field count, a new field must both bump the
  count and gain an assertion in the same change — never bump the count alone.
- Cover error paths and edge cases, not just the happy path.
- Don't chase coverage: skip tests of `//go:build ignore` tools and of a test
  helper's trivial error branches that need platform tricks (a fake binary on
  `PATH`, `chmod 0`, a removed working directory); never add a production
  override (env var, hook, parameter) only so a test can reach a branch.
