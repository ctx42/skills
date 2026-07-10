# review rule editing

Read when Rule-edit or Learn mode triggers. Both modes write rules.

> **Writes must reach the repo.** These modes edit `../style/SKILL.md` and
> `rules.md` in place, relative to the running plugin copy. Rules only stick if
> that copy is the git clone (loaded via `claude --plugin-dir ./golang`), so the
> change can be committed and shared. If this skill is running from a marketplace
> install (a copy under `~/.claude/plugins/cache/`), the edit lands in that
> throwaway copy and is lost on the next update — warn the user and have them
> re-run from the clone before writing.

## Rule-edit mode

Triggered when the input is a preference or asks to add/change/remove a rule.

1. Read `style`'s `SKILL.md`.
2. Turn the input into rule entries shaped per **How a rule entry should
   look** below. If the scope is ambiguous, ask one quick question.
3. Detect duplicate or conflicting rules; show them and the proposed change,
   then **wait** for confirmation before writing. Never silently overwrite a
   conflicting rule.
4. Write the rule to `style`; add a keyed `rules.md` entry only when the
   rule is non-obvious.
5. Show the before/after diff.

## Learn mode

Triggered when asked to learn from the session / your feedback (e.g. `/review
learn`). Turns the corrections you gave while editing Go this session into
durable rules. Same repo-copy caveat and write path as Rule-edit mode.

1. Warn if running from a marketplace copy (above) before writing.
2. Gather two signals since the last /clear: (a) feedback you gave on Go code —
   corrections, "do X not Y", requested renames/refactors, accepted or rejected
   suggestions; (b) the diff those turns produced (`git diff` and the session's
   edits). Pair each piece of feedback with the before/after hunk that resolved
   it. The diff corroborates and illustrates feedback — it is not an independent
   source; never mine a rule from code the user never commented on.
3. Keep only **generalizable convention** — a rule that applies beyond the one
   site. Drop task-specific instructions (one-off logic, a lone rename with no
   pattern). When unsure, keep it as a candidate and let the user cut it.
4. Distill each into a terse rule per **How a rule entry should look**, using the
   paired hunk as its before/after example; classify Production/Test/both;
   dedupe against existing `style` rules.
5. Present candidates as a list — each with its provenance (the session moment
   that prompted it), flagging duplicates/conflicts. **Wait** for the user to
   pick which to keep; never write unpicked or conflicting rules.
6. Write the chosen rules via Rule-edit mode's path (steps 4–5): `style` line +
   keyed `rules.md` entry when non-obvious; show the before/after diff.

## How a rule entry should look

- One rule = one concept = one dense imperative line.
- State it generically: name the construct, not the site — no project
  identifiers, domain nouns, or file names in the prose (`the receiver`, not
  `page`).
- Cut every word the rule survives without.
- Scope it Production (`*.go`), Test (`*_test.go`), or both; place it in that
  section, grouped near related rules.
- Examples may show only generic Go syntax (`ErrXxx`, `[Type]`,
  `//nolint:name`); never project-specific identifiers.
- Prefer no example when the prose stands alone; add one only to remove
  ambiguity.
- Deeper rationale or detection detail goes in `rules.md`, keyed to the rule
  and only when non-obvious; keep both files lean.
