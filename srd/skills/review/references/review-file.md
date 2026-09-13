# The review file

How `<srd>.review.md` is laid out, numbered, cited, and ordered. Read before
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
`Status` field that violates both STA-2 and STA-3 takes one correction and one
yes, so it is one finding. Cite the rule the fix is derived from and name the
other in the text. Atomicity is about the fix, not about how many rules the
defect trips.

Open finding shape — number first, then severity, then category:

`- [ ] #7 [blocker, atomicity] GR-3a: problem — fix. (SRD:REQ-1)`

## Citations

Close each finding with its rule-id citation namespaced `SRD:` — `(SRD:REQ-1)`,
`(SRD:GLO-3)`. The only rule namespaces are `STR`, `STA`, `LANG`, `REQ`, `GLO`,
and `SCO`; never cite a rule absent from
[../../create/references/srd-standard.md](../../create/references/srd-standard.md)
(e.g. a defunct `MD-*`). A consistency-pass finding cites `(SRD:consistency)`
and sits under the section where the conflict surfaces; a house-addition
finding (US English, draft scaffolds) cites `(SRD:house)`. A `reference`
finding cites its evidence in the same slot and the same shape —
`(SRD:ref ifp-doc/formats/x.md#heading)` for a corpus contradiction,
`(SRD:ref <the dead link>)` for a broken pointer — so every finding closes with
a parenthesis a reader can act on, and none carries a rule namespace that does
not exist.

## Anchors and wrapping

Locate by identifier, never by line number: anchor each finding to the SRD's
own id — requirement (`GR-3a`), scope item (`SC-12`), or glossary term — or,
when no id fits, to the section name verbatim plus a short quote of the
offending text. Never invent shorthand such as `§1.3`; line numbers shift with
formatting. Never quote literal doubled or trailing whitespace as evidence;
describe it in words ("two consecutive spaces before the word *in*"), because
wrapping the review file normalizes whitespace and destroys the quoted proof.

Wrap every finding at 80 columns, breaking onto continuation lines indented two
spaces. Only a single unbreakable token (a long URL or path) may overflow. A
`*(Partial — …)*` note starts its own continuation line.

## Layout

In order:

1. `## Errata` first — every open finding that passes the gate and allowlist of
   the errata class in
   [../../create/references/errata.md](../../create/references/errata.md),
   grouped here instead of under its document section so the author can
   bulk-apply the block via `edit autofix`. The
   literal heading `## Errata` is the anchor `edit autofix` locates; never
   rename it. Errata findings keep their global number, category, and citation,
   and carry the severity the rule gives them — usually `[minor]`, but the
   allowlist admits the STR-8 keyword notice, whose severity is blocker. The
   class decides whether a finding can be bulk-applied; it does not decide how
   bad the finding is, and a blocker filed as `[minor]` because of where it sits
   would drop out of the count that gates the Quality Bar. Each states its fix
   as the exact substitution the class requires — literal `` `old` → `new` ``,
   or for whitespace and glyph classes the class plus a neighboring word
   (`autofix` derives the fix) — and a substitution repeated across sites lists
   every site so `autofix` can verify the count. Two different substitutions are
   two findings. Omit the section when empty.
2. Open findings, grouped by document section: Metadata, Introduction,
   Glossary, Scope, Requirements. Omit a section with no open findings. An
   errata finding lives in `## Errata`, never also under its document section.
   No `---` between these sections — the rule separates the file's parts
   (Errata, open findings, Resolved, Withdrawn), not the document sections
   inside the open part.
3. A `---` line, then `## Resolved`: fixed findings as `- [x] #7 …`, a flat
   list sorted by number, keeping the original text and rule id and appending
   what closed it (`— added GR-11`). Keep, then append: a rewritten finding
   loses what was wrong, and the pair is what makes the entry readable a month
   later.
4. A `---` line, then `## Withdrawn` (last): `- #9 … (withdrawn: <reason>)` —
   no checkbox, keeps the number.

## What the sections still owe

All four are omitted while empty: a first review writes only the sections it
has findings for. Empty headings promise a history the file does not have.

A finding lives in exactly one place. Regression: a resolved finding that
breaks again moves back to its open section, unticked, keeping its number.

Separate consecutive findings with exactly one blank line in every section;
one blank line after a section heading before its first finding.

## Frontmatter and worked example

The metadata is YAML frontmatter with lowercase keys; `prepared` and `updated`
carry a date and time. Include `cfsync-plugin: ignore-push` verbatim so the
Confluence sync never pushes this generated artifact.

```
---
prepared: YYYY-MM-DD HH:MM
updated: YYYY-MM-DD HH:MM
source: path/to/srd.md
cfsync-plugin: ignore-push
---

# SRD Review — <Document Title>

## Errata

- [ ] #8 [minor, linguistic] VIEW-4 uses British spelling: `colour` → `color`.
  (SRD:house)

- [ ] #10 [minor, format] GR-3a: two consecutive spaces after the word "sensor"
  — collapse to one. (SRD:LANG-2)

- [ ] #12 [minor, linguistic] GR-6, GR-9 and DET-2 drop the infinitive:
  `force users re-authenticate` → `force users to re-authenticate`.
  (SRD:LANG-2)

---

## Requirements

- [ ] #3 [blocker, atomicity] GR-3a: states two rules ("validate ... and log
  ...") — split into one rule each. (SRD:REQ-1)

- [ ] #5 [major, redundancy] GR-7 and GR-9 state the same limit in different
  words — merge or remove one. (SRD:consistency)

---

## Resolved

- [x] #1 [blocker, coverage] SC-2 In Scope item had no requirement — added
  GR-11. (SRD:SCO-2)

- [x] #4 [minor, linguistic] British spelling "behaviour" — changed to US.
  (SRD:house)

---

## Withdrawn

- #2 [major, redundancy] GR-5 seemed to overlap GR-6 (withdrawn: distinct
  triggers, confirmed by author).
```
