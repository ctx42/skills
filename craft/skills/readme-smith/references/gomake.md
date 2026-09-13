# Go example injection (gomake)

Applies when the project is Go, the README wants `go` example fences, and the
project itself uses gomake. Examples are generated from runnable code instead
of hand-written snippets, so the README cannot drift from code that compiles.

This replaces the drafting and writing of those fences: author and pass the
`Example…` functions first, draft the README around empty marked fences, and
let the target fill them. The README is written once, by the target.

## Workflow

1. Detect — and detect the *project*, not the machine. `:doc:mce` is a gomake
   built-in: `gomake --list` shows it in any directory on a box where gomake is
   installed, including one with no gomake config at all. That listing is a
   precondition, not evidence. The evidence is in the repo: an existing
   `<!-- gmmce:… -->` marker, a gomake config, or a gomake step in CI. Without
   one, hand-write the examples — injected fences a contributor cannot
   regenerate are worse than snippets they can read.
2. Author runnable examples first: Go testable `Example…` functions in
   `_test.go`; run `go test ./...` until they pass. These are new Go source
   files in someone's repo — take the separate confirmation `SKILL.md` requires
   before creating any of them, naming the files and their functions in one
   batch. Without that yes there is no injection: fall back to hand-written
   examples, or to reporting the finding.
3. Mark the spots: above each `go` fence where an example belongs, write a
   one-line `<!-- gmmce:… -->` marker (see Marker keys).
4. Inject: run `gomake :doc:mce`; it fills each marked fence with the matching
   function's body, refreshing it in place on re-runs. `--dir` (default `.`) is
   the tree scanned for examples, and also where the default `--file`
   (`README.md`) is looked for; `--file` is the Markdown file written. For a
   README outside the scan root, `--file` alone is enough — marker keys resolve
   against the Markdown file's own directory, not against `--dir`, so narrowing
   the scan is the only reason to pass `--dir` as well.
5. Never hand-edit an injected fence: to change an example, edit its `Example…`
   function and re-run the target. An *example* `go` fence not backed by a
   passing `Example…` function is drift. This is about example code, not every
   `go` fence — a one-line `import "…"` showing the import path is prose in a
   fence, and no `Example…` function expresses it.
6. Re-run the target after any later edit to the README. It is idempotent, so
   the cost is nil, and an edit that shifts a fence is otherwise silent.

## Marker keys

Place each marker directly above an empty `go` fence:

````markdown
Use a buffer for stdout to capture program output without touching `os.Stdout`:

<!-- gmmce:pkg/foo/ExampleNew -->
```go
```
````

The key is `<relpath>/<FuncName>`: the exact `Example…` function name (Go
conventions: `ExampleType_method`, `ExampleFunc_suffix`) prefixed by the example
package's directory **relative to the Markdown file** — `pkg/foo/ExampleNew` for
a README at the repo root. Drop the prefix only when the `_test.go` lives in the
same directory as the README. Relative to the Markdown file, not to `--dir` and
not to the module root: a `pkg/queue/README.md` beside its own example takes the
bare key even when the run scans from the repo root. A key with the wrong
prefix silently no-ops: a marker with no matching example is left untouched, so
a wrong key looks like nothing happened rather than failing. The `Found` lines
name the keys that matched — read them, not the fences.
One marker per example.

The function body lands with its trailing `// Output:` block, dedented by one
tab — without the `func` line and without the file's imports. The reader
cannot copy-paste it into a file and build it, so write the example so its
imports are obvious from the calls, and never lean on an import the snippet
does not show. It must also obey the template's No horizontal scroll rule:
keep its lines short and split long output rather than printing one wide line —
e.g. loop over `bytes.Split(b, []byte("\r\n"))` with one `%q` per line instead
of `fmt.Printf("%q\n", wireBytes)`.

## Verify the injection landed

`gomake :doc:mce` prints one `Found <key>` line per example it discovered, then
`Writing <file>`. Only the `Found` list is evidence: `Writing` prints even when
nothing matched, and the exit status is 0 either way. A marker whose key is
absent from that list was not injected and its fence still holds whatever it
held. Re-read the fence after the run; a key that never appears is usually a
missing `<relpath>/` prefix.
