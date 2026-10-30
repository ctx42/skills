# The review file

How `<srd>.review.md` (the SRD's `review` working file; its path is in
`project-config.md`, "5. Working files") is laid out, numbered, cited, and
ordered. Read before
writing or updating one — every mode that touches the file needs it, and no
mode needs it before then.

## Contents

- Numbering and shape
- Citations
- Anchors and wrapping
- Layout
- Frontmatter and worked example
- What the sections still owe

## Numbering and shape

Every finding carries a global sequential number (`#1..#N`): a plain integer,
permanent, never reused and never renumbered. The next number is `max(all
numbers across open + Resolved + Withdrawn) + 1` — no stored counter; the file
is self-describing.

Each finding is atomic — one indivisible fix, verifiable by a single yes/no. If
two edits can be verified or resolved separately, they are two findings, even
when they share one root cause. No bullet says "do A and B".

Two rules breaking on one edit is the mirror case and resolves the same way: a
lifecycle value that violates both a prerequisite rule (say, a sign-off the
final state needs) and the rule gating the final state on the acceptance
criteria takes one correction and one yes, so it is one finding. Cite the rule
the fix is derived from and name the other in the text; when both derive it,
cite the gating rule and name the prerequisite one. A final-state value that
breaks a prerequisite rule always takes that citation, even when the
acceptance criteria are otherwise met — never the prerequisite rule alone.
Atomicity is about the fix, not about how many rules the defect trips.

Open finding shape — number first, then severity, then category (`ABC-1`
stands for a rule identifier of the fetched standard, `XY-3a` for the SRD's
own requirement id):

`- [ ] #7 [blocker, atomicity] XY-3a: problem — fix. (SRD:ABC-1)`

## Citations

Close each finding with the identifier of the rule it breaks, as the fetched
standard writes it, namespaced `SRD:` — `(SRD:ABC-1)`. Cite only identifiers
that standard states; never one from memory, from another standard, or no
longer in it. A spelling, punctuation, or spacing finding cites the standard's
rule that covers it when one does, else `(SRD:house)`. A consistency-pass
finding cites `(SRD:consistency)` and sits under the section where the conflict
surfaces; a house-addition finding (US English, draft scaffolds, terminology
drift) cites the fetched standard's id when the standard states that rule —
check it before citing — else `(SRD:house)` (authoring guide). When both could
fit — the consistency pass surfaced it, a house addition defines it — cite the
house addition's citation: the rule that defines the defect outranks the pass
that spotted it, so terminology drift never cites `(SRD:consistency)`. A
`reference` finding cites its evidence in the same slot and the same shape, the
document's `id` as identity —
`(SRD:ref 1774485611#tag-names)` for a corpus contradiction,
`(SRD:ref kb/x.md#heading)` for a KB one (its fix offers both ways out: align
the SRD, or confirm the SRD's fact so the KB changes),
`(SRD:ref <the dead link>)` for a broken pointer — so every finding closes with
a parenthesis a reader can act on, and none carries a rule identifier the
fetched standard does not state.

## Anchors and wrapping

Locate by identifier, never by line number: anchor each finding to the SRD's
own id — requirement (`XY-3a`), scope item, or defined term — or, when no id
fits, to the section name verbatim plus a short quote of the offending text;
a header field is anchored as the header plus the field name as the SRD
writes it. Never invent shorthand such as `§1.3`; line numbers shift with
formatting. Never quote literal doubled or trailing whitespace as evidence;
describe it in words ("two consecutive spaces before the word *in*"), because
wrapping the review file normalizes whitespace and destroys the quoted proof.

Wrap every finding at 80 columns, breaking onto continuation lines indented two
spaces. Only a single unbreakable token (a long URL or path), or a verbatim
line of the obligation-keyword notice inside its erratum, may overflow. A
`*(Partial — …)*` note starts its own continuation line.

## Layout

In order:

1. `## Errata` first — every open finding that passes the gate and allowlist of
   the errata class in `errata.md`, grouped here instead of under its document
   section so the author can bulk-apply the block via `edit autofix`. The
   literal heading `## Errata` is the anchor `edit autofix` locates; never
   rename it. Errata findings keep their global number, category, and citation,
   and carry the severity the rule gives them — usually `[minor]`, but the
   allowlist admits the obligation-keyword notice, whose severity is blocker,
   and a dead anchor, which stays `major` like every `reference` finding. The
   class decides whether a finding can be bulk-applied; it does not decide how
   bad the finding is, and a blocker filed as `[minor]` because of where it sits
   would drop out of the count that gates the acceptance criteria. Each states
   its fix as the exact substitution the class requires — literal
   `` `old` → `new` ``, or for whitespace and glyph classes the class plus a
   neighboring word (`autofix` derives the fix), or for a missing
   obligation-keyword notice `` `(missing)` → `` the full notice, or for a
   requirement-group divider (`[minor, format]`, never `structure`: markup,
   even when the standard files its rule among its layout rules) the heading
   plus `` `(missing)` → `---` `` or `` `---` → `(none)` `` — and a
   substitution repeated across sites lists every site so `autofix` can verify
   the count; a casing fix also names, in the same finding, the terms it
   excludes. Two different substitutions are two
   findings. Omit the section when empty.
2. Open findings, grouped by document section: one `##` heading per part of
   the SRD the standard's layout defines, named as the SRD names it — the
   block above the first section under the name the standard gives it (its
   header or metadata) — in the standard's layout order; a section the
   standard does not define follows in the SRD's own order. Omit a section
   with no open findings. An errata finding lives in `## Errata`, never also
   under its document section.
   No `---` between these sections — the rule separates the file's parts
   (Errata, open findings, Resolved, Withdrawn), not the document sections
   inside the open part.
3. A `---` line, then `## Resolved`: fixed findings as `- [x] #7 …`, a flat
   list sorted by number, keeping the original text and rule id and appending
   what closed it (`— added XY-11`). Keep, then append: a rewritten finding
   loses what was wrong, and the pair is what makes the entry readable a month
   later.
4. A `---` line, then `## Withdrawn` (last):
   `- #9 … (withdrawn <YYYY-MM-DD HH:MM>: <reason>)` — no checkbox, keeps the
   number. The stamp is the withdrawing run's `updated:` value, which
   `edit summary` uses to date the withdrawal; an unstamped entry stays as
   found.

## What the sections still owe

All four are omitted while empty: a first review writes only the sections it
has findings for. Empty headings promise a history the file does not have.

A finding lives in exactly one place. Regression: a resolved finding that
breaks again moves back to its open section, unticked, keeping its number.

Separate consecutive findings with exactly one blank line in every section;
one blank line after a section heading before its first finding.

## Frontmatter and worked example

The metadata is YAML frontmatter with lowercase keys; `prepared` and `updated`
carry a date and time. `updated:` moves only when something else in the file
moved with it: a mode that resolves nothing, appends nothing, and re-sorts
nothing writes no bytes at all, so a second run over an unchanged SRD leaves a
file byte-identical to the first run's. This governs every mode that writes the
file; none bumps the timestamp unconditionally.

```
---
prepared: YYYY-MM-DD HH:MM
updated: YYYY-MM-DD HH:MM
source: path/to/srd.md
---

# SRD Review — <Document Title>

## Errata

- [ ] #8 [minor, linguistic] VIEW-4 uses British spelling: `colour` → `color`.
  (SRD:house)

- [ ] #10 [minor, format] XY-3a: two consecutive spaces after the word "sensor"
  — collapse to one. (SRD:house)

- [ ] #12 [minor, linguistic] XY-6, XY-9 and DET-2 drop the infinitive:
  `force users re-authenticate` → `force users to re-authenticate`.
  (SRD:house)

---

## Requirements

- [ ] #3 [blocker, atomicity] XY-3a: states two rules ("validate ... and log
  ...") — split into one rule each. (SRD:ABC-1)

- [ ] #5 [major, redundancy] XY-7 and XY-9 state the same limit in different
  words — merge or remove one. (SRD:consistency)

---

## Resolved

- [x] #1 [blocker, coverage] In-scope item "Export to CSV" had no requirement
  — added XY-11. (SRD:ABC-2)

- [x] #4 [minor, linguistic] British spelling "behaviour" — changed to US.
  (SRD:house)

---

## Withdrawn

- #2 [major, redundancy] XY-5 seemed to overlap XY-6 (withdrawn YYYY-MM-DD
  HH:MM: distinct triggers, confirmed by author).
```
