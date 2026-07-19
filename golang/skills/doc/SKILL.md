---
name: doc
description: >
  Fixes and completes Go in-source documentation — package godoc, symbol
  godoc, and inline comments — one documentable item at a time. Use to
  document, fix, correct stale or inaccurate comments, or fill missing godoc
  across a function, a line, a file, a package, or a module.
license: MIT
argument-hint: "[func=NAME | FILE:LINE | FILE.go | ./pkg | module]
  [max_changes=N] [packages=a,b] [only=godoc|exported] [fanout]"
---

# doc

Executing skill: it reads code, edits godoc and inline comments in `*.go` /
`*_test.go`, and verifies. Unlike `/review` it acts on the code.

**Governing rule — a comment changes only when it fails the checklist.** Judge
every documentable item against the checklist below; change it only for a
checklist item that fires, and apply the minimal edit that clears it. A comment
that is correct and complete by the checklist is left alone, however short.
"Too dry" means a checklist fact is missing — never that a comment looks short.
The documentable item — never the file — is the unit of work.

Sources of truth:
- `../style/SKILL.md` (on-demand: before writing a comment — read only its
  "Godoc & comments" section, plus Naming) — obey it in every comment written;
  it is the rule spec, do not restate it.
- The package's own comment conventions, then a sibling package (on-demand:
  when writing) — for voice and cross-reference style.

## Target

`$1` is the target token; read controls from the rest of `$ARGUMENTS`. Resolve
`$1` to one of five execution kinds (fall back to the user's prose if it is not
one of the forms below). Each fixes an order; always work it one documentable
item at a time.

- function / method — `func=Foo` or `func=T.Bar`. Its godoc plus its body's
  inline comments. Run straight (no plan gate), then report.
- line — `path/to/foo.go:42`. Resolve to the enclosing item (declaration or
  inline comment) and run its loop. Run straight, then report.
- file — `path/to/foo.go`. Every item in the file, top to bottom. Plan-first.
- package (default) — a path like `./pkg/foo` or an import path. Files
  alphabetically; within each, items top to bottom. Plan-first.
- module (opt-in) — `./...`, a `go.mod` dir, or an explicit "module".
  Packages alphabetically, sequentially by default (see `fanout` in
  Controls); within each package, files alphabetically; within each file,
  items top to bottom. Plan-first.

A documentable item is one of: the package comment (once per package, in the
package-named file), a top-level declaration's godoc (type, func, method,
const/var block), or the inline comments inside one function body.

State the resolved kind and the item set before reading.

## Controls

Read from `$ARGUMENTS`, any order after the target:
- `max_changes=N` — hard cap on comments changed this run; report what is left.
- `packages=a,b` — module mode: restrict to these packages.
- `only=godoc` — skip inline body comments; touch declaration and package
  godoc only.
- `only=exported` — touch the package comment and exported symbols only;
  skip unexported godoc and inline comments.
- `fanout` — module mode: dispatch one subagent per package (each gets the
  style rules and this per-item loop for its package) and merge the per-package
  reports. Use on large modules to keep the main context lean; packages are
  independent, so ordering is preserved per package.

## The checklist

Run each item against the code; it is a yes/no read, not a judgment of length.
Change the comment only for an item that fires.

1. missing — an exported symbol or the package has no godoc. Add it.
2. wrong lead — godoc does not start with the symbol name (Go convention).
   Fix it.
3. inaccurate — the comment contradicts the code (stale signature, renamed
   param, changed behavior). Correct it to match the code.
4. missing fact — a fact the signature cannot express is absent and
   non-obvious: a precondition or invariant on inputs, ownership or mutation of
   a passed argument, nil / zero-value behavior, the error *conditions* (not
   just "returns an error"), concurrency safety, units or encoding, or a side
   effect. Add only that fact.
5. bad prose — not a full sentence, ungrammatical, or names the receiver
   variable instead of the type. Fix per style.
6. restates code — an inline comment narrates what the next line plainly does
   instead of explaining why. Tighten to the why, or delete it.
7. interface-method godoc — a method implementing an interface (pinned by a
   `var _ Iface = (*T)(nil)` assertion) carries godoc. Remove it when the
   method does nothing unexpected vs. the interface contract; keep it,
   expanded to name the surprise (a side effect, an empty/zero return on
   success, state left unrecorded), when it does. Never add godoc to an
   unremarkable one. If the method carries a `//nolint` directive, never
   delete the block — keep the directive verbatim and give it a godoc: terse
   if unremarkable, expanded if unexpected.

## Accuracy

Never write a fact you cannot confirm from the code. Before writing a claim,
establish ground truth: read the signature, the body, and (for a type) its
fields and methods. Confirm anything that reaches beyond the visible code with
the `LSP` tool, same discipline as `review`:

- `hover` / `goToDefinition` — confirm signatures, types, and zero values.
- `findReferences` / `goToImplementation` — confirm a behavior, concurrency,
  or "callers must" claim before asserting it.
- Confirm every godoc cross-reference `[Type]` / `[pkg.Symbol]` resolves to a
  real symbol; downgrade an unresolved one to plain text.

A fact you cannot confirm from code is flagged in the report, never guessed
into a comment. If no Go language server is configured the tool errors — fall
back to reading the code and note the reduced confidence.

## Per-item loop

For each item, work in strict order. **Never start item B until item A is
edited and verified.**

1. Read the code the item documents; establish ground truth (see Accuracy).
2. Run the checklist; note every item that fires. None fires — leave it
   untouched, do not restate the report line.
3. Confirm each fact you will write (see Accuracy); demote the unverifiable to
   a flag.
4. Apply the minimal edit that clears the fired items — add only the missing
   fact, fix only the wrong clause. Obey the style Godoc rules and `max_changes`.

## Never touch

Never edit these; name them in the report when in scope:
- magic directive comments (`//go:build`, `//go:embed`, `//go:generate`,
  `//nolint`, `//export`) — they are code, never reflow or reword them.
- generated files marked `DO NOT EDIT`.
- a comment whose intent cannot be confirmed from the code — flag it, do not
  guess.

## Plan (file / package / module)

Before writing, present:
- per item in scope: which checklist items fire (`file:Symbol — item`),
- items to be flagged unverifiable (`file:Symbol — the unconfirmable fact`),
- never-touch items in scope (`file:Symbol — reason`).

Wait for approval. Then write and verify, one item to completion before the
next.

## Write

- Apply the minimal edit; do not rewrite a comment that only needed a clause.
- Obey the style "Godoc & comments" rules (already read); improvise nothing
  beyond them.
- Package comment goes in the package-named file; never add a `doc.go` for it.
- Mirror the package's own comment voice; if none, a sibling package's.
- Respect `max_changes` and the `only=` filter.

## Verify

End of run:
1. Run `gofmt -l` on every edited file; fix any issue (a rewrap can break the
   ≤ 80-col rule).
2. Run `go build ./<pkg>` on every edited package; it must pass — guards
   against a directive comment broken by an edit.
3. Run `go test ./<pkg>` only if the package already has `Example*` or
   doc-comment tests; they must still pass. Never create them (out of scope).

## Output

- Changes made: `file:Symbol — which checklist item`.
- Flagged unverifiable: `file:Symbol — the fact left unwritten and why`.
- Never-touched in scope: `file:Symbol — reason`.
- Module mode: which packages were done and which were skipped.
- Items left alone need no line. Never skip a flagged or never-touched item
  silently. Suggest running `/review` on the result.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/golang/doc.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
