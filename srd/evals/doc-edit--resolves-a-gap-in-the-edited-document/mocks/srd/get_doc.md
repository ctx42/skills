---
type: agent
---
For the id `2215906431` or the path `docs/operations/reconciliation.md` answer with this document:

# Reconciliation

A reconciliation run compares the postings of two Ledgers to find a payment
mismatch between them.

## Prerequisites

Both Ledgers use the same currency and close at the same cut-off.

## Results

A run reports each mismatch as an amount and the pair of postings behind it.

For any other id answer {"error":"document not found"}.
