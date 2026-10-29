#!/usr/bin/env bash
set -euo pipefail
cat > project-config.md <<'EOF_PC'
---
mcp-server: srd
kb: kb
initiatives: initiatives
srd-standard: docs/srd-standard.md
glossary: docs/glossary
precedence:
  - kb
  - docs/concepts
  - docs/api-gateway
  - docs/operations
  - docs/glossary
---

# Project configuration (eval fixture)

EVAL TEST DATA ONLY. Copy this file to the root of a scenario's workspace so
the srd skills' gate finds a project; a scenario's `setup` overrides any key.
In an eval run, `srd/evals/mocks/srd/fixtures/srd-standard.md` stands in for the
`get_doc` result of `srd-standard` — see `dev/eval/blind-runner-prompt.md`.
EOF_PC
mkdir -p kb
cat > kb/_inbox.md <<'EOF_INBOX'
---
title: Knowledge base inbox
last_verified: 2026-09-29
---

# Knowledge base inbox

## Shipping quotes use a per-zone weight step

> Not in the platform docs. Attested parcel-quotes
> interview 2026-09-29.

Shipping quotes use a per-zone weight step. When EXAMPLE quotes a parcel, it
rounds the parcel's weight up to the weight step of the destination zone, not
to one step for the whole catalog.

## Provenance

Where each section of this inbox comes from.

| Section                                    | Source                             |
|--------------------------------------------|------------------------------------|
| Shipping quotes use a per-zone weight step | parcel-quotes interview 2026-09-29 |
EOF_INBOX
cat > kb/shipping-quotes.md <<'EOF_CORR'
---
title: Shipping Quotes
aliases: [rate quote, quote engine, RATES quote]
attested: 2026-09-10
srd_ref: rates
last_verified: 2026-09-20
---

# Shipping Quotes

How EXAMPLE quotes the shipping price of a parcel: which carriers are asked,
which price list is used, what a quote carries, and how quotes are shown and
handled.

## What a shipping quote is in EXAMPLE

> Not in the platform docs. Attested rates interview
> 2026-09-10.

A shipping quote is the price EXAMPLE offers a buyer for delivering one parcel
with one carrier. EXAMPLE computes it from the carrier price lists it loads
each day. A quote names the carrier, the price, and a confidence value.

## Carriers eligible for a quote

> Not in the platform docs. Attested rates interview
> 2026-09-10.

Only carriers enabled for the shop are asked. A carrier must serve the
destination zone; carriers with no rate for that zone are never asked. A
parcel may receive quotes from several carriers at once.

## Price list used for a quote

> Not in the platform docs. Attested rates interview
> 2026-09-10.

A quote uses the price list the carrier published for the current day.
Price lists from different days are never mixed within one quote.

## Quote confidence value

> Not in the platform docs. Attested rates interview
> 2026-09-10.

Every quote carries a confidence value from 0 to 100. The value expresses
how closely the parcel matches the carrier's size classes. A quote below 30 is
shown greyed out in the quote list.

## Quote delivery estimate

> Not in the platform docs. Attested rates interview
> 2026-09-10.

The delivery estimate is stated as a number of working days from dispatch,
counted in the destination zone's calendar, not as a calendar date.

## Quotes at checkout

> Not in the platform docs. Attested rates interview
> 2026-09-10.

A quote is shown at checkout as one row per carrier, cheapest first.
Selecting the row opens the quote's details, including the carrier and the
confidence value.

## Manual quotes from the order screen

> Not in the platform docs. Attested rates interview
> 2026-09-10.

A clerk can request a quote by hand by picking a carrier on the order
screen. A manual quote uses the latest price list of that carrier. Its result
is stored beside the automated quotes and marked as manual.

## Quotes for split parcels

> Not in the platform docs. Attested rates interview
> 2026-09-10.

An order shipped as several parcels is quoted parcel by parcel. That
quote is separate from the single-parcel quote described above.

## Quotes and address data quality

> Not in the platform docs. Attested rates interview
> 2026-09-10.

Quoting depends on the destination address. Postcode and country come from
the buyer's address book; an address with no postcode is shown in violet on
the order screen and must be corrected before its quotes can be trusted.

## Quote statuses

> Not in the platform docs. Attested rates interview
> 2026-09-10.

A quote is New when it is produced. A clerk can set it to To check,
Confirmed, or Dismissed. Setting an automated quote to To check is what opens a
pricing review.

## Quote recalculation after rate edits

> Not in the platform docs. Attested rates interview
> 2026-09-10.

Editing a carrier rate does not recalculate past quotes. Only quotes
computed after the edit use the changed rate.

## Provenance

Where each section of this page comes from.

| Section                              | Source                     |
|--------------------------------------|----------------------------|
| What a shipping quote is in EXAMPLE  | rates interview 2026-09-10 |
| Carriers eligible for a quote        | rates interview 2026-09-10 |
| Price list used for a quote          | rates interview 2026-09-10 |
| Quote confidence value               | rates interview 2026-09-10 |
| Quote delivery estimate              | rates interview 2026-09-10 |
| Quotes at checkout                   | rates interview 2026-09-10 |
| Manual quotes from the order screen  | rates interview 2026-09-10 |
| Quotes for split parcels             | rates interview 2026-09-10 |
| Quotes and address data quality      | rates interview 2026-09-10 |
| Quote statuses                       | rates interview 2026-09-10 |
| Quote recalculation after rate edits | rates interview 2026-09-10 |
EOF_CORR
