---
type: agent
---
Answer each id or path with its document below, verbatim.

For `1882030917` or `docs/operations/storage-housekeeping.md`:

````markdown
# Storage housekeeping

## Nightly jobs

The housekeeping job runs at 02:00 Instance time and compacts the time-series
store.

## Archive tier

Recordings older than 90 days move to the archive tier. Archived recordings
stay playable but load more slowly.
````

For `kb/gift-cards.md`:

````markdown
---
title: Gift cards
attested: 2026-09-20
srd_ref: gift-cards, checkout-v3
last_verified: 2026-09-30
---

# Gift cards

## Refund window

> Not in the platform docs. Attested gift-cards interview 2026-09-20.

A buyer may return an unused gift card for a full refund during the first 14
days after purchase. Later requests go to support, case by case.

## Gift card expiry

> Not in the platform docs. Attested gift-cards interview 2026-09-20;
> checkout-v3 interview 2026-09-29.

A gift card expires 24 months after purchase; its unspent balance is then
lost.

## Provenance

Where each section of this page comes from.

| Section          | Source                             |
|------------------|------------------------------------|
| Refund window    | gift-cards interview               |
| Gift card expiry | gift-cards, checkout-v3 interviews |
````

For `kb/_inbox.md`:

````markdown
---
title: Knowledge base inbox
last_verified: 2026-09-01
---

# Knowledge base inbox
````

For any other id answer {"error":"document not found"}.
