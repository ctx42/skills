# Draft scaffolds

The two working scaffolds of a draft SRD, what each suppresses, and the two
procedures that touch them. Read when the SRD holds either scaffold, on "Add X
to TODO", or on the user's signal to fill the in-scope list; no other run needs
it.

## The scaffolds

Both live in a draft SRD (House additions in the authoring guide). `edit`
maintains them and resolves them only on the user's signal.

- In-scope `--- TODO ---` marker: while the in-scope list (the standard's
  list of what the SRD delivers, under whatever heading it sets) holds only
  this marker, it is knowingly pending — suppress every complaint under the
  standard's rule that each in-scope item be covered (issue summary,
  re-validation, consistency pass) and do not fabricate in-scope items.
- `## TODO` section: a numbered list of open issues the human must return to,
  kept as the document's last section.

## Add to TODO (any time)

On "Add X to TODO" (or similar), append X as the next numbered item of
`## TODO`, creating the section last if absent. The instruction is the
confirmation: skip the loop, renumber nothing else, report only the line added.

## Generate the in-scope list (on the user's signal)

Only when the marker is present and the user signals the requirements are
complete (or asks to fill the in-scope list). Take the template's instruction
comment above the marker along when the marker goes: that comment is scaffold,
and the read-only rule protects the author's comments, not the template's
directions to them. Run the in-scope derivation procedure in
`srd-procedures.md`, walking its candidates — none of them yet carrying an id —
through the loop; that file carries when ids are assigned, if the standard
gives scope items any, and the re-check that follows. Never trigger this on
your own.
