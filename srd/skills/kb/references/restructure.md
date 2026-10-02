# Restructuring the knowledge base

Splitting a page, moving a section, renaming a subject — and repairing every
reference the move breaks. Read when a write would restructure rather than
append; an ordinary append never needs it.

`restructure` reorganizes the KB. Because a document id **is** its path,
every move breaks references — so this is a deliberate operation with repair
built in, never a bare file move.

1. Show the proposed moves — sections between pages, pages renamed, merged, or
   created — and get confirmation before touching anything.
2. Apply them. A `##` section moves **with everything bound to it**: its
   attestation line, its rows in the source page's `## Provenance` table, and
   any of its entries under `## Open questions`. A section that arrives
   stripped of its attestation line is silently an unsourced claim.

   Moving out of `_inbox.md` carries the section's inbox `## Provenance` row
   like any other move. What it cannot carry is a question that lived in the
   index alone, with no wording on the page: write that wording on arrival,
   from the `_open-questions.md` row, rather than leaving the new page short of
   what every other page has. A promoted fact that loses its provenance row is
   an unsourced claim by a slower route.
3. Repair every inbound reference in the same pass. Five kinds, all greppable
   in the `kb` folder except the gap-store ones:
   - Page links between KB pages.
   - Anchors. Moving a section changes `page.md#heading` targets. Moving one
     into a page that already has a heading of that name changes it again — the
     corpus disambiguates repeated heading anchors, so the arriving section may
     not get the anchor its name suggests. Re-derive anchors after the move, do
     not assume them.
   - `_open-questions.md` rows, whose `Lives in` column points at the page each
     question came from.
   - `doc_id` values in the gap store, reached through the same server
     (`list_gaps`); scan it for the old ids. Repairing one is a write, and this
     skill holds only read access to that store, and no skill can edit a gap
     past `draft`: report each stale `doc_id` with its gap id and the value it
     should take, for the user to fix. A restructure is not blocked by it — the
     move proceeds and the list goes in the report.
   - `kb_entry.ref` values on gaps parked as `kb` (`list_gaps` with `status: kb`),
     which point at a KB page and anchor. Report each
     stale one the same way as a stale `doc_id`.
4. Report what moved and what was repaired, counted.

State plainly that references from SRDs are not repaired: this skill writes
nothing outside the `kb` folder. Grep the `initiatives` folder for the old ids
and list each SRD that cites one, so the user can fix it.

Prefer adding a sibling page over restructuring. Restructuring is the escape
hatch, not the growth mechanism.
