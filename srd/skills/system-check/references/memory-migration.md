# memory.md migration

Legacy store locations from earlier versions of this skill. Consult only when
`$MEM` (resolved in `SKILL.md`) does not exist on this machine.

Check in order; on the first hit, offer to move the file to `$MEM` (confirm
the move with the user), then use it:

1. `$HOME/.agent-data/ctx42-skills/memory.md` — old bundle root.
2. `${XDG_DATA_HOME:-$HOME/.local/share}/srd-system-check/memory.md`.
3. `${XDG_DATA_HOME:-$HOME/.local/share}/ctx42-srd/memory.md`.
4. An old `memory.md` in this skill's directory — the oldest layout.

If none exists there is nothing to migrate — seed `$MEM` from
`memory.template.md` in this skill's directory.
