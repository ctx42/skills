# Tenant isolation plan

## Summary

| #  | Item                         | Status |
|----|------------------------------|--------|
| 1  | Row-level filters            | N      |
| 2  | Per-tenant keys              | N      |
| 3  | Cross-tenant tests           | N      |

Legend: Y implemented · N not yet · X rejected

## 1. Row-level filters — [ ]

Every query against a tenant-scoped table carries the tenant id, applied by the
repository layer rather than by each call site.

Done when: a query built without a tenant id fails to compile, and the
integration suite covers one table per repository.

## 2. Per-tenant keys — [ ]

Encryption keys are derived per tenant so one tenant's leaked key cannot open
another's data.

Done when: key derivation takes the tenant id, and rotating one tenant's key
leaves the others readable.

## 3. Cross-tenant tests — [ ]

A suite that asserts tenant A cannot read, write, or enumerate tenant B.

Done when: the suite exists and fails if the row-level filter is removed.
