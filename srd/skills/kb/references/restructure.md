# Restructuring the knowledge base

Splitting a page, moving a section, renaming a subject — and repairing every
reference the move breaks. Read when a write would restructure rather than
append; an ordinary append never needs it.

`restructure` reorganizes the KB. Because a KB page's identity **is** its path
(it carries no `id`), every move breaks references — so this is a deliberate
operation with repair built in, never a bare file move.

1. Show the proposed moves — sections between pages, pages renamed, merged, or
   created — and get confirmation before touching anything.
2. Apply them. A `##` section moves **with everything bound to it**: its
   attestation line, its rows in the source page's `## Provenance` table, and
   any `> Open: gap-NNNN.` warning line it carries — never expanded into the
   question's wording. A section that arrives stripped of its attestation line
   is silently an unsourced claim.

   Moving out of `_inbox.md` carries the section's inbox `## Provenance` row
   like any other move. A promoted fact that loses its provenance row is an
   unsourced claim by a slower route.
3. Repair every inbound reference in the same pass. Four kinds, all greppable
   in the `kb` folder except the gap-store ones:
   - Page links between KB pages.
   - Heading slugs. Moving a section changes `page.md#<slug>` targets. Moving
     one into a page that already has a heading of that name changes it again —
     a repeated heading's slug takes a `-1`, `-2` suffix, so the arriving
     section may not get the slug its name suggests. Re-derive slugs after the
     move, do not assume them.
   - `doc_id` values in the gap store, reached through the same server
     (`list_gaps`), open questions (`answer` set) included; scan it for the old
     identities. Repairing one is a write, and this skill holds only read
     access to that store: report each stale `doc_id` with its gap id and the
     value it should take, for the user to fix. A restructure is not blocked by
     it — the move proceeds and the list goes in the report.
   - `filled_by` refs (`<identity>#<slug>`) on filled and partly filled
     gaps, which point at a KB page and heading slug. Report each stale one the same
     way as a stale `doc_id`; `srd:backlog` re-fills it.
4. Report what moved and what was repaired, counted.

State plainly that references from SRDs are not repaired: this skill writes
nothing outside the `kb` folder. Grep the `initiatives` folder for the old
paths and list each SRD that cites one, so the user can fix it.

Prefer adding a sibling page over restructuring. Restructuring is the escape
hatch, not the growth mechanism.
