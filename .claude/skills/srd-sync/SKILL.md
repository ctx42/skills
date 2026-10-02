---
name: srd-sync
description: >
  Regenerates the SRD standard reference (srd-standard.md) from its Confluence
  source and reports local divergences. Use when asked to sync, regenerate, or
  update the SRD standard from Confluence, or after the source page changed.
  Maintainer-only; needs the private vr checkout.
---

# srd-sync

## Usage

```
/srd-sync   regenerate srd-standard.md from Confluence, report divergences (default)
```

`cfsync pull` the mirror first so the source is current, then invoke: review
the reported diffs and push any LOCAL-ONLY / TEXT DIFFERS units to Confluence
before confirming the write. Project-local (`.claude/skills/`), shipped in no
plugin — it depends on the `vr` checkout plugin users do not have.

Regenerate `srd/skills/create/references/srd-standard.md` from the Confluence
source. The copy is a **generated artifact**: source rule text trimmed for
agent use and wrapped in a hand-maintained frame. This skill is the only thing
that writes it. Maintainer task: it needs the cfsync mirror in the private
`vr` checkout.

## Files

| Role            | Path                                                                                                            | Load    |
|-----------------|-----------------------------------------------------------------------------------------------------------------|---------|
| Source (mirror) | `$SRD_STANDARD_SRC`, else `~/ws/vr/docs/confluence/infraport/guidelines_for_software_requirements_documents.md` | (eager) |
| Generated copy  | `srd/skills/create/references/srd-standard.md`                                                                  | (eager) |
| Header frame    | `dev/srd-standard.header.md`                                                                                    | (eager) |
| Footer frame    | `dev/srd-standard.footer.md`                                                                                    | (eager) |

The copy's provenance banner (below) is the sole record of the source version
it was generated from; read it with
`grep -o 'page_version [0-9]*' srd/skills/create/references/srd-standard.md`.

## Assembly

The assembled file is exactly:

```
srd-standard.md = header + <transformed source body> + footer
```

one blank line between the parts, with one edit to the header on the way in:

- Emit the header's H1 (`# SRD Standard`), then the generated provenance
  banner, then the header from its first prose line on. Drop the header's
  hand-maintained-frame note comment: the banner replaces it, and it never
  appears in the artifact.
- The banner MUST carry the source `page_version` (from the frontmatter) so the
  `dev/check-srd-standard.sh` tripwire can read it back:

  ```
  <!-- GENERATED FILE — do not edit by hand; page_version NN. Assembled by the
       srd-sync skill from dev/srd-standard.header.md, the upstream
       "Guidelines for Software Requirements Documents" source, and
       dev/srd-standard.footer.md. Edit the frame files or the upstream source,
       then re-run srd-sync. See CONTRIBUTING.md "Syncing the SRD standard". -->
  ```

  Emit it with a 5-space continuation indent, and keep those line breaks
  exactly — the specimen above is wrapped the way the artifact is, not the way
  this file is. Re-wrapping it to sit prettier here puts a two-line hunk in
  front of the maintainer on every single sync, on a banner whose only real
  change is the version number.

## Transform (source → body)

Produce the body in this order: `# Glossary` (kept terms), then
`# Requirements`. The RFC keyword notice is hand-maintained frame in the
header, not generated here.

Copy every kept requirement and glossary definition verbatim. Do not reword,
tighten, fix, or re-wrap rule text — free rewording is the one failure this
skill must not commit; if source wording seems wrong, fix it in Confluence, not
here. When the words are unchanged, preserve the copy's existing line wrapping:
never churn line breaks for zero content change (the repo hard-wraps by hand).

Unknown-section guard: list every top-level `# ` heading in the source. Each
must be in the keep set (Glossary, Requirements) or the drop set (Introduction,
Scope, Quality Bar — dropped whole; the footer supplies Quality Bar, and the
Scope section's `SC-*` / `OSC-*` items go with it). Any other heading → HARD
STOP: report `NEW SECTION: <name>` and do not write; the maintainer must extend
this transform first.

Drop these common-knowledge glossary terms: Example Annotation, Design Tool,
Initiative, Ticketing System, Markdown, Status, User Interface (UI). Keep every
other term.

Strip these, keeping the surrounding text: the `---` frontmatter block; the
metadata table (`|` rows); the TOC block (a fenced ```` ```adf ```` block whose
body is `type: toc` plus a `localId`); the intro note ("This page is itself a
valid SRD…"); cfsync `N>` indent markers and their continuation indentation in
glossary definitions; and the example expands — `> [!EXPAND] Example`
blockquotes carrying the Don't/Do pairs, stripped entire, since a real SRD
carries no Example/Don't/Do annotation. (Earlier exports emitted `[[TOC]]` and
`[[*expand:…]]`/`[[*orderedList:…]]` placeholders; neither appears from
page_version 16 on. Strip whichever form the source in hand actually uses.)
In REQ-7, keep only through "It MUST be the rule and nothing more." and drop
the source's trailing "This page is the one and only exception…" aside (it is
specific to the source page). Collapse any doubled blank line the strips leave.

Requirements keep their `**ID:**` prefixes; every group outside Scope stays.

Do not make the vr-internal-reference rewrites (GLO-3, STR-10, STA-3, STA-4) by
hand: copy those units verbatim like any other; `dev/srd-subst.sh` bakes the
swaps in at step 5.

## Steps

1. Resolve the source path. If the file is absent, report that the vr checkout
   is missing and stop — do not write anything.
2. Read the source, the current copy, and both frame files.
3. Frozen-node check. If the source `page_version` is newer than the copy's
   provenance version, the frozen nodes (the Quality Bar list and the Bad→Good
   example expands) may have changed without showing in the export. Run the
   diff below. Only the expand diff can stop the sync, and only when it finds
   something: an expand the guide does not account for, or one that has gone.
   The Quality Bar is never a stop — it lives in the footer, which the export
   does not carry, so no run can tell whether it was re-checked. Say in one
   line that it wants a human look at this version and carry on. Match expands
   by the rule they follow,
   not by id — the export stopped carrying localIds, so the rule each one sits
   under is the only stable key. A clean check is reported in one line and the
   sync continues — a version bump alone is a prompt to look, not a hard stop,
   or no sync could ever complete.
   - Diff the source's example expands against the `<!-- expand: -->`
     anchors in `srd/skills/create/references/authoring-guide.md` plus the
     list in `dev/srd-untranscribed-examples.md`, keyed by the rule each
     expand follows on both sides. Both files are keyed that way as of
     page_version 19; an entry still carrying only a localId is stale and
     matches nothing, which is how GLO-4 stayed invisible across three
     version bumps. Report each new one with the rule it follows (read it in
     Confluence, then transcribe it into the guide or add it to the list) and
     each one that has gone (retire its guide section or list entry).
   - An entry in the list naming a file that holds the transcribed text —
     today `dev/srd-glo4-example-pending.md` — is text already written and
     parked because the shipped standard did not yet define its rule. When the
     candidate body from step 4 defines that rule, paste the held section into
     the guide where the pending file says, delete the pending file, drop its
     list entry, and say all three happened. A sync that lifts the standard
     past the rule and leaves the text parked is the version bump that silently
     re-hides it.
   - When the expand diff found something, stop: tell the maintainer to open
     the page, review the expands and the Quality Bar list, and update
     `dev/srd-standard.footer.md` and the guide before continuing. Found
     nothing: report the clean check and the Quality Bar reminder in one line
     and go on.
   - Re-read the footer after any edit, then continue.
4. Transform the source into the body per the rules above.
5. Apply substitutions to the body, before assembling and before wrapping:
   `dev/srd-subst.sh <body.tmp >body.final` (reads stdin, prints the result).
   Order matters: the copy holds post-substitution words, so substituting
   before the frame and the wrap is what reproduces it. Wrapping first can also
   split a pattern across lines and produce a spurious `matched 0 times` —
   whether it does depends on where the wrap falls, so a phrase that survives
   at one width fails at another. Either way, check the order before touching
   the script's rules: that failure is not the upstream-phrase-changed case.
   A genuine assertion failure means an upstream phrase changed — update the
   script's rule, never resolve it by accepting the source wording. The script
   prints one `subst '<phrase>' xN` line per rule: a phrase cited by two rules
   reports `xN` and is rewritten in every place, which is correct — how many
   rules cite a given phrase changes between page versions, so the count is
   information, not something to assert in advance. It refuses outright when a
   phrase occurs only inside a longer one, since these are substring matches
   and "the Technology Group" sits inside "the Technology Group Lead".
6. Assemble the final candidate: `header + body.final + footer`, one blank line
   between, with the banner edit from Assembly, then wrap new and changed prose
   to 80 columns. Unchanged units keep the wrapping they already have — reflowing
   them turns a three-line diff into a whole-file one and buries the real change.
7. `diff` the final candidate against the current copy. The hunks are the real
   changes since the last sync. Verify only the changed units
   character-for-character against the source minus the trims and the step-5
   substitutions (unchanged units were verified at the previous sync). Report
   the hunks in these buckets:
   - LOCAL-ONLY (in the copy, not the candidate): local debt — push it
     upstream to Confluence, then re-sync. Print its full text so it is not
     lost.
   - SOURCE-ONLY (in the candidate, not the copy): will be added on write.
   - TEXT DIFFERS: show both sides. Reconcile in Confluence, or accept the
     source wording by writing.
   - FRAME (inside the header or footer part): a frame-file edit reaching the
     copy; needs no confirmation.
   Also run these consistency checks on the candidate:
   - Notice check: extract the source's first blockquote (the RFC keyword
     notice, `[!INFO]` line dropped) and compare it to the notice in the
     header. The only permitted difference is `in this document` → `in an
     SRD`. Any other difference → report `NOTICE DIFFERS` with both texts and
     hard-stop until the maintainer updates the header (or Confluence).
   - Contents check: list the `## ` group headings under `# Requirements` in
     the final candidate and confirm each appears in the header's Contents
     requirement-group line, and vice versa. Mismatch → tell the maintainer to
     update the header's Contents, then re-assemble.
8. If any LOCAL-ONLY or TEXT DIFFERS units exist, surface them and get
   explicit confirmation before writing — a write adopts the source and drops
   local-only text. When the diff is only the provenance `page_version` line
   and FRAME hunks, proceed — unless a consistency check above failed. A stale
   Contents line or a differing notice lives inside the header, so it arrives
   as a FRAME hunk and would otherwise ride straight through on the
   FRAME-only path, shipping a standard whose Contents names a group that no
   longer exists. A failed check blocks the write regardless of which bucket
   its hunk landed in.
9. Write the final candidate to the copy (move the temp file into place).
10. Run `./dev/lint-skills.sh` (must stay at 0 errors), then check that the
    regenerated standard can still back the srd:review fixture eval. The
    fixture is `srd/skills/review/assets/flawed-srd.md` and its finding set
    must not shrink. Check it this way rather than by re-reviewing the fixture,
    which grades the reviewer and not this sync:
    - Take the ids `srd/skills/review/evals/expectations.json` mentions, and
      keep only those the **outgoing** standard defines as rules (`**ID:**`).
      Calibrating against the old copy is what makes this checkable: the
      expectations also name the fixture's own requirement ids — `GR-3`,
      `SC-2`, `OSC-1` — which are the flawed SRD's content, never rules, and a
      bare id regex reports all of them as missing on a perfectly good sync.
    - Confirm each surviving id is still defined in the written standard. One
      the new version dropped or renumbered takes its finding with it,
      silently: the fixture still holds the defect, the reviewer has no rule
      left to cite, and the eval fails on a skill nobody touched.
    - Report any id that vanished, with the expectation that cites it, so the
      fixture and its expectations are updated in the same change as the sync.

## Output

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. Print the diff buckets (full text where
noted), then a one-line pointer to the written file and the new version; never
re-dump the generated file.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/srd-sync.md`, the
sibling winning a conflict — a read-only install writes the second, and what it
learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule to the sibling when this directory
is writable, else to the fallback, creating it, and report where.