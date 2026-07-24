# srd-sync

Maintainer skill. Regenerates `srd/skills/create/references/srd-standard.md`
from its Confluence source (mirrored by cfsync into the private `vr` checkout)
plus the `dev/srd-standard.header.md` / `dev/srd-standard.footer.md` frame,
reports local edits that should be pushed upstream, and self-verifies that the
copy mirrors the source verbatim.

## Usage

```
/srd-sync   regenerate srd-standard.md from Confluence, report divergences (default)
```

`cfsync pull` the mirror first so the source is current. Then invoke; review the
reported diffs and push any LOCAL-ONLY / reworded units to Confluence before
confirming the write.

See [SKILL.md](SKILL.md) for the transform rules, the diff buckets, and the
consistency checks. `dev/srd-subst.sh` owns the deterministic
vr-internal-reference swaps, so an LLM never edits rule text to make one.

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
- Verifies the changed units are the source text minus the mechanical trims,
  character for character, before the write.

### 2b. Deterministic substitution via the script

**Request:** "Sync the SRD standard." (Source says "the Company Glossary" in
GLO-3.)

- The skill copies GLO-3 verbatim, then applies substitutions by piping the
  candidate through `dev/srd-subst.sh` — it does not hand-edit the rule.
- The final copy says "the shared glossary"; GLO-3 is not reported as a diff
  (the script baked the swap in, matching the current copy).
- The RFC notice is not touched — it lives in the header frame.

### 3. Local-only rule not upstream

**Request:** "Update srd-standard from the source." (The copy has a rule absent
from Confluence.)

- Reports it as LOCAL-ONLY with its full text and says to push it upstream.
- Does not silently drop it; warns that writing will remove it before
  proceeding.

### 4. Source unavailable

**Request:** "Sync the SRD standard." (No vr checkout on this machine.)

- Reports the source is missing and names the expected path.
- Writes nothing — no copy, no provenance change.

### 5. Terse output

**Request:** "Sync the SRD standard." (Clean — only a version bump, no unit
diffs.)

- No preamble or step narration; no closing summary re-dumping the file.
- States the frozen-node reminder and a one-line "wrote … (page_version N)"
  pointer, once.
