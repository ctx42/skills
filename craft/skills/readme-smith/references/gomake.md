# Go example injection (gomake)

Applies when the project is Go, examples belong in the README, and the
`:project:doc-eg` gomake target exists. Examples are generated from runnable
code instead of hand-written snippets, so the README cannot drift from code
that compiles.

## Workflow

1. Detect: run `gomake --help` and confirm `:project:doc-eg` is listed. If
   absent, hand-write the examples.
2. Author runnable examples first: Go testable `Example…` functions in
   `_test.go`; run `go test ./...` until they pass.
3. Mark the spots: above each `go` fence where an example belongs, write a
   one-line `<!-- gmdoceg:… -->` marker (see Marker keys).
4. Inject: run `gomake :project:doc-eg`; it fills each marked fence with the
   matching function's body and `// Output:` block, refreshing it in place on
   re-runs.
5. Never hand-edit an injected fence or ship an unbacked snippet: to change an
   example, edit its `Example…` function and re-run the target. A `go` snippet
   not backed by a passing `Example…` function is drift.

## Marker keys

Place each marker directly above an empty `go` fence:

````markdown
Use a buffer for stdout to capture program output without touching `os.Stdout`:

<!-- gmdoceg:pkg/foo/ExampleNew -->
```go
```
````

The key is `<relpath>/<FuncName>`: the exact `Example…` function name (Go
conventions: `ExampleType_method`, `ExampleFunc_suffix`) prefixed by the
example package's directory relative to the Markdown file — `pkg/foo/ExampleNew`
for a README at the repo root. Drop the prefix only when the `_test.go` lives in
the same directory as the README. A bare `<!-- gmdoceg:ExampleNew -->` silently
no-ops when the example is in a subpackage. One marker per example.

The injected body and its `// Output:` land verbatim, so the function must obey
the template's No horizontal scroll rule: keep its lines short and split long
output rather than printing one wide line — e.g. loop over
`bytes.Split(b, []byte("\r\n"))` with one `%q` per line instead of
`fmt.Printf("%q\n", wireBytes)`.
