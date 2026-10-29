# SRD Errata Class

The bulk-appliable defect class. A defect whose fix changes only surface form,
never what a requirement *says*, is errata: `review` collects it under
`## Errata` and `edit autofix` applies the whole block behind one confirmation.
Because nobody reviews the fixes individually, the class is drawn to make a
false positive impossible rather than unlikely. Classify against the gate,
the allowlist, and the exclusions below, never by feel.

## Contents

- The gate
- Allowlist
- Exclusions

## The gate

A finding is errata **only if** its fix can be stated as an exact literal
substitution, `old → new`, anchored to one named id or verbatim heading, where
`old` appears in that anchor and nowhere ambiguous within it. A duplicated id
is no anchor: under one, the fix is errata only when `old` occurs under exactly
one of the duplicates and the finding names which by its text. If the fix has to
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
  `standardised → standardized`, `cancelled → canceled`, and `dialogue →
  dialog` for a UI element.
- Whitespace: trailing spaces; two consecutive spaces where one belongs; a
  space trapped inside an identifier's markup; a space directly inside an
  opening or closing quotation mark.
- Glyph: a curly quote closing with the wrong direction; a hyphen where a
  parenthetical dash belongs; a stray backslash or other leftover markup glyph.
- Emphasis and code markers: unbalanced or stray `**` or backticks; bold
  leaking into the middle of a sentence; a bolded section heading; an
  identifier whose markup breaks the format the standard sets by a misplaced
  marker or space alone (the one repair is moving it).
- Missing terminal period on a requirement.
- Closed-form orthography: `can not → cannot`, and like joins or splits where
  the part of speech leaves one correct form.
- A uniquely determined function word: an article, preposition, or infinitive
  `to` whose absence is ungrammatical and whose insertion is the only
  grammatical repair (`force users re-authenticate → force users to
  re-authenticate`). If more than one insertion works, it is not errata.
- Heading case matched to the document's own convention:
  `## Open issues → ## Open Issues` when every sibling heading is title-cased.
- A required section under a variant name, renamed to the name the standard
  sets for it: `## <variant> → ## <the standard's name>`. Errata only when no
  heading already carries the canonical name and the variant is the only
  candidate for it; heading level stays as found.
- Boilerplate with one fixed form: the keyword notice the standard requires.
  This is the one entry that cannot meet the 40-character rule above — the
  notice is a multi-line block with two URLs — so it is quoted as the whole
  block and applied by replacing it entire: both `old` and `new` quoted in
  full, every line verbatim with its leading `>` and the callout header line
  included, or applying it unreviewed breaks the callout. That works because
  its text is fixed: there is exactly one correct form to replace it with,
  which is what makes the substitution safe to apply unreviewed. No other long fix
  inherits this exemption. The one correct form is the notice text the
  standard fixes for an SRD, else the default notice in `srd-template.md`
  (`[!INFO]` callout, "in this document"); notice text in the standard that
  describes the standard itself is never the replacement. Its anchor is the
  notice block itself, which appears once; its location is the SRD section
  that holds it, named as the review file names sections (the block above the
  first section by the name the standard gives it).
- A missing keyword notice: an insertion the class admits, since its text
  and place are both fixed. `old` is `(missing)`, `new` the correct notice
  (above) quoted in full, preceded by the heading of the section the standard
  puts it in when that section is missing too; it goes where the standard
  places it, after a TOC macro that directly precedes that place. Errata only
  when no keyword notice appears anywhere in the SRD and the standard fixes
  the place; a misplaced one is a move, not errata. Its location is the
  section the standard places it in, named as for a wrong notice.
- A missing first-use link to the shared glossary: the one coded fix outside
  whitespace and glyph, since a link target cannot meet the 40-character rule
  but `glossary_terms` fixes it. State it as "link *term* to its shared
  glossary entry" plus the anchor id holding the first use; `edit` derives the
  link, and the text and its case stay as found. Errata only when the standard
  asks for a first-use link, the term occurs nowhere before that anchor in any
  sense or form (plural, case), linked or not, no later use carries the link,
  the site means the defined term beyond doubt, and the term is no proper name
  the standard exempts from linking; otherwise an ordinary finding. Cite the
  standard's first-use link rule by its identifier. A finding anchored past
  the term's first use qualifies once re-anchored there: the same defect, its
  site corrected.
- A dead same-document anchor: a link whose `#anchor` matches no heading of the
  document, when exactly one heading is its evident target — it shares the
  anchor's distinctive words and no other heading does. `#old` → that
  heading's anchor, in the form the document's working links use; every site
  named. It keeps its `[major, reference]` tag and its `(SRD:ref …)` citation.
- A requirement-group divider (authoring guide): a missing `---` before a
  group heading in the requirements section or after the last group, or a
  stray `---` elsewhere in the body. Coded: `(missing)` → `---` or `---` →
  `(none)`, a blank line kept on each side, anchored to the verbatim heading
  directly below the line (blank lines aside), or `(end of document)` when no
  heading follows the last group; a stray `---` with no heading directly
  below it is an ordinary finding. Never a front-matter fence or a line
  inside a code block or callout. One finding per direction, each heading
  one of its sites, as the gate's repeated-fix rule allows. Cite the
  standard's divider rule, else `(SRD:house)`.
- Running-text casing the project's casing rules fix: a term those rules write
  lowercase in running text, capitalized mid-sentence (`Project` → `project`).
  Errata only when the rules lowercase it whatever its sense, so no site needs
  judgment; never at a sentence start, in a heading, glossary entry heading,
  quoted UI string, code span, or anchor. Every site named with its count.
  A local terms entry or user-interface component whose name contains the
  word (`Order Status` for `Order`) is no site and costs no judgment: name each
  as excluded (`excluding Order Status, Order Tabs`), and the finding still
  qualifies. Any other capitalized phrase holding the word (a proper name, a
  named screen) takes judgment: the whole finding is ordinary, never split
  into errata and ordinary parts. Cite the standard's
  casing rule, else `(SRD:house)`.

The first-use link and casing entries are `[minor]` and `terminology`: a
missing link or a case slip is cosmetic, never the terminology drift `major`
covers. A divider is `[minor, format]`: markup, not a missing part, even when
the standard files its rule among its document-structure rules.

## Exclusions

These stay out of `## Errata` even when a literal substitution exists:

- Text inside a code span, a URL, a quoted UI string, or a product, device, or
  proper name. The "misspelling" may be the real spelling. A space directly
  inside a quotation mark is not inside the string: the Whitespace entry
  admits it. A same-document `#anchor` is not a URL: the dead-anchor entry
  admits it.
- Inserting or deleting a content word (noun, verb, adjective) or any normative
  keyword.
- Any change to a requirement identifier: its spelling, number, prefix, or
  order.
- Subject, voice, or mood: passive → active, or "the user interface MUST" →
  "the system MUST". These are rewrites, not surface form.
- Capitalizing a term to its glossary form, or lowercasing one the project's
  casing rules do not lowercase in every sense. Whether the site means the
  defined term or the generic sense is author judgment, not surface form.
- Line wrapping or reflow.
- Any case with two plausible corrections, or where the intended word is
  genuinely in doubt. Classify conservatively: when in doubt, not errata.
