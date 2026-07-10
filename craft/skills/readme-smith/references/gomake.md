# Go example injection (gomake)

Applies when the project is Go, examples belong in the README, and the
`:project:doc-eg` gomake target is available. Examples are generated from
runnable code instead of hand-written snippets, so the README cannot drift
from code that compiles.

## Workflow

1. **Detect.** Run `gomake --help` and confirm `:project:doc-eg` is listed. If
   absent, hand-write examples as usual.
2. **Author runnable examples first.** Write them as Go testable `Example…`
   functions in `_test.go`; run `go test ./...` until they pass.
3. **Mark the spots.** Above each ```go fence where an example belongs, write
   a one-line `<!-- gmdoceg:… -->` marker — see Marker keys below.
4. **Inject with gomake.** Run `gomake :project:doc-eg`; it fills each marked
   fence with the matching `Example…` function's body and `// Output:` block.
5. **Never hand-edit injected fences or ship unbacked snippets.** To change an
   injected example, edit its `Example…` function and re-run the target. A
   `go` snippet not backed by a passing `Example…` function is drift.

## Marker keys

Place each marker directly above an empty `go` fence:

````markdown
Use a buffer for stdout to capture program output without touching `os.Stdout`:

<!-- gmdoceg:pkg/foo/ExampleNew -->
```go
```
````

The marker key is `<relpath>/<FuncName>`: the exact `Example…` function name
(Go conventions: `ExampleType_method`, `ExampleFunc_suffix`) prefixed by the
example package's directory **relative to the Markdown file** — e.g.
`pkg/foo/ExampleNew` for a README at the repo root. Drop the prefix only when
the `_test.go` lives in the same directory as the file (`relpath` `.`). A bare
`<!-- gmdoceg:ExampleNew -->` silently no-ops when the example is in a
subpackage. One marker per example; the tool refreshes the fence in place —
never hand-edit the fence content, edit the function and re-run.

The injected body *and its `// Output:`* land verbatim in the fence, so the
function must obey the template's **No horizontal scroll** rule: keep its
lines short and split long output rather than printing one wide line. A dump
like `fmt.Printf("%q\n", wireBytes)` overflows — print the value in pieces
(e.g. loop over `bytes.Split(b, []byte("\r\n"))`, one `%q` per line) instead.
