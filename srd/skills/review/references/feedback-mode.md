# feedback — the plain-text issue list

The output format for `review <srd> feedback`, read on demand when that mode
runs. Every other mode can ignore this file.

Emit plain text for an email or ticket — no file write:

- Title: `<Document Title> — Review Feedback`.
- Group by section name as a plain heading (no markdown symbols). `## Errata`
  is one such group — list it first, as `Errata`, when it holds open findings.
  An errata finding keeps its substitution in prose, not markdown, and a
  casing fix its excluded terms in full, however long the bullet wraps:
  `#4 GR-2: "behaviour" should read "behavior"`.
- One bullet per open finding, blank-line separated. Keep the finding number
  and the SRD's own requirement id (`#7 GR-3a:`), then a one-line
  problem-and-fix. A finding against text with no id of its own — a metadata
  field, an Introduction sentence — is anchored the way the review file anchors
  it: the section name, and a short quote when the section holds more than one
  candidate. `#2 Metadata (Owners): only one owner is listed; add a secondary
  owner.` `#5 Introduction ("the system handles all remaining cases"): states a
  rule outside Requirements; move it or drop it.` A project instruction
  limiting author-facing lists to what is wrong and where overrides this:
  drop the fix from every ordinary bullet; an errata bullet keeps its
  substitution and excluded terms, which state what is wrong. Drop the
  checkbox, the severity tag, the category tag, and the rule-id citation;
  keep a source line, as the bullet's last sentence. No bold. One
  bullet is one paragraph — it wraps like any prose, and "no multi-line
  bullets" means no sub-bullets and no blank line inside a bullet, not a
  bullet that fits on one physical line.
- Open findings only — omit Resolved and Withdrawn.
