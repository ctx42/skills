# Severity and category — tagging a finding

How to tag each new finding `[severity, category]`, read on demand before the
first finding `review` or `walk` writes. Modes that only move, re-check, or
list findings keep the tags already written.

## Severity

Tag each finding:

- `blocker` — breaks Quality-Bar acceptance: non-atomic (REQ-1), unverifiable
  (REQ-5/6), uncovered In Scope item (SCO-2; suspended while the In Scope
  `--- TODO ---` marker stands), requirement contradicting Out of Scope
  (SCO-3), undefined term (GLO-3/STR-10), rule hidden in a glossary entry or
  metadata (GLO-1/2), duplicate or out-of-order id (REQ-3/4), missing forward
  link (STR-2/3/5/7), a missing or altered RFC 2119 / RFC 8174 keyword notice
  (STR-8), invalid or over-claimed Status (STA-*), an unresolved
  draft scaffold — the In Scope `--- TODO ---` marker or a non-empty `## TODO`
  section (house additions).
- `major` — real defect, does not block: style (LANG-1/2/5/6/7), terminology
  drift, overlapping or duplicate requirements, a normative keyword in the
  wrong case or the wrong section (LANG-3/4), and any `reference` finding —
  a wrong link, ticket id, or claim about the live system — since a reader
  acting on it is misled without the SRD being unacceptable.
- `minor` — cosmetic: British spelling, spacing, punctuation.

The rows are the common cases — STR-9/11-13, STA-4-8 and REQ-2/7/8 have
none. Place an unlisted rule by what breaking it costs: the Quality Bar
(blocker), a reader who must still act (major), the eye alone (minor). Say
which tier and why, so the next run lands in the same place. Never a fourth.

## Category

Also tag each finding with one category — two only when it genuinely carries
two — inside the same bracket as the severity, comma-separated, severity first
and the primary category next: `[major, logical, redundancy]`. Lowercase,
mandatory on every finding in every section, never a third category. One
bracket only: adjacent `][` is CommonMark reference-link syntax and renders as
a broken link in Obsidian.

Categories in precedence order — when a finding fits more than one, the higher
entry leads and the lower becomes the second tag:

- `structure` — a required part of the document is absent or malformed, or its
  lifecycle state is invalid (STR-*, STA-*).
- `logical` — two rules conflict, a case no rule covers, precedence between
  rules unstated.
- `coverage` — an In Scope item no requirement covers, a requirement
  contradicting Out of Scope, or a rule stated where rules do not live: a
  glossary entry, the metadata, a Note, the Introduction (SCO-2, SCO-3,
  GLO-1/2).
- `reference` — a link, ticket id, or claim about the live system that is
  wrong or stale, or a claim a KB section contradicts. The standard forbids
  no such error, so this finding cites evidence where others cite a rule: the
  corpus doc id and heading that contradict it, or the dead link.
- `redundancy` — two rules state the same thing, or one subsumes the other.
- `verifiability` — a vague quality, an unmeasurable criterion, an open-ended
  list (REQ-5, REQ-6, LANG-7). Judge REQ-5 against every method it names, not
  test alone: a rule no finite test proves ("MUST NOT limit X") may still pass
  by inspection or analysis.
- `atomicity` — one item carrying more than one rule, an example or note
  inside a rule, a rule stating appearance instead of behavior (REQ-1, REQ-7,
  LANG-5, SCO-1).
- `terminology` — one concept under many names, an undefined term, casing that
  drifts from the glossary (GLO-3), a local Glossary entry for a term the
  Company Glossary defines (link its first use instead, GLO-4): check every
  local entry against that term set. GLO-4's first use counts from the
  Introduction on: a use in the metadata block, Objective included, owes no
  link. Casing drift is a finding only where the project's casing rules fix
  running-text casing: read them before writing one; when they leave it free,
  a casing-only difference is no finding. A rule *hidden* in a glossary entry
  is `coverage`, not this: the defect is a requirement in the wrong place, not
  a word in the wrong form. Two names that may differ in meaning are
  `logical`, asking which is meant, never drift asking to "use one name".
- `linguistic` — grammar, spelling, a missing word, the wrong subject or
  voice, a misplaced or lowercase normative keyword (LANG-1, LANG-2, LANG-3,
  LANG-4, LANG-6).
- `format` — markup, bold identifiers, id numbering, punctuation, spacing
  (REQ-2, REQ-3, REQ-4, REQ-8).

`reference` covers a wrong pointer or fact, `terminology` a diverging word
choice: an SRD that renames an existing platform concept is `terminology`.
Category is orthogonal to `## Errata`: an errata finding is `format` or
`linguistic` — `structure` for the STR-8 notice, `terminology` for a GLO-4 link
or casing fix, `reference` for a dead anchor — yet not every such finding is
errata. A normative keyword in the Introduction is `coverage` when its sentence
states a rule, `linguistic` (LANG-3) when it does not. A duplicate id's fix in
an `ACCEPTED` SRD gives the later item a fresh id and renumbers nothing
(STA-7).
