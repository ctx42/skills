---
type: agent
---
Answer each id or path with its document below, verbatim.

For `1000000110` or `docs/engines/hot-fire-campaigns.md`:

````markdown
# Hot-Fire Campaigns

## Campaign plan

An Anvil engine is cleared to fly after three hot-fires of at least 30
seconds each; a stage is cleared after one full-duration stage hot-fire.

## Cold archive

Hot-fire recordings older than 30 days move to the cold archive. Archived
recordings stay downloadable but load more slowly.
````

For `kb/scrub-refunds.md`:

````markdown
---
title: Scrub refunds
attested: 2026-09-20
srd_ref: scrub-refunds, payload-booking
last_verified: 2026-09-30
---

# Scrub refunds

## Customer scrub refund

> Not in the platform docs. Attested scrub-refunds interview 2026-09-20.

When the customer causes a scrub, Starforge pays back 80% of the slot fee;
the other 20% covers the pad crew's costs for the day.

## Refund claim deadline

> Not in the platform docs. Attested scrub-refunds interview 2026-09-20;
> payload-booking interview 2026-09-29.

A customer must claim a scrub refund within 60 days of the scrub; later
claims are refused.

## Provenance

Where each section of this page comes from.

| Section               | Source                                    |
|-----------------------|-------------------------------------------|
| Customer scrub refund | scrub-refunds interview                   |
| Refund claim deadline | scrub-refunds, payload-booking interviews |
````

For `kb/_inbox.md`:

````markdown
---
title: Knowledge base inbox
last_verified: 2026-09-01
---

# Knowledge base inbox
````

For `docs/srd-standard.md`:

````markdown
{{file:fixtures/srd-standard.md}}
````

For any other id answer {"error":"document not found"}.
