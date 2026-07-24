# doc

Fix and complete Go in-source documentation, one documentable item at a time.
It reads the code, edits godoc and inline comments, verifies the result builds
and stays formatted, and reports the facts it could not confirm rather than
guessing them.

**The rule it lives by:** a comment changes only when it fails the checklist —
missing godoc, a wrong lead, an inaccurate or stale claim, a missing
non-obvious fact, bad prose, or an inline comment that restates the code. A
comment that is correct and complete by that checklist is left alone, however
short. "Too dry" means a checklist fact is missing, never that a comment looks
short.

It writes to the `style` "Godoc & comments" rules. Run `/review` after to audit
the result.

## Usage

```
/doc ./pkg/foo                package (default): iterate item by item, plan-first
/doc func=Foo                 one function's godoc + body comments; runs straight
/doc func=T.Bar               one method
/doc pkg/svc/foo.go:42        the item enclosing that line
/doc pkg/svc/foo.go           every item in the file, plan-first
/doc module                   every package, sequential, plan-first
/doc ./pkg/foo max_changes=8  cap comments changed this run
/doc module packages=svc,api  module mode: restrict to these packages
/doc ./pkg/foo only=godoc     skip inline body comments
/doc ./pkg/foo only=exported  package comment + exported symbols only
/doc module fanout            module mode: one subagent per package, merged
```

A documentable item is the package comment, a declaration's godoc, or one
function's inline comments.

## Controls

```
/doc ./pkg/foo max_changes=8          # cap comments changed this run
/doc module packages=svc,api          # module mode: restrict packages
/doc ./pkg/foo only=godoc             # skip inline body comments
/doc ./pkg/foo only=exported          # public API surface only
```

- `max_changes=N` — cap on comments changed; reports what is left.
- `packages=a,b` — module mode only; restrict to these packages.
- `only=godoc` — declaration and package godoc only; skip inline comments.
- `only=exported` — package comment and exported symbols only.
- `fanout` — module mode only; one subagent per package, merged report. Keeps
  the main context lean on large modules.

## Relationship to style and review

- `style` — the "Godoc & comments" rules this skill writes to (lead with the
  symbol name, full sentences, cross-refs, no godoc on interface methods).
- `doc` — fixes and completes the comments, then verifies the build.
- `review` — run it after to audit the result for correctness and style.
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

### 3. Never touches directives or interface-method godoc

**Request:** `/doc ./pkg/io` on a package with a `//go:build` line, a
`//go:generate` directive, and a `Read` method that implements `io.Reader` and
carries a godoc comment.

**Expected behavior:**
- Leaves both directive comments byte-for-byte unchanged.
- Flags the `Read` godoc for removal (style forbids godoc on
  interface-implementing methods); never rewrites it as prose.
- Presents these as never-touch / flagged items in the plan before writing.

### 4. Terse output

**Request:** `/doc func=Foo`.

**Expected behavior:**
- No preamble or narration ("I'll now read the code…"); opens with the result.
- Lists changes made (`file:Symbol — item`), flagged, and never-touched items,
  each once, with no closing restatement of the edits just shown.
