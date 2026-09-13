# GLO-4 example — transcribed, held until the standard regenerates

The Bad→Good pair for GLO-4 ("link a Company Glossary term on first use"),
transcribed from the source at page_version 19. It is NOT in
`srd/skills/create/references/authoring-guide.md` yet: the shipped
`srd-standard.md` is generated from page_version 16 and defines only
GLO-1..3, and `srd:review` is told never to cite a rule the standard does
not carry — so a guide section citing GLO-4 and GLO-5 would licence exactly
the citation the reviewer forbids.

Paste it into the guide's "Defect classes" section, before the REQ-1
subsection, as part of the srd-sync run that lifts the standard to 19.

---

### Glossary link repeated on every use (GLO-4)
<!-- expand: (follows GLO-4) -->

Bad:
> The Acoustic Channel carries the signal. Each
> [Acoustic Channel](glossary/main_glossary.md#acoustic-channel) is sampled
> independently, and an [Acoustic Channel](glossary/main_glossary.md#acoustic-channel)
> with no sensor is skipped.

Good — linked on first use, bare after that:
> The [Acoustic Channel](glossary/main_glossary.md#acoustic-channel) carries the
> signal. Each Acoustic Channel is sampled independently, and an Acoustic
> Channel with no sensor is skipped.

GLO-4 is a SHOULD, and the link is owed once per document, not once per section
— a term linked again three pages later has not broken the rule so much as made
the SRD read like a reference card. GLO-5 governs where that one link points:
at the entry, never at the glossary document.

