# srd-sync

Maintainer skill: regenerates `srd/skills/create/references/srd-standard.md`
from its Confluence source and reports local divergences.

## Usage

```
/srd-sync   regenerate srd-standard.md from Confluence, report divergences (default)
```

`cfsync pull` the mirror first so the source is current. Then invoke; review the
reported diffs and push any LOCAL-ONLY / TEXT DIFFERS units to Confluence before
confirming the write.

The copy is assembled from the cfsync mirror in the private `vr` checkout plus
the `dev/srd-standard.header.md` / `dev/srd-standard.footer.md` frame, and
self-verified to mirror the source verbatim. See [SKILL.md](SKILL.md) for the
transform rules, the diff buckets, and the consistency checks.
`dev/srd-subst.sh` owns the deterministic vr-internal-reference swaps, so an
LLM never edits rule text to make one; `dev/srd-untranscribed-examples.md`
lists the upstream example blocks not yet transcribed into the authoring guide.

Project-local (`.claude/skills/`), not shipped in any plugin — it depends on
the vr checkout that plugin users do not have. The passive drift tripwire that
lint runs is `dev/check-srd-standard.sh` (compares one `page_version` number);
this skill does the actual regeneration.

## When to use

Sync, regenerate, or update the SRD standard after the Confluence source
changed (`dev/check-srd-standard.sh` warns when it has).

## Evaluations

### 1. Normal sync after a source edit

**Request:** "Sync the SRD standard from Confluence."
(Source advanced a version; one rule reworded upstream.)

- Reads the source, current copy, and header/footer before proposing anything.
- Reports the reworded rule under TEXT DIFFERS with both sides shown.
- Confirms before writing, then writes `header + transformed body + footer` with
  the provenance banner carrying the new source `page_version`.
- Generated rule text is the source text verbatim — no paraphrase or re-wrap
  that changed words.

### 2. Verbatim fidelity (no rewording)

**Request:** "Regenerate the standard." (A source requirement is wordy /
awkward, and not in the substitution set.)

- Copies the requirement unchanged; does not tighten, fix, or summarize it.
- Verifies the changed units are the source text minus the mechanical trims
  and substitutions, character for character, before the write.

### 3. Deterministic substitution via the script

**Request:** "Sync the SRD standard." (GLO-3 in the source links the
vr-internal glossary page.)

- The skill copies GLO-3 verbatim, then applies substitutions by piping the
  candidate through `dev/srd-subst.sh` — it does not hand-edit the rule.
- The final copy carries the script's replacement; GLO-3 is not reported as a
  diff (the script baked the swap in, matching the current copy).
- If the script's match assertion fails, the skill updates the script's rule
  rather than accepting the source wording.
- The RFC notice is not touched — it lives in the header frame.

### 4. Local-only rule not upstream

**Request:** "Update srd-standard from the source." (The copy has a rule absent
from Confluence.)

- Reports it as LOCAL-ONLY with its full text and says to push it upstream.
- Does not silently drop it; warns that writing will remove it before
  proceeding.

### 5. Frozen nodes — new example block upstream

**Request:** "Sync the SRD standard." (Source `page_version` bumped; the export
carries a `[[*expand:` localId that is neither an `<!-- expand: -->` anchor in
`authoring-guide.md` nor listed in `dev/srd-untranscribed-examples.md`.)

- Stops before assembly; reports the new id and the rule it follows.
- Tells the maintainer to review the Quality Bar list and the expands, and to
  transcribe the block into the guide or add its id to
  `dev/srd-untranscribed-examples.md`.
- Re-reads the footer before continuing; writes nothing until then.

### 6. New top-level section upstream

**Request:** "Regenerate the standard." (Source gained a `# Tooling` heading.)

- Hard-stops with `NEW SECTION: Tooling`; writes nothing.
- Does not guess whether to keep or drop it; says the transform must be
  extended first.

### 7. Frame edit and header consistency checks

**Request:** "Sync the SRD standard." (Since the last sync the header frame's
intro paragraph was edited and its Contents line still names a requirement
group the source no longer has.)

- Reports the intro hunk as FRAME and asks no confirmation for it.
- The Contents check fails: names the stale group and tells the maintainer to
  update the header's Contents, then re-assembles.
- The Notice check passes silently when the only difference is `in this
  document` → `in an SRD`; any other difference is `NOTICE DIFFERS` and a
  hard-stop.

### 8. Source unavailable

**Request:** "Sync the SRD standard." (No vr checkout on this machine.)

- Reports the source is missing and names the expected path.
- Writes nothing — no copy, no provenance change.

### 9. Terse output

**Request:** "Sync the SRD standard." (Clean — only a version bump, no unit
diffs.)

- No preamble or step narration; no closing summary re-dumping the file.
- States the frozen-node reminder and a one-line "wrote … (page_version N)"
  pointer, once.
