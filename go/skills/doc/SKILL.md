---
name: doc
description: >
  Fixes and completes Go in-source documentation — package godoc, symbol
  godoc, and inline comments — one documentable item at a time. Use to
  document, fix, correct stale or inaccurate comments, or fill missing godoc
  across a function, a line, a file, a package, or a module.
license: MIT
argument-hint: "[func=NAME | FILE:LINE | FILE.go | ./pkg* | module]
  [max_changes=N] [packages=a,b] [only=godoc|exported] [fanout]"
---

# doc

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

Executing skill: it reads code, edits godoc and inline comments in `*.go` /
`*_test.go`, and verifies. Unlike `go:review` it acts on the code. Scope
stops at in-source comments: never write an `Example*` function or a package
`README` overview to carry what a comment should say.

**Governing rule — a comment changes only when it fails the checklist.** Judge
every documentable item against the checklist below and apply the minimal edit
that clears the checklist items that fire. A comment that passes is left alone,
however short: "too dry" means a checklist fact is missing, never that a
comment looks short. The documentable item — never the file — is the unit of
work.

Sources of truth:
- `../style/SKILL.md` (on-demand: before the first comment is written — read
  its Production "Godoc & comments" and "Naming" sections, plus "Formatting"
  and "Declarations & files", which the Verify step and the package-comment
  rule below both cite) — obey it in every comment written; it is the rule
  spec, do not restate it. Checklist item 7 is the one place this skill
  departs from it.
- The package's own comment conventions, then a sibling package's (on-demand:
  when writing) — for voice and cross-reference style.

## Target

The first token of the invocation is the target; read controls from the tokens
after it. Resolve that target to one of five execution kinds (fall back to the
user's prose if it is not
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

A documentable item is one of: the package comment (once per package), a
top-level declaration's godoc (type, func, method, const/var block), or the
inline comments inside one function body.

`func=Foo` names a function or, when the package has no such function and
exactly one type carries a method of that name, that method — ambiguity across
two types is an error, not a guess: say which types match and ask. `func=T.Bar`
is always the method and never guesses.

A line target resolves to the innermost item containing that line: a line in a
body is that body's inline comments, and the enclosing declaration's godoc is
*not* in scope — target the declaration by name to reach it. A line on or
inside a declaration's doc comment is that godoc.

State the resolved kind and the item set before reading.

## Controls

Read from `$ARGUMENTS`, any order after the target:
- `max_changes=N` — hard cap on comments changed this run; report what is left.
- `packages=a,b` — module mode: restrict to these packages.
- `only=godoc` — skip inline body comments; touch declaration and package
  godoc only.
- `only=exported` — touch the package comment and exported symbols only;
  skip unexported godoc and inline comments.
- `fanout` — module mode: dispatch one subagent per package (each gets The
  checklist, Accuracy, Never touch, and the Per-item loop, for its package) and
  merge the per-package reports. Use on large modules to keep the main context
  lean; packages are independent, so ordering is preserved per package.

  Merging is not accepting. Before a worker's edits enter the report, re-read
  each added or changed comment against the checklist — item 4 above all, since
  a worker that has the seven fact categories in front of it and a whole package
  to get through is exactly where an unsupported claim appears. Check every
  added fact against the code that is supposed to establish it: a concurrency
  guarantee on a type with no synchronization, an error condition no branch
  produces, a units claim nothing converts. Revert what the code does not carry
  and say so in the merged report: two workers given the same package and the
  same prompt have added and declined the very same unsupported guarantee, so
  which one you got is not something the merge can assume. The parent is the
  last checklist pass, not a stapler.

## The checklist

Run each checklist item against the code; each is a yes/no read.

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

   This item fires on a fact the code *establishes*, never on a category the
   code leaves open. A type with no synchronization is not thereby documented
   "not safe for concurrent use" — that is a conclusion about code nobody
   wrote, and the next commit can falsify it. Ask what the body proves, not
   which of the seven categories has no sentence yet: an absent guarantee is a
   silence to leave alone or a question to flag under Accuracy, not a blank to
   fill. The list is where to look, not a set of slots to complete.
5. bad prose — not a full sentence, ungrammatical, or names the receiver
   variable instead of the type. Fix per style.
6. restates code — an inline comment narrates what the next line plainly does
   instead of explaining why. Tighten to the why, or delete it.
7. interface-method godoc — a method implementing an interface the type is
   pinned to carries godoc. Pinned means the package itself commits to it: a
   `var _ Iface = (*T)(nil)` assertion, a constructor returning the interface,
   or a struct field or parameter declared as it. A type that merely happens to
   fit an interface is not pinned, and its methods are judged as ordinary
   godoc. Unremarkable vs. the
   interface contract: remove it. Surprising: keep it, expanded to name the
   surprise — the one exception to the style rule against such godoc. Never
   add godoc to an unremarkable one.

   Surprising means a caller holding the interface would be wrong about this
   implementation: it does something the contract does not license (writes
   through a second path, mutates the argument, blocks), or declines something
   the contract implies (returns an empty/zero value on success, records
   nothing, ignores an option). Doing the job the method exists to do is not a
   surprise — a `Write` that writes and a `Close` that releases are exactly
   what the contract promised, however many side effects that takes.

   A `//nolint` directive on the method is never deleted: keep it verbatim.
   The linter it silences generally wants a doc comment there, so an
   unremarkable method under one keeps the style's one-line
   `// implements [Iface].` instead of having its godoc removed — the
   directive, not the method, is what makes this the exception.
8. bad framing — godoc says a project or file lives "on disk"; a group headline
   borrows a member's contrastive phrasing instead of naming the group on its
   own terms; or a comparison equates unlike things (a project-level constant
   with an OCI image annotation). Reword. A dangling cross-reference that
   exists only for such a comparison is deleted, never downgraded to plain
   text.

## Accuracy

Never write a fact you cannot confirm from the code; flag it in the report
instead. Establish ground truth first: read the signature, the body, and (for
a type) its fields and methods. Confirm anything beyond the visible code with
the `LSP` tool:

- `hover` / `goToDefinition` — signatures, types, zero values.
- `findReferences` / `goToImplementation` — a behavior, concurrency, or
  "callers must" claim.
- Every godoc cross-reference `[Type]` / `[pkg.Symbol]` must resolve to a real
  symbol; downgrade an unresolved one to plain text.

With no Go language server the `LSP` tool errors, and a client without it
wired has no such tool at all — either way, fall back to reading the code and
note the reduced confidence in the report.

## Per-item loop

For each item, in strict order; never start item B until item A is written.

1. Read the code the item documents; establish ground truth (Accuracy).
2. Run the checklist; note every checklist item that fires. None fires —
   leave the comment untouched.
3. Confirm each fact you will write (Accuracy); demote the unverifiable to a
   flag.
4. Write the minimal edit that clears the fired checklist items — add only
   the missing fact, fix only the wrong clause; never rewrite a comment that
   needed a clause. Obey the style rules read from `../style/SKILL.md`,
   `max_changes`, and the `only=` filter. Mirror the package's comment voice,
   else a sibling package's. The package comment goes in the package-named
   file (style "Declarations & files"); never create a `doc.go` for it.

## Never touch

Never edit these; name them in the report when in scope:
- magic directive comments (`//go:build`, `//go:embed`, `//go:generate`,
  `//nolint`, `//export`) — they are code, never reflow or reword them.
- generated files marked `DO NOT EDIT`.
- a comment whose intent the code cannot confirm — flag it.

## Plan (file / package / module)

Before writing, present:
- per item in scope: which checklist items fire (`file:Symbol — item`); a
  symbol nothing fires on does not appear, so the plan stays the list of
  intended edits rather than an inventory of the package,
- items to flag unverifiable (`file:Symbol — the unconfirmable fact`),
- never-touch items in scope (`file:Symbol — reason`).

Wait for approval, then run the per-item loop and Verify.

## Verify

End of run:
1. Run `gofmt -l` on every edited file and fix any listing; then re-check that
   every edited comment line stays within the style line limit (style
   "Formatting") — gofmt does not enforce that.
2. Run `go build ./<pkg>` on every edited package; it must pass — guards
   against a directive comment broken by an edit.
3. Run `go test ./<pkg>` only if the package already has `Example*`
   functions; they must still pass. Never create them (out of scope).

## Output

- The Verify result, one line: which packages were gate-checked and that
  `gofmt -l` and `go build` passed. A gate whose outcome never reaches the
  reply is indistinguishable from one that never ran.
- Changes made, one line each, in exactly this shape:
  `file:Symbol — <checklist item #>: <what changed>`.
- Flagged unverifiable: `file:Symbol — the fact left unwritten and why`.
- Never-touched in scope: `file:Symbol — reason`.
- Module mode: which packages were done and which were skipped.
- Items left alone get no line; a flagged or never-touched item is never
  dropped silently. Close with a one-line pointer to run `go:review` on
  the result.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/go/doc.md`, the
sibling winning a conflict — a read-only install writes the second, and what it
learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule — general, naming nothing from
the project at hand (its files, tests, tickets) — to the sibling when this
directory is writable, else to the fallback, creating it, and report where.