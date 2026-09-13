---
name: reshape
description: >
  Studies how a Go project consumes a given library and proposes ranked
  changes to that library's API that would simplify the consuming code;
  read-only. Use when asked how a dependency's API could change to clean up
  the code that uses it, for an API wishlist, or for consumer-driven API
  design.
license: MIT
argument-hint: "LIB [in ./pkg] [max=N]"
---

# reshape

## Usage

```
/reshape github.com/x/y/must   consumer scope is the whole module (default)
/reshape must in ./pkg/render  restrict the consumer scope to one package
/reshape must max=5            cap proposals reported (default 8, highest impact first)
```

Consumer-driven API review. Point it at a library the project depends on; it
maps every call site, diagnoses the friction, and proposes the highest-impact
changes to the *library's* API — the ones that would most simplify the code
that uses it. It reasons only; it edits nothing.

Keep the proposals on the **library** surface. The consumer simplification is
the *payoff* shown in before/after, not the change itself — never propose
refactoring only the call sites with the API left as-is.

Sources of truth:
- `../style/SKILL.md` (on-demand: when drafting a proposal — its Naming,
  Errors, and API design sections) — the Go idioms every proposed signature
  must respect; do not restate them.
- [references/change-catalog.md](references/change-catalog.md) (on-demand: the
  entry for the archetype being drafted) — detection cue, API shape, and a Go
  before/after per archetype in the list below.

## Target

The first token of the invocation is the library; read the scope and control
from the tokens after it (fall back to the user's prose if empty):

- library — an import path (`github.com/x/y/pkg/must`), a module path, or a
  short package name the project imports. Consumer scope defaults to the current
  module.
- `in ./pkg/foo` — restricts the consumer scope to that package (or path list).
- `max=N` — caps the proposals reported (default 8), highest impact first.

## Modifiability

Detect whether the library source is editable:
- local — in this repo, reachable via a `replace` directive, or a `go.work`
  module. Source is readable → propose concrete signature/type diffs.
- external — a normal module dependency. Work from the public surface (godoc /
  the exported API) → propose at the API-shape level and note you can't diff
  internals.

## Workflow

1. Resolve target + modifiability (above); list the symbols the consumer uses.
2. Map usage with the `LSP` tool: `findReferences` on each imported symbol
   (`workspaceSymbol`/`hover` for shape), falling back to grep on the import
   path when no language server is reachable — whether none is configured or
   the harness exposes no `LSP` tool at all; say which, and that the mapping is
   textual, since grep cannot tell a same-named symbol on an unrelated type
   from a real call site. Record every call site.
3. Diagnose friction per usage pattern: repeated setup boilerplate, options
   built inline, an interface the consumer declares itself, error-string
   matching, awkward multi-returns, type assertions, a hand-rolled loop that
   wants an iterator, test scaffolding the library could ship.
4. Brainstorm across the archetypes below — force at least one structural
   option, not only local tweaks. Structural means the library takes on work
   the consumer is doing: absorb-the-sequence, move-responsibility-upstream,
   invert-control, split-the-god-func, iterator, expose-the-interface. A
   rename, a default, or one added helper is local. Draft each candidate from
   its catalog entry and against the `style` sections above.
5. Score and rank by the impact rubric.
6. Report (below).

## Change archetypes

- options-constructor — functional options replace inline struct-building or
  a long positional param list.
- default-away-a-param — a useful zero value removes an arg every call passes
  the same.
- absorb-the-sequence — move a repeated call-site sequence into one library
  call.
- batch-or-variadic — collapse a consumer loop into one call.
- iterator — a range-over-func replaces cursor/index boilerplate.
- result-type — return a named struct instead of an awkward multi-value tuple.
- sentinel-error — an `ErrXxx` + `errors.Is` support replaces string matching.
- expose-the-interface — ship the interface the consumer keeps re-declaring.
- testing-helper — ship a spy/fake/helper so consumers drop hand-rolled
  scaffolding.
- builder — a fluent builder for staged config done awkwardly inline.
- split-the-god-func — separate the modes a consumer switches a flag on.
- invert-control — take a callback or return the finished value instead of
  making the consumer orchestrate.
- generics — remove per-type duplication and call-site type assertions.
- move-responsibility-upstream — the library owns what consumers keep
  reimplementing (retry, pagination, normalization).
- shed-a-leaky-return — drop an error that can't occur, or presentation the
  caller shouldn't be forced to handle.

## Impact rubric

Rank each candidate by **net impact**, biggest first:

- reach — how many of the N uses it simplifies. Uses, not calls: a change
  that reshapes declarations rather than call sites (exposing an interface,
  adding a testing helper) has a real reach, and counting only calls would pin
  every such proposal at 0 while step 4 still requires one.
- savings — boilerplate / lines / steps removed per site.
- quality — readability, testability, fewer error-prone steps.
- cost (discount) — API breakage (additive beats breaking), implementation
  effort, blast radius on *other* consumers.

Net = reach × savings × quality, discounted by cost. Label each **High** or
**Med** — High is worth doing this quarter, Med worth doing — and lead with the
single biggest-impact change. There is no third label: a shape worth knowing
but not worth doing is a declined note under the table (see Output), so a
bottom tier would only ever name rows that belong somewhere else. Label the
Net, after the discount; the table's Breakage and Effort columns show what was
discounted, so
a High beside heavy Breakage means it survived that. A change that touches many
sites and is additive outranks a flashy structural rewrite that breaks everyone.

`max=N` caps what is reported, never what is considered, and it cuts from the
bottom of the ranked list. The forced structural option competes on Net like
everything else: if it does not make the cut, say in one line that it was
considered and what displaced it, so the cap does not silently hide the kind of
proposal the brainstorm exists to surface.

## Output

Open with the ranked payload:

1. One line: library · consumer scope · modifiability · N uses ·
   M proposals. N counts every syntactic use of the library's surface in the
   consumer scope, each once: a call to one of its functions; a method call on
   a value it owns (`src.Next()`); a composite literal of one of its types
   (`must.Options{…}`); a conversion to one of its types
   (`(*oskit.File)(nil)`); a variable, field, or parameter declared as one
   (`var doc yaml.Node`); and a reference to one of its exported constants or
   sentinel errors (`yaml.DocumentNode`, `errors.Is(err, tidy.ErrEmpty)`). A
   line using two of them counts twice; a use inside a loop counts once. Not
   files, not occurrences of the package name, not per-iteration executions.

   N is the denominator every `Reach` is a fraction of, so both must count the
   same way — a headline counting only calls beside a Reach counting literals
   makes the table unreadable.
2. A table ranked by impact — unless there are no proposals, in which case say
   so in a sentence and stop: an empty table is a shrug with borders. Name what
   you looked for and found absent, so the reader can tell a clean API from a
   shallow pass. A shape worth knowing but not worth doing is a named
   declined note there, not a row padding the table.


   | # | Change (archetype) | Reach | Impact | Breakage | Effort |

3. Then each proposal, top-down:
   - the API change — the new signature/type; a concrete diff when local, an
     API-shape sketch when external;
   - a representative call site before → after proving the payoff;
   - one line tying it to the rubric (why this impact).
4. Anything deferred or needing the user's judgment; for an external library,
   the local wrapper to use where an upstream change can't land.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md`
and `$HOME/.agent-data/ctx42-skills/lessons/golang/reshape.md`, the sibling
winning a conflict — a read-only install writes the second, and what it
learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule to the sibling when this directory
is writable, else to the fallback, creating it, and report where.