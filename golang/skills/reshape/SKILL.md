---
name: reshape
description: >
  Studies how a Go project consumes a given library and proposes ranked,
  impact-scored changes to that library's API that would make the consuming
  code cleaner. Read-only: it proposes, edits nothing. Brainstorms across a
  broad catalog of change archetypes — not just obvious tweaks — and detects
  whether the library source is locally editable (concrete diffs) or external
  (public surface). Use when asked how a dependency's API could change to
  simplify the code that uses it, for an API wishlist, or for consumer-driven
  API design.
license: MIT
---

# reshape

Consumer-driven API review. Point it at a library the project depends on; it
maps every call site, diagnoses the friction, and proposes the highest-impact
changes to the *library's* API — the ones that would most simplify the code that
uses it. It reasons only; it edits nothing.

Keep the proposals on the **library** surface. The consumer simplification is
the *payoff* shown in before/after, not the change itself — never propose
refactoring only the call sites with the API left as-is.

Sources of truth:
- `../style/SKILL.md` — Go idioms the proposals must respect (accept interfaces,
  functional options, `%w`, `ErrXxx`, useful zero value).
- `references/change-catalog.md` — each archetype's detail + Go example, keyed to
  the list below. Consult an entry when drafting that proposal; don't preload it.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/golang/reshape.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.

## Target

Resolve the invocation:
- **library** — `reshape <lib>` where `<lib>` is an import path
  (`github.com/x/y/pkg/must`), a module path, or a short package name the project
  imports. Consumer scope defaults to the current module.
- **scoped** — `reshape <lib> in ./pkg/foo` restricts the consumer to that
  package (or path list).
- Control: `max=N` caps the proposals reported (default 8), highest impact first.

State the resolved library, the consumer scope, and the call-site count before
proposing.

## Modifiability

Detect whether the library source is editable, and say which:
- **local** — in this repo, reachable via a `replace` directive, or a `go.work`
  module. Source is readable → propose concrete signature/type diffs.
- **external** — a normal module dependency. Work from the public surface
  (godoc / the exported API) → propose at the API-shape level; note you can't
  diff internals, and offer a local wrapper as the fallback when a proposal can't
  land upstream.

## Workflow

High-freedom analysis — reason from the steps, the archetypes, and the rubric;
no rigid script.

1. Resolve target + modifiability (above); list the symbols the consumer uses.
2. **Map usage** with the `LSP` tool: `findReferences` on each imported symbol
   (`workspaceSymbol`/`hover` for shape), falling back to grep on the import path
   if no language server is configured. Record every call site.
3. **Diagnose friction** per usage pattern: repeated setup boilerplate, options
   built inline, an interface the consumer declares itself, error-string
   matching, awkward multi-returns, type assertions, a hand-rolled loop that
   wants an iterator, test scaffolding the library could ship.
4. **Brainstorm broadly** across the archetypes below — force at least one
   structural option, not only local tweaks. Consult `change-catalog.md` for an
   archetype's shape and example when drafting its proposal.
5. **Score and rank** by the impact rubric.
6. Report (below). Change nothing.

## Change archetypes

The brainstorm engine — reach past the obvious. Detail + example per archetype in
`change-catalog.md`.

- **options-constructor** — functional options replace inline struct-building or
  a long positional param list.
- **default-away-a-param** — a useful zero value removes an arg every call passes
  the same.
- **absorb-the-sequence** — move a repeated call-site sequence into one library
  call.
- **batch-or-variadic** — collapse a consumer loop into one call.
- **iterator** — a range-over-func replaces cursor/index boilerplate.
- **result-type** — return a named struct instead of an awkward multi-value tuple.
- **sentinel-error** — an `ErrXxx` + `errors.Is` support replaces string matching.
- **expose-the-interface** — ship the interface the consumer keeps re-declaring.
- **testing-helper** — ship a spy/fake/helper so consumers drop hand-rolled
  scaffolding.
- **builder** — a fluent builder for staged config done awkwardly inline.
- **split-the-god-func** — separate the modes a consumer switches a flag on.
- **invert-control** — take a callback or return the finished value instead of
  making the consumer orchestrate.
- **generics** — remove per-type duplication and call-site type assertions.
- **move-responsibility-upstream** — the library owns what consumers keep
  reimplementing (retry, pagination, normalization).
- **shed-a-leaky-return** — drop an error that can't occur, or presentation the
  caller shouldn't be forced to handle.

## Impact rubric

Rank each candidate by **net impact**, biggest first:

- **reach** — how many call sites it simplifies (the LSP count).
- **savings** — boilerplate / lines / steps removed per site.
- **quality** — readability, testability, fewer error-prone steps.
- **cost** (discount) — API breakage (additive beats breaking), implementation
  effort, blast radius on *other* consumers.

Net = reach × savings × quality, discounted by cost. Label each **High / Med /
Low** and lead with the single biggest-impact change. A change that touches many
sites and is additive outranks a flashy structural rewrite that breaks everyone.

## Output

Open with the ranked payload — no preamble.

1. One line: library · consumer scope · modifiability · N call sites · M proposals.
2. A table ranked by impact:

   | # | Change (archetype) | Reach | Impact | Breakage | Effort |

3. Then each proposal, top-down:
   - the **API change** — the new signature/type; a concrete diff when local, an
     API-shape sketch when external;
   - a representative **call site before → after** proving the payoff;
   - one line tying it to the rubric (why this impact).
4. Note anything deferred or needing the user's judgment; for an external library
   offer a local wrapper where an upstream change can't land.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.
