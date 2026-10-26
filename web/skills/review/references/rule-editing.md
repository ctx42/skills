# review rule editing

Read when Rule-edit or Learn mode triggers. Both modes write to the
`web:style` rulebook: `../style/SKILL.md` for rules a tool cannot check,
`../style/references/biome.json` for rules Biome can.

## Writes must reach the repo

The paths resolve relative to the running plugin copy. Rules only stick if
that copy is the git clone (loaded via `claude --plugin-dir ./web`). From a
marketplace install (a copy under `~/.claude/plugins/cache/`) the edit lands
in a throwaway copy and is lost on the next update — warn the user and have
them re-run from the clone before writing.

## Where a rule goes

1. A Biome rule, with its options, enforces it — over the files the rule
   names or more (a rule worded for `.ts` modules that Biome checks in every
   file counts): it goes in `../style/references/biome.json`, at `error`, in
   its group; look the rule up in the installed Biome's
   `configuration_schema.json` rather than from memory. Nothing goes in the
   prose rulebook: config and prose line together is never right for a rule
   Biome checks in full.
2. Biome checks only part of what the rule asks (some cases, not others): the
   part Biome checks goes in the config, and the prose line keeps only what it
   cannot.
3. Otherwise: one line in `../style/SKILL.md`.

Say which of the three it is, and why, in the confirmation.

## Rule-edit mode

1. Read `../style/SKILL.md` and `../style/references/biome.json`.
2. Turn the input into rule entries shaped per How a rule entry should look,
   placed per Where a rule goes. If the scope is ambiguous, ask one question.
3. Detect duplicate or conflicting rules in both files; show them and the
   proposed change, then wait for confirmation before writing. Never silently
   overwrite a conflicting rule.
4. Check the write location (above), then write: `add` inserts the line or
   the config entry; `change` rewrites it in place; `remove` deletes it.
5. Show the before/after of the rule text or config entry.

## Learn mode

Turns the corrections the user gave on frontend code this session into
durable rules.

1. Gather, since the last /clear, the user's feedback on `.vue`/`.ts` code —
   corrections, "do X not Y", requested renames, accepted or rejected
   suggestions — and pair each with the before/after hunk that resolved it.
   The diff illustrates feedback; never mine a rule from code the user never
   commented on.
2. Keep only convention that applies beyond the one site; drop one-off
   instructions. When unsure, keep it as a candidate for the user to cut.
3. Distill each into a rule per How a rule entry should look, placed per
   Where a rule goes, and dedupe against both files.
4. Present candidates as a list, each with its provenance and its placement,
   flagging duplicates and conflicts; wait for the user to pick. When every
   candidate dedupes away, say in one line which existing rules already cover
   the session and stop.
5. Write the chosen rules via Rule-edit steps 4–5.

## How a rule entry should look

- One rule = one concept = one dense imperative line, in the Production or
  Test section (`*.test.ts` and `e2e/*.spec.ts` are Test), near related rules.
- State it generically: name the construct, not the site — no project
  identifiers, domain nouns, or file names.
- Cut every word the rule survives without; prefer no example, and use only
  generic Vue or TypeScript syntax when one is needed.
- A config entry carries no comment; its rule name says what it does.
