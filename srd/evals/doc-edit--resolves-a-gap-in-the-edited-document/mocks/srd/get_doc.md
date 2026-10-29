---
type: agent
---
For the id `1000000105` or the path `docs/operations/scrub-refunds.md` answer with this document:

# Scrub Refunds

A scrub refund returns part or all of a launch slot fee to the customer when a
launch attempt is scrubbed.

## Refund rates

A weather or factory scrub refunds 100% of the slot fee. A customer-caused
scrub refunds 80% of it.

## Refund record

Each refund is recorded against the customer mission and the launch slot that
was scrubbed.

For any other id answer {"error":"document not found"}.
