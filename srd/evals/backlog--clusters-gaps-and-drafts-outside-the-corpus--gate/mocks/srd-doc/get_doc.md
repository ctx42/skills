---
type: agent
---
For the id `confluence/example/operations/storage-housekeeping.md` answer with this document:

# Storage housekeeping

## Nightly jobs

The housekeeping job runs at 02:00 Instance time and compacts the time-series
store.

## Cold storage

Recordings older than 90 days move to the archive tier. Archived recordings
stay playable but load more slowly.

For any other id answer {"error":"document not found"}.
