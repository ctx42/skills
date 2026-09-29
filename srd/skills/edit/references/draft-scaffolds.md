# Draft scaffolds — the two procedures

What to do when the user asks for a TODO line, or signals that In Scope can be
filled. Read on either trigger; no run needs this file before then. The
scaffolds themselves, and the rule that suppresses SCO-2 while the In Scope
marker stands, are in `SKILL.md`.

## Add to TODO (any time)

On "Add X to TODO" (or similar), append X as the next numbered item of
`## TODO`, creating the section last if absent. The instruction is the
confirmation: skip the loop, renumber nothing else, report only the line added.

## Generate In Scope (on the user's signal)

Only when the marker is present and the user signals the requirements are
complete (or asks to fill In Scope): run the In Scope derivation procedure in
[../../create/references/srd-procedures.md](../../create/references/srd-procedures.md),
walking its unnumbered candidates through the loop; that file carries when the
`SC-n` numbers are assigned and the re-check that follows. Never trigger this
on your own.
