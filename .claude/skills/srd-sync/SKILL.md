---
name: srd-sync
description: >
  Regenerates the SRD standard reference (srd-standard.md) from its Confluence
  source and reports local divergences. Use when asked to sync, regenerate, or
  update the SRD standard from Confluence, or after the source page changed.
  Maintainer-only; needs the private vr checkout.
---

# srd-sync

Regenerate `srd/skills/create/references/srd-standard.md` from the Confluence
source. The copy is a **generated artifact**: source rule text trimmed for
agent use and wrapped in a hand-maintained frame. This skill is the only thing
that writes it. Maintainer task — it needs the cfsync mirror in the private
`vr` checkout; without it, stop.

## Files

| Role            | Path                                                                                                 | Load    |
|-----------------|------------------------------------------------------------------------------------------------------|---------|
| Source (mirror) | `$SRD_STANDARD_SRC`, else `~/ws/vr/docs/infraport/guidelines_for_software_requirements_documents.md` | (eager) |
| Generated copy  | `srd/skills/create/references/srd-standard.md`                                                       | (eager) |
| Header frame    | `dev/srd-standard.header.md`                                                                          | (eager) |
| Footer frame    | `dev/srd-standard.footer.md`                                                                          | (eager) |

The version the copy was generated from lives ONLY in the copy's provenance
banner (below) — there is no separate state file. Read it with
`grep -o 'page_version [0-9]*' srd/skills/create/references/srd-standard.md`.

## Assembly

The assembled file is exactly:

```
srd-standard.md = header + <transformed source body> + footer
```

one blank line between the parts, with one edit to the header on the way in:

- Emit the header's H1 (`# SRD Standard`), then the generated provenance
  banner, then the header from its first prose line on. **Drop the header's
  hand-maintained-frame note comment** — it never appears in the artifact; the
  banner replaces it.
- The banner MUST carry the source `page_version` (from the frontmatter) so the
  `dev/check-srd-standard.sh` tripwire can read it back:

  ```
  <!-- GENERATED FILE — do not edit by hand; page_version NN. Assembled by the
       srd-sync skill from dev/srd-standard.header.md, the Confluence page
       1949564932 ("Guidelines for Software Requirements Documents"), and
       dev/srd-standard.footer.md. Edit the frame files or the Confluence
       source, then re-run srd-sync. See CONTRIBUTING.md "Syncing the SRD
       standard". -->
  ```

## Transform (source → body)

Produce the body in this order: `# Glossary` (kept terms), then
`# Requirements`. The RFC keyword notice is hand-maintained frame in the
header — not generated here.

**Copy every kept requirement and glossary definition verbatim.** Do not
reword, tighten, fix, or re-wrap rule text — free rewording is the one failure
this skill must not commit; if source wording seems wrong, fix it in Confluence,
not here. When the words are unchanged, preserve the copy's existing line
wrapping — never churn line breaks for zero content change (the repo hard-wraps
by hand).

**Unknown-section guard.** List every top-level `# ` heading in the source.
Each must be in the keep set (**Glossary**, **Requirements**) or the drop set
(**Introduction**, **Scope**, **Quality Bar**). Any other heading → HARD STOP:
report `NEW SECTION: <name>` and do not write; the maintainer must extend this
transform first.

Drop these whole top-level sections: **Introduction**, **Scope**,
**Quality Bar** (the footer supplies Quality Bar).

Drop these common-knowledge glossary terms: **Example Annotation**,
**Design Tool**, **Initiative**, **Ticketing System**, **Markdown**,
**Status**, **User Interface (UI)**. Keep every other term.

Strip these, keeping the surrounding text: the `---` frontmatter block; the
metadata table (`|` rows); `[[TOC]]`; the intro note ("This page is itself a
valid SRD…"); cfsync `N>` indent markers and their continuation indentation in
glossary definitions; `[[*expand:…]]` and `[[*orderedList:…]]` placeholders.
In **REQ-7**, keep only through "It MUST be the rule and nothing more." and drop
the source's trailing "This page is the one and only exception…" aside (it is
specific to the source page). Collapse any doubled blank line the strips leave.

Requirements keep their `**ID:**` prefixes. The dropped Scope section's `SC-*`
/ `OSC-*` items go with it; every other requirement group stays.

The vr-internal-reference rewrites (GLO-3, STR-10, STA-3, STA-4) are NOT made
by hand here — `dev/srd-subst.sh` owns them and applies them at step 6. Copy
those units verbatim like any other; the script bakes the swaps in.

## Steps

1. Resolve the source path. If the file is absent, report that the vr checkout
   is missing and stop — do not write anything.
2. Read the source, the current copy, `dev/srd-standard.header.md`, and
   `dev/srd-standard.footer.md`.
3. **Frozen-node check (before assembly).** If the source `page_version` is
   newer than the copy's provenance version, the **frozen nodes** — the Quality
   Bar list and the Bad→Good example expands — may have changed without showing
   in the export. STOP and:
   - Tell the maintainer to open the page and review the Quality Bar list and
     the expands, then update `dev/srd-standard.footer.md` and
     `srd/skills/create/references/authoring-guide.md` NOW.
   - Diff the source's `[[*expand:` localIds against the ids annotated in
     `authoring-guide.md` (transcribed + untranscribed). A new id → read it in
     Confluence and transcribe or list it untranscribed. A missing id → retire
     its guide section or backlog entry.
   - Re-read the footer after any edit, then continue.
4. Transform the source into the body per the rules above — verbatim copy plus
   the drops, strips, and unknown-section guard.
5. Assemble the candidate to a temp file: `header + body + footer`, one blank
   line between, with the banner edit from Assembly.
6. Apply substitutions: `dev/srd-subst.sh <candidate.tmp >final.tmp` (reads
   stdin, prints the result). Its output is the final candidate. If it fails
   its match assertion, an upstream phrase changed — update the script's rule,
   never resolve it by accepting the source wording.
7. `diff` the final candidate against the current copy. The hunks are the real
   changes since the last sync. **Verify only the changed units**
   character-for-character against the source (unchanged units were verified at
   the previous sync). Report the hunks in three buckets:
   - **LOCAL-ONLY** (in the copy, not the candidate): local debt — push it
     upstream to Confluence, then re-sync. Print its full text so it is not
     lost.
   - **SOURCE-ONLY** (in the candidate, not the copy): will be added on write.
   - **TEXT DIFFERS**: show both sides. Reconcile in Confluence, or accept the
     source wording by writing.
   Also run these consistency checks on the candidate:
   - **Notice check.** Extract the source's first blockquote (the RFC keyword
     notice, `[!INFO]` line dropped) and compare it to the notice in the
     header. The only permitted difference is `in this document` → `in an SRD`.
     Any other difference → report `NOTICE DIFFERS` with both texts and
     hard-stop until the maintainer updates the header (or Confluence).
   - **Contents check.** List the `## ` group headings under `# Requirements` in
     the final candidate and confirm each appears in the header's Contents
     requirement-group line, and vice versa. Mismatch → tell the maintainer to
     update the header's Contents, then re-assemble.
8. If any LOCAL-ONLY or TEXT DIFFERS units exist, surface them and get explicit
   confirmation before writing — a write adopts the source and drops local-only
   text. When the only expected diff is the provenance `page_version` line
   (a version-only sync), proceed.
9. Write the final candidate to the copy (move the temp file into place).
10. Run `./dev/lint-skills.sh` (must stay at 0 errors) and re-check the
    srd:review fixture eval `srd/skills/review/assets/flawed-srd.md`: its
    finding set must not shrink against the regenerated standard.

## Output

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. Print the three diff buckets (full text where
noted), then a one-line pointer to the written file and the new version — never
re-dump the generated file.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/srd-sync.md` when this directory is
read-only. On a correction or self-caught mistake (e.g. a transform rule the
source outgrew, an accidental reword the self-verify missed), append a one-line
rule to whichever is writable (creating it) and report where.
