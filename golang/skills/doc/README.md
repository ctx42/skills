# doc

Fix and complete Go in-source documentation, one documentable item at a time.

## Usage

```
/doc ./pkg/foo                package (default): item by item, plan-first
/doc func=Foo                 one function's godoc + body comments; no plan
/doc func=T.Bar               one method
/doc pkg/svc/foo.go:42        the item enclosing that line; no plan
/doc pkg/svc/foo.go           every item in the file, plan-first
/doc module                   every package, sequential, plan-first
/doc ./pkg/foo max_changes=8  cap comments changed this run; reports the rest
/doc module packages=svc,api  module mode: restrict to these packages
/doc ./pkg/foo only=godoc     skip inline body comments
/doc ./pkg/foo only=exported  package comment + exported symbols only
/doc module fanout            module mode: one subagent per package, merged
```

A documentable item is the package comment, a declaration's godoc, or one
function's inline comments.

## How it decides

It reads the code, edits godoc and inline comments, verifies the result builds
and stays formatted, and reports the facts it could not confirm rather than
guessing them.

A comment changes only when it fails the checklist — missing godoc, a wrong
lead, an inaccurate or stale claim, a missing non-obvious fact, bad prose, an
inline comment that restates the code, or godoc on an interface-implementing
method. A comment that passes is left alone, however short: "too dry" means a
checklist fact is missing, never that a comment looks short.

## Relationship to style and review

- `golang:style` — owns the "Godoc & comments" rules this skill writes to
  (lead with the symbol name, full sentences, cross-references). `doc` departs
  from it in one place: godoc on an interface-implementing method is removed
  when unremarkable but kept when it names a surprise.
- `golang:review` — run it after to audit the result for correctness and
  style.
- `doc` stops at in-source comments; it never writes `Example*` functions or a
  package `README` / `doc.go` overview.

## Evaluations

### 1. A correct-but-terse comment is left alone

**Request:** `/doc func=Get` where `Get`'s godoc is one accurate sentence that
already states everything the signature cannot.

**Expected behavior:**
- Runs the checklist and finds no item fires.
- Leaves the comment unchanged; does not pad it or restate the signature.
- Reports no change line for it.

### 2. Adds only a missing, confirmable fact — never a guess

**Request:** `/doc func=Store` where `Store` mutates a passed slice and is
safe for concurrent use, but its godoc says neither.

**Expected behavior:**
- Fires checklist item 4 (missing fact) for the mutation and concurrency.
- Confirms both against the body / callers (via `LSP`) before writing them.
- Adds only those facts; if concurrency safety cannot be confirmed from code,
  flags it as unverifiable instead of asserting it.

### 3. Never touches directives; interface-method godoc per item 7

**Request:** `/doc ./pkg/io` on a package with a `//go:build` line, a
`//go:generate` directive, and a `Read` method that implements `io.Reader` and
carries a godoc comment restating the interface contract.

**Expected behavior:**
- Leaves both directive comments byte-for-byte unchanged and lists them as
  never-touch items in the plan.
- Plans the `Read` godoc for removal (checklist item 7, unremarkable); would
  keep it, naming the surprise, only if `Read` did something the `io.Reader`
  contract does not promise.
- Writes nothing before approval.

### 4. Terse output

**Request:** `/doc func=Foo`.

**Expected behavior:**
- No preamble or narration ("I'll now read the code…"); opens with the result.
- Lists changes made (`file:Symbol — item`), flagged, and never-touched items,
  each once, with no closing restatement of the edits just shown.

### 5. A line target resolves to its item and runs straight

**Request:** `/doc pkg/svc/foo.go:42` where line 42 is inside the body of
`(*Svc).Flush`, and `// increment i` sits above `i++`.

**Expected behavior:**
- States the resolved kind (line) and the item: `Flush`'s godoc and its body's
  inline comments — nothing else in the file.
- Presents no plan; runs the loop and reports.
- Fires checklist item 6 on `// increment i` and deletes it.

### 6. Module mode with fanout and a package filter

**Request:** `/doc module fanout packages=svc,api`.

**Expected behavior:**
- The plan lists only `svc` and `api` items; every other package is reported
  as skipped.
- After approval, dispatches one subagent per package and merges their
  reports into the Output format.
- Verifies (`gofmt -l`, `go build`) every edited package before reporting.
