# SRD Errata Class

The bulk-appliable defect class. A defect whose fix changes only surface form,
never what a requirement *says*, is errata: `review` collects it under
`## Errata` and `edit autofix` applies the whole block behind one confirmation.
Because nobody reviews the fixes individually, the class is drawn to make a
false positive impossible rather than unlikely. Classify against the gate,
the allowlist, and the exclusions below, never by feel.

## The gate

A finding is errata **only if** its fix can be stated as an exact literal
substitution, `old → new`, anchored to one named id or verbatim heading, where
`old` appears in that anchor and nowhere ambiguous within it. If the fix has to
be described in prose ("reword", "restate with the system as subject", "make it
consistent"), it is **not** errata, however small it looks.

Three consequences:

- `old` and `new` must survive the review file's 80-column wrapping: keep each
  under roughly 40 characters, and never let a substitution straddle a line
  break. A fix that cannot be quoted that tightly is not errata.
- Whitespace and glyph fixes carry a class plus a neighboring word, never a
  literal span. Quoting whitespace is forbidden (wrapping destroys the proof),
  so state "two consecutive spaces before the word *in*" and let `edit autofix`
  derive the canonical fix from the class.
- One fix repeated identically across sites is one finding, but it MUST name
  every site, so `autofix` can verify it found exactly that many.

## Allowlist

Nothing outside this list is errata.

- Misspelling of a clearly intended word: `Authentiction → Authentication`,
  `massage → message`, `U ser → User`. The intended word must be beyond doubt
  from the sentence.
- British → US spelling: `behaviour → behavior`, `grey → gray`,
  `standardised → standardized`, `cancelled → canceled`.
- Whitespace: trailing spaces; two consecutive spaces where one belongs; a
  space trapped inside a bold identifier.
- Glyph: a curly quote closing with the wrong direction; a hyphen where a
  parenthetical dash belongs; a stray backslash or other leftover markup glyph.
- Emphasis markers: unbalanced or stray `**`; bold leaking into the middle of a
  sentence; a bolded section heading; a malformed bold identifier
  (`**AC-3: ** → **AC-3:** `).
- Missing terminal period on a requirement.
- Closed-form orthography: `can not → cannot`, and like joins or splits where
  the part of speech leaves one correct form.
- A uniquely determined function word: an article, preposition, or infinitive
  `to` whose absence is ungrammatical and whose insertion is the only
  grammatical repair (`force users re-authenticate → force users to
  re-authenticate`). If more than one insertion works, it is not errata.
- Heading case matched to the document's own convention:
  `## In scope → ## In Scope` when every sibling heading is title-cased.
- Boilerplate the standard fixes verbatim: the STR-8 keyword notice.

## Exclusions

These stay out of `## Errata` even when a literal substitution exists:

- Text inside a code span, a URL, a quoted UI string, or a product, device, or
  proper name. The "misspelling" may be the real spelling.
- Inserting or deleting a content word (noun, verb, adjective) or any normative
  keyword.
- Any change to a requirement identifier: its spelling, number, prefix, or
  order.
- Subject, voice, or mood: passive → active, or "the user interface MUST" →
  "the system MUST" (LANG-1). These are rewrites, not surface form.
- Capitalizing a term to its glossary form. Whether the site means the defined
  term or the generic sense is author judgment, not surface form.
- Line wrapping or reflow.
- Any case with two plausible corrections, or where the intended word is
  genuinely in doubt. Classify conservatively: when in doubt, not errata.
