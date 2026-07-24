# reshape

Consumer-driven Go API review. Name a library the project depends on; `reshape`
maps every call site, diagnoses the friction, and proposes the highest-impact
changes to that **library's** API — the ones that would most simplify the code
using it. It reasons only and edits nothing.

**The rule it lives by:** the proposal is a change to the *library*, and the
consumer cleanup is the payoff shown in before/after — never a refactor of the
call sites with the API left alone. It brainstorms across a broad archetype
catalog (options constructors, iterators, sentinel errors, moving whole
responsibilities upstream, …), then ranks by impact so the biggest win leads.

## Usage

```
/reshape github.com/x/y/must   default: map call sites across the whole module
/reshape must in ./pkg/render  restrict the consumer scope to one package
/reshape must max=5            cap proposals reported (highest impact; default 8)
```

It detects whether the library source is editable (local module / `replace` /
`go.work` → concrete diffs) or external (public surface → API-shape proposals
plus a local-wrapper fallback).

## Relationship to style and review

- `style` — the Go idioms the proposals must respect.
- `review` — audits code you already have; `reshape` proposes changes to a
  dependency so the code you write against it is cleaner.

## Evaluations

### 1. Ranked, multi-archetype proposals — not just obvious tweaks

**Request:** `/reshape must` where the consumer wraps most `must.Value` calls in
the same three-line error-drop and builds an options struct inline at many sites.

**Expected behavior:**
- Resolves the library and consumer scope and states the call-site count first.
- Proposes changes across multiple archetypes, including at least one structural
  / out-of-the-box option (e.g. absorb-the-sequence or
  move-responsibility-upstream), not only a rename or a lone one-off helper.
- Ranks by impact (reach × savings × quality, discounted by breakage/effort) and
  leads with the biggest win; each proposal shows a call-site before → after.

### 2. Proposals stay on the library API

**Request:** `/reshape oskit in ./pkg/render`.

**Expected behavior:**
- Every proposal is a change to `oskit`'s API; the consumer diff is the payoff,
  never a call-site-only refactor with the API unchanged.
- Edits nothing — reports the proposal set and stops.

### 3. External library — public-surface proposals

**Request:** `/reshape gopkg.in/yaml.v3`, a normal module dependency.

**Expected behavior:**
- Detects the library is external; frames proposals at the public-API level and
  notes it can't diff internals.
- Offers a local wrapper as the fallback where an upstream change can't land.

### 4. Terse output

**Request:** `/reshape must max=3`.

**Expected behavior:**
- Opens with the ranked table — no preamble or narration.
- States each proposal once; no closing summary that re-lists the table already
  shown.
