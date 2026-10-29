# Severity and category — tagging a finding

How to tag each new finding `[severity, category]`, read on demand before the
first finding `review` or `walk` writes. Modes that only move, re-check, or
list findings keep the tags already written.

Defects below are named by kind, never by rule identifier: the fetched
standard decides which rule each one breaks and what that rule is called. A
kind the standard states no rule for is no finding, unless a house addition of
the authoring guide states it.

## Severity

Tag each finding:

- `blocker` — breaks the standard's acceptance criteria (its gate, bar, or
  checklist for the final lifecycle state, by whatever name it uses): a
  requirement stating more than one rule; an uncheckable requirement or one
  resting on a vague quality; an in-scope item no requirement covers
  (suspended while the in-scope list holds only the draft `--- TODO ---`
  marker); a requirement contradicting an out-of-scope item; an undefined
  term; a rule hidden in a term definition or the header; a duplicate or
  out-of-order requirement identifier; a missing forward link or required
  header value; a missing or altered obligation-keyword notice the standard
  requires; an invalid or over-claimed lifecycle value; an unresolved draft
  scaffold — the in-scope list's `--- TODO ---` marker or a non-empty
  `## TODO` section (house additions).
- `major` — real defect, does not block: style (tense, voice, sentence
  length, appearance stated instead of behavior, a double negative, an
  open-ended list), terminology drift, overlapping or duplicate requirements,
  an obligation keyword in the wrong case or the wrong section, and any
  `reference` finding — a wrong link, ticket id, or claim about the live
  system — since a reader acting on it is misled without the SRD being
  unacceptable.
- `minor` — cosmetic: British spelling, spacing, punctuation.

The rows are the common cases, not every rule the standard states. Place an
unlisted rule by what breaking it costs: the acceptance criteria (blocker), a
reader who must still act (major), the eye alone (minor). Say which tier and
why, so the next run lands in the same place. Never a fourth.

## Category

Also tag each finding with one category — two only when it genuinely carries
two — inside the same bracket as the severity, comma-separated, severity first
and the primary category next: `[major, logical, redundancy]`. Lowercase,
mandatory on every finding in every section, never a third category. One
bracket only: adjacent `][` is CommonMark reference-link syntax and renders as
a broken link in Obsidian.

Categories in precedence order — when a finding fits more than one, the higher
entry leads and the lower becomes the second tag:

- `structure` — a part the standard's layout rules require is absent,
  malformed, or out of order, or the lifecycle value is invalid.
- `logical` — two rules conflict, a case no rule covers, precedence between
  rules unstated.
- `coverage` — an in-scope item no requirement covers, a requirement
  contradicting an out-of-scope item, or a rule stated where rules do not
  live: a term definition, the header, a note, the introduction.
- `reference` — a link, ticket id, or claim about the live system that is
  wrong or stale, or a claim a KB section contradicts. The standard forbids
  no such error, so this finding cites evidence where others cite a rule: the
  corpus doc id and heading that contradict it, or the dead link.
- `redundancy` — two rules state the same thing, or one subsumes the other.
- `verifiability` — a vague quality, an unmeasurable criterion, an open-ended
  list. Judge a checkability rule against every verification method the
  standard names, not test alone: a rule no finite test proves ("MUST NOT
  limit X") may still pass by inspection or analysis.
- `atomicity` — one item carrying more than one rule, an example or note
  inside a rule where the standard forbids one, a rule stating appearance
  instead of behavior, a scope item naming more than one change.
- `terminology` — one concept under many names, an undefined term, casing that
  drifts from the term's definition, a local definition of a term the shared
  term list defines where the standard says to link it instead: check every
  local entry against that term set. A first-use link rule counts from where
  the standard says; when it says nothing, from the first section after the
  header — a use in the header owes no link. Casing drift is a finding only
  where the project's casing rules fix running-text casing: read them before
  writing one; when they leave it free, a casing-only difference is no
  finding. A rule *hidden* in a term definition is `coverage`, not this: the
  defect is a requirement in the wrong place, not a word in the wrong form.
  Two names that may differ in meaning are `logical`, asking which is meant,
  never drift asking to "use one name".
- `linguistic` — grammar, spelling, a missing word, the wrong subject or
  voice, a misplaced or lowercase obligation keyword.
- `format` — markup, the requirement-identifier form the standard fixes, id
  numbering, punctuation, spacing.

`reference` covers a wrong pointer or fact, `terminology` a diverging word
choice: an SRD that renames an existing platform concept is `terminology`.
Category is orthogonal to `## Errata`: an errata finding is `format` or
`linguistic` — `structure` for the obligation-keyword notice, `terminology`
for a shared-term link or casing fix, `reference` for a dead anchor — yet not
every such finding is errata. An obligation keyword in the introduction is
`coverage` when its sentence states a rule, `linguistic` when it does not. A
duplicate id's fix in an SRD past the lifecycle point where the standard
forbids renumbering gives the later item a fresh id and renumbers nothing.
