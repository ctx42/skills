## v0.26.0 (Thu, 01 Oct 2026 21:28:07 UTC)
- docs(srd): clarify rule id prefixes are not reserved.
- chore!: retire the skill-smith skill.
- fix(lint): report findings by repo-relative path.
- feat(skills)!: drop per-skill README.md for SKILL.md and evals.json.
- fix(lint): skip SKILL.md files under assets/.
- feat(srd): add the kb skill.
- feat(srd)!: replace resolve-doc-gaps with the backlog skill.
- feat(srd): add the doc-corpus and errata references.
- refactor(create): tighten the prompt and its references.
- refactor(report-doc-gap): retarget the consumer side and tighten the prompt.
- feat(srd)!: retire system-check's memory file for the knowledge base.
- refactor(skills): let the self-learning block stay silent with no lessons.
- docs: list report-doc-gap in the skill catalogs.
- fix(srd): keep the Company Glossary name in the standard copy.
- docs(srd): drop Markdown Export from the standard contents.
- feat(srd-sync): track untranscribed examples and flag frame-only hunks.
- refactor(edit): fold the lessons into the prompt and tighten it.
- refactor(review): fold the lesson into the prompt and tighten it.
- refactor(cm): restate the input contract and tighten the prompt.
- refactor(doc-smith): fold the lessons into the prompt and tighten it.
- refactor(readme-smith): fold the lessons into the prompt and tighten it.
- refactor(style): trim rules.md to what the one-line rule cannot carry.
- refactor(golang-review): fold the lesson into the prompt and tighten it.
- refactor(doc): tighten the prompt and fold Write into the walk.
- refactor(cover): tighten the prompt.
- refactor(reshape): tighten the prompt and its change catalog.
- feat(grill-me)!: migrate to the README-free layout.
- feat(grill-me): interrogate a topic, not only a build plan.
- fix(grill-me): ask one question per turn and keep turns short.
- feat(plan-smith)!: migrate to the README-free layout.
- fix(plan-smith): keep a written plan to the brief's scope.
- feat(enhance-skills)!: migrate to the README-free layout.
- fix(enhance-skills): stop harvesting what is not a lesson.
- feat(readme-smith)!: migrate to the README-free layout.
- fix(readme-smith): target the gomake example injector that exists.
- feat(cm)!: migrate to the README-free layout.
- feat(doc-smith)!: migrate to the README-free layout.
- feat(cover)!: migrate to the README-free layout.
- feat(doc)!: migrate to the README-free layout.
- feat(reshape)!: migrate to the README-free layout.
- feat(review)!: migrate to the README-free layout.
- feat(style)!: migrate to the README-free layout.
- feat(backlog)!: migrate to the README-free layout.
- feat(create)!: migrate to the README-free layout.
- feat(edit)!: migrate to the README-free layout.
- feat(kb)!: migrate to the README-free layout.
- feat(report-doc-gap)!: migrate to the README-free layout.
- feat(review)!: migrate to the README-free layout.
- feat(system-check)!: migrate to the README-free layout.
- feat(srd-sync)!: migrate to the README-free layout.
- build(lint): fail on a skill README now that none remain.
- fix(readme-smith): close the gaps six eval runs walked into.
- fix(readme-smith)!: ask before writing Go source.
- docs(readme-smith): stop framing an unpublished module as a failed run.
- fix(cm): amend the message without swallowing the index.
- fix(doc): stop the checklist inviting comments the code cannot support.
- fix(style): make the fan-out merge performable.
- fix(reshape): supply the definitions the ranking depends on.
- fix(review): scope reason-only to the review, not the fix.
- fix(report-doc-gap): resolve the channel before spending the finder's attention.
- fix(doc-smith): order create so the self-review can actually run.
- fix(srd): give the REST mirror an address so it can be found.
- fix(skills)!: stop reading the second argument as the first.
- fix(edit)!: honor STA-4 content freeze on an accepted SRD.
- fix(system-check): refresh the review instead of freezing it.
- fix(plan-smith): require evidence before marking an item done.
- fix(enhance-skills): retrofit the block's words, not its line breaks.
- fix(cover): read the Production rules the tests it writes must obey.
- fix(grill-me): a branch the user calls done is not thereby resolved.
- fix(create): an unchecked platform claim is unconfirmed, not accepted.
- fix(kb): report stale gap-store ids instead of claiming to repair them.
- fix(review): give every rule a severity and make errata idempotent.
- fix(srd-sync): substitute before assembling, and let a clean check continue.
- fix(backlog): establish an unknown from the user, not from the corpus.
- docs(style): state the test structure the rules already constrain.
- fix(cover): divide max_tests before dispatching a fan-out.
- fix(skills): read the lessons a read-only session wrote.
- fix(report-doc-gap): say what "the same fact" means before merging on it.
- fix(kb): make the attestation line writable without a filed gap.
- fix(review): number fresh findings in document order.
- fix(edit): tell pasted feedback from a targeted description.
- fix(system-check): keep the answers that are about the SRD.
- docs(doc-smith): define the unit revise walks and the paragraph em dashes count.
- fix(srd-subst): allow a phrase two rules both cite, refuse one inside a longer.
- feat(evals)!: split the rubric out of the scenario file.
- test(evals): cover four documented behaviours, and mark what cannot run.
- test(review): move the regression-gate instruction out of the setup.
- docs(contributing): record how to run the evals now that they can be blind.
- fix(doc): make the parent audit what a fan-out worker wrote.
- fix(skills): finish removing argument meta-prose from four skills.
- test(doc): repair three expectations the blind grading exposed.
- fix(cm): say which git invocation `apply` uses, and refuse it with an empty index.
- fix(enhance-skills): close the retrofit template's fence.
- build(eval): move the blind-runner prompt out of tmp/.
- fix(grill-me): handle a branch nobody in the room can resolve.
- fix(plan-smith): match the unverified-claim scenario to its own fixture.
- fix(cover): separate un-coverable from deferred, and reject unknown controls.
- fix(review): ground the learn scenario in what the rulebook actually says.
- fix(reshape): say what a zero-proposal run prints, and what counts as a site.
- fix(style): fold the merge by rule, and pin id, severity and granularity.
- fix(readme-smith): reconcile where a gap gets marked.
- fix(doc-smith): normalize spelling to the document, not to a house default.
- fix(review): stop claiming every rule has a severity row.
- fix(create): repair the draft's own defects instead of reporting them.
- fix(kb): say what a bare capture attests to, and what an inbox move carries.
- fix(edit): give the open-questions list and unlanded edits a home.
- fix(report-doc-gap): probe the channel with a read, never a write.
- fix(srd-sync): correct the source path, and parse the export that exists.
- fix(backlog): tell a missing gap endpoint from a broken store.
- fix(system-check): keep question ids meaningful across re-runs.
- test(cm,plan-smith): repair what independent grading exposed.
- fix(evals): repair what eight independent graders exposed.
- fix(lint): catch the two ways a reference file lies about itself.
- fix(srd): say what a corpus document id is, so a live source is not called stale.
- fix(cm,enhance-skills): repair what two blind runs walked into.
- fix(golang:doc): close six gaps a blind run had to guess its way through.
- fix(plan-smith): settle the five things a blind run had to decide for itself.
- fix(golang:review,style): one meaning for plan_first, broad, and a rule id.
- fix(golang:cover): repair six places a run had to read past the text.
- fix(grill-me): a duplicated clause, and three places the map ran out.
- fix(doc-smith): four instructions that pulled two ways, and a backwards sentence.
- fix(golang:reshape): a label nothing could wear, and a count that ranked nothing.
- fix(srd): give the gap store an address, and a store root a run can redirect.
- fix(golang:style,review,readme-smith): make a rule id derivable, and correct gomake.
- fix(srd:review): a citation form for reference findings, and room to say it.
- fix(cm,srd:review): the invented number no expectation was watching for.
- fix(enhance-skills): the empty run's report, and a scenario that graded a drop as a failure.
- fix(srd:kb,backlog): what a write owes the page, and what a closed row keeps.
- fix(srd-sync): find the expand that three version bumps hid.
- fix(srd:edit,grill-me,plan-smith): an open branch that survives the chat window.
- fix(srd,golang): one answer per question, across skills that gave three.
- fix(golang:cover,srd:system-check): make the order visible, and ground a setup in the corpus.
- fix(golang:style,readme-smith): the numbers nobody re-derived.
- test(evals): repair the expectations thirteen graders called uncheckable.
- docs(dev): park the GLO-4 example and re-key the untranscribed list.
- fix(golang:style): drop the last copy of plan_first's old meaning.
- test(system-check): unpick two bullets that asked for opposite things.
- fix(srd:create): the fourth wrong number, and a requirement nobody attested.
- fix(srd:edit): the ordering rule I wrote this afternoon was still ambiguous.
- docs(structure): note the extra `..` a references/ file needs.
- fix(golang:cover): five things a blind run could not decide from the text.
- fix(srd-sync): the banner specimen was wrapped for the wrong file.
- fix(golang:style): the id rule contradicted its own examples.
- docs(srd): regenerate the standard at page_version 19.
- feat(skills): honor AGENT_DATA_DIR for the lessons store.
- fix(srd:edit): the decision-log specimen was split across two files.
- feat(notify): add a hooks-only desktop attention plugin.
- refactor!: rename the golang plugin to go.
- feat(notify): register the plugin in the marketplace.
- feat(notify): dismiss the attention cards on click.
- perf(srd): probe delegate buffers instead of invoking them.
- perf(srd:edit): cut session start to a probe and a gate read.
- docs(skills): record lessons from earlier sessions.
- docs(srd): stop treating a simpler phrasing as a defect.
- fix(srd:edit): stop asking for the glossary path at session start.
- fix(srd:edit): stop before session start when the mode cannot run.
- fix(srd:edit): settle five things a run had to decide for itself.
- fix(srd:edit): point feedback at the review file's own reference.
- fix(srd): report the buffer probe, and let it run without an SRD.
- docs(skills): record three more lessons.
- fix(srd): settle rules two runs could read differently.
- docs(review): record two lessons.
- feat(style): take the line limit from .editorconfig.
- fix(style): keep fanned-out workers consistent and re-check splits.
- test(style): split the fan-out eval from the plan-first stop.
- docs(srd:edit): record a lesson on resolving comment blocks.
- fix(style): settle detection, severity and ids runs read differently.
- test(style): make the fan-out bullets checkable, add opposing fixes.
- chore(eval): have blind runners save every subagent brief.
- docs(eval): bound the eval loop with entry and exit rules.
- fix(srd:edit): name the newest decision-log block in the manifest.
- fix(srd:edit): log only reasons the user or the proposal gave.
- fix(srd:create): confirm facts by restatement, and skip a confirm turn.
- fix(srd): quote the STR-8 erratum as whole blocks.
- fix(srd:review): drain gaps before searching, and report the probe.
- fix(srd:kb): re-read each page and cut what nobody attested.
- fix(srd:system-check): credit srd:kb in the learn report.
- fix(srd:edit): quote decision-log reasons verbatim.
- test(srd:create): allow the kb-location ask at the first confirmed fact.
- fix(srd): name the template's keyword notice as the one correct form.
- fix(srd:system-check): drop questions a lookup answers, unasked.
- fix(srd:edit): never invent a figure, and settle the targeted walk.
- fix(srd): settle buffer keys, citation matching and provenance rows.
- fix(srd:create): settle glossary timing, definitions and empty sessions.
- fix(srd:review): settle categories, numbering, anchors and wrapping.
- fix(srd:system-check): probe in learn, and report one probe clause.
- test(srd): make the expectations checkable and the fixtures honest.
- test(style): shrink the fan-out fixtures to eight packages.
- chore(eval): snapshot files a skill writes across turns.
- fix(style): let a const-group headline cover self-describing members.
- fix(style): allow godoc on interface methods beyond the contract.
- fix(style,review): aggregate style-only fixes into one change.
- docs(review): record a lesson on go mod tidy and require blocks.
- docs(srd:edit): record a lesson on keeping glossary definitions general.
- feat(review): grade correctness findings by their reachable consequence.
- test(review): grade the rubric in the current-diff scenario.
- docs(review): record a lesson on naming a value a fix moves into Then.
- fix(srd): key the delegate buffers by the SRD's path, not an id.
- fix(srd:kb): give an inbox fact's open question a home for its wording.
- fix(srd): keep drafts and merges to what someone actually stated.
- fix(srd:backlog): report what srd:kb wrote as a count, not a list.

## v0.25.0 (Fri, 31 Jul 2026 14:33:17 UTC)
- feat(srd): classify STR-8 keyword notice as errata.
- feat(srd): add decision log to edit skill.
- docs(srd): clarify severity and category tagging in review files.
- feat(srd): require exact substitutions for errata.

## v0.24.0 (Fri, 24 Jul 2026 18:50:06 UTC)
- docs(srd): write SRD status values in uppercase.
- docs(doc-smith): record two review lessons.
- feat(srd): drop the 80-column line limit (MD-2).
- docs(srd): rename shared glossary to Company Glossary, drop MD rules.
- docs(srd): define errata class in authoring guide.
- feat(srd): group errata into a top block in review output.
- feat(srd): add review errata retrofit mode.
- feat(srd): list errata in review feedback output.
- feat(srd): add edit autofix mode for bulk errata.
- docs(srd): document errata and autofix modes.
- docs(srd): complete README coverage of errata and autofix.
- feat(srd): scope review check to named findings.
- feat(srd): retire MD namespace, add comma check ids.
- docs(skills): add Usage section to every skill readme.
- feat(srd): add line and #n start points to edit.

## v0.23.0 (Thu, 23 Jul 2026 11:10:45 UTC)
- feat(srd): mark generated review/questions files ignore-push.
- docs(srd-edit): record four edit lessons.
- docs(srd-standard): make the glossary conditional.

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

