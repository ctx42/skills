---
type: agent
---
For the id `1882030917` or the path `docs/operations/storage-housekeeping.md` answer with this document:

# Storage housekeeping

## Nightly jobs

The housekeeping job runs at 02:00 Instance time and compacts the order
database.

## Cold storage

Uploaded e-book files older than 90 days move to the archive tier. Archived
files stay downloadable but load more slowly.

For any other id answer {"error":"document not found"}.
