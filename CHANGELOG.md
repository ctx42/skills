## v0.22.0 (Thu, 23 Jul 2026 09:58:54 UTC)
- feat(srd-system-check): add learn and memory-clean modes.

## v0.21.0 (Thu, 23 Jul 2026 08:17:37 UTC)
- docs(srd): stop flagging external STR-4/6 back-links.

## v0.20.0 (Tue, 21 Jul 2026 19:09:59 UTC)
- docs(doc-smith): add em-dash rule and usage notes.
- docs(doc-smith): record four whole-document review lessons.
- feat(srd-edit): add Yes/Next/Skip/Edit choices to edit loop.

## v0.19.0 (Sun, 19 Jul 2026 20:33:35 UTC)
- feat(golang): make style a runnable pass, delegated from review.

## v0.18.0 (Sun, 19 Jul 2026 16:09:33 UTC)
- feat(skill-smith): drop Grok support, adopt Claude-native frontmatter.
- docs: retarget skill catalog at Claude Code only.
- feat(golang): adopt argument-hint, $ARGUMENTS, and diff injection.
- feat(srd): adopt argument-hint and $ARGUMENTS.
- feat(craft): adopt argument-hint, $ARGUMENTS, and cm diff injection.
- Bump version to v0.18.0.
- docs(doc): refine interface-method godoc handling.
- docs(skill-smith): add argument-hint default-marker convention.

## v0.18.0 (Sun, 19 Jul 2026 15:56:06 UTC)
- feat(skill-smith): drop Grok support, adopt Claude-native frontmatter.
- docs: retarget skill catalog at Claude Code only.
- feat(golang): adopt argument-hint, $ARGUMENTS, and diff injection.
- feat(srd): adopt argument-hint and $ARGUMENTS.
- feat(craft): adopt argument-hint, $ARGUMENTS, and cm diff injection.

## v0.17.0 (Sun, 19 Jul 2026 15:15:03 UTC)
- feat(cm): default to mini verbosity.
- docs(doc-smith): record glossary-scope lesson.
- docs(grill-me): add lesson on plain-prose grilling.
- docs(review): add empty Given section rule.
- docs(style): forbid empty Given section marker.
- feat(srd): let create defer In Scope and track TODOs.
- feat(srd): maintain draft scaffolds in edit.
- docs(srd): record edit skill lessons.
- feat(srd): recognize draft scaffolds in review.
- feat(golang): add doc skill.

## v0.16.0 (Thu, 16 Jul 2026 17:20:42 UTC)
- feat(craft): add doc-smith skill.
- docs(skill-smith): require US English in authored content.
- refactor(doc-smith): rename proofread mode to proof.

## v0.15.0 (Wed, 15 Jul 2026 19:06:31 UTC)
- docs: tighten rule and reference terseness across skills.
- docs(review): rename depth=exhaustive to depth=full.

## v0.14.0 (Wed, 15 Jul 2026 16:45:11 UTC)
- feat(srd): add doc-gap skill and documentation-corpus grounding.
- docs(doc-gap): add README for the doc-gap skill.
- refactor(srd): rename doc-gap skill to resolve-doc-gaps.
- feat(srd): add report-doc-gap producer skill.
- feat(srd): define report-doc-gap buffer store.
- feat(srd): capture doc gaps light on discovery.
- feat(srd): drain the gap buffer on resume and checkpoints.
- feat(srd): grill gaps at a user-chosen depth.
- feat(srd): allow opting out of the gap grill.
- feat(srd): file gaps only after confirmation.
- feat(srd): draw the doc-gap vs SRD-gap boundary.
- fix(srd): correct broken anchor links in report-doc-gap.
- refactor(srd): delegate gap reporting to report-doc-gap.
- feat(srd): let edit and review find and report doc gaps.
- docs(srd): note report-time knowledge in resolve-doc-gaps.
- docs(review): clarify fix reporting rules, discourage diffs.
- docs(srd): pin skills to the srd-doc MCP server.

## v0.13.0 (Sun, 12 Jul 2026 21:09:16 UTC)
- docs(cm): rename minimal verbosity argument to mini.
- docs(readme-smith): trim duplicated rules and refresh badges.
- docs(grill-me): tighten prose and reformat lists.
- feat(grill-me): broaden description triggers and sharpen evals.
- docs(readme-smith): rename "strict-portable" to "portable".
- feat(skill-smith): enforce plain lists and cut standards duplication.
- feat(skill-smith): add eval-harness (Measure mode).
- feat(skill-smith): surface Measure mode, add eval templates.
- feat(plan-smith): add plan authoring and tracking skill.
- feat(lint): warn on oversized SKILL.md bodies.
- feat(craft): make plan-smith the canonical plan writer.
- chore(skill-smith): drop tracked lessons log.
- docs(craft): generalize spaced-list rule, tighten cm skill.
- style(cm): space prose-step lists in SKILL.md.
- docs(skill-smith): fix post-Measure doc drift.
- fix(cm): widen description for oblique triggers.
- docs(readme-smith): dedup verify checks, fix reference drift.
- docs(plan-smith): align summary-table columns.
- docs(create): shrink always-loaded token surface.
- docs(srd): cut workflow leaks from edit/review descriptions.
- docs(system-check): cut duplicated guardrails recap.
- docs(style): trim description leak, fix rule-edit pointer.
- docs(review): honest rules.md load label, drop bold lead-ins.
- docs(reshape): drop bold list lead-ins, link change catalog.
- docs(cover): drop bold list lead-ins, trim description.

## v0.12.0 (Fri, 10 Jul 2026 18:48:49 UTC)
- docs: shorten the shared Self-learning block in every skill.
- docs: trim per-skill duplication from SKILL.md files.
- feat(golang): add env-through-ring and three more style rules.
- docs(review): record lesson to keep segmented multi-line strings.
- docs(srd): drop redundant SRD validation checklist.
- feat(srd): verify srd-standard.md against its source.
- docs: slim skills' always-loaded surface and add token tooling.
- feat(srd): drive srd-standard sync from a skill.
- feat(golang): add fail-fast ordering style rule.
- chore: git-ignore the /tmp scratch directory.
- docs(srd): keep Confluence out of user-facing skills.
- feat(srd): track review findings as numbered tasks.
- feat(cm): add micro, minimal, and apply arguments.

## v0.11.0 (Thu, 09 Jul 2026 14:04:42 UTC)
- docs(srd): prefer three- or four-letter requirement codes.
- docs(srd): update SRD template with formatting changes and RFC link addition.
- feat(srd): cache glossary digest, regenerate only on change.
- docs(srd): escape pipe in template status cell.
- docs(readme-smith): add lessons store.
- refactor(system-check): scope memory store under srd/.
- feat(lint): warn on Markdown lines over 80 columns.

## v0.10.0 (Thu, 09 Jul 2026 12:06:42 UTC)
- docs(golang): add rule to break over-width table rows positionally.
- feat(golang): plan and chunk broad review fix jobs.
- docs(golang): add godoc placement and grammar rules.
- feat(grill-me): bias toward small specs and explicit evaluation.
- feat: add skill self-learning and the enhance-skills skill.
- docs: wrap skill lessons to the house markdown style.

## v0.9.0 (Mon, 06 Jul 2026 16:37:50 UTC)
- feat(golang): add reshape skill for library API proposals.

## v0.8.0 (Mon, 06 Jul 2026 10:55:14 UTC)
- docs(golang): fix cover module fan-out claim and trim description.

## v0.7.0 (Sun, 05 Jul 2026 20:37:16 UTC)
- feat(golang): extend style and review rules with receiver names, switch spacing, and error assertion guidance.
- Add `SKILL-STANDARD.md` textbook on crafting durable, reliable, and maintainable agent skills.
- feat(skill-smith): add eval-first and lint gates.
- feat(golang): add test-helper and topic-grouping style rules.
- docs(golang): make review skill description and terse rule mode-wide.
- feat(skill-smith): audit reference content and eager preloading.
- refactor(golang): restructure review rules around principles.

## v0.6.0 (Sun, 05 Jul 2026 13:16:16 UTC)
- feat(golang): expand the Go style and review rule set.

## v0.5.0 (Sun, 05 Jul 2026 11:06:20 UTC)
- feat(golang): add output-ownership rule to Go style.
- fix(readme-smith): require relpath prefix in gmdoceg markers.
- feat(golang): add /review learn mode and two style rules.

## v0.4.0 (Sat, 04 Jul 2026 20:25:11 UTC)
- feat(readme-smith): add README authoring and audit skill.

## v0.3.0 (Sat, 04 Jul 2026 14:22:16 UTC)
- feat(skill-smith): guard skill edits against the standard.
- feat(golang): expand the Go review and style rule set.
- fix(skills): resolve authoring-standard violations.

## v0.2.0 (Sat, 04 Jul 2026 13:01:00 UTC)
- build(dev): move maintainer scripts to dev/ and drop jq.
- build(marketplace): validate plugin manifests and add entry descriptions.

## v0.1.2 (Sat, 04 Jul 2026 12:34:56 UTC)
- skills: add rules on asserting distinctive output.
- build(version): derive plugin manifests from VER.
- docs(cm): scale commit-body detail to reader impact.

## v0.1.1 (Fri, 03 Jul 2026 22:08:21 UTC)
- docs(style): tighten and re-wrap Go style rules.

## v0.1.0 (Fri, 03 Jul 2026 21:51:18 UTC)
- Initial commit.

