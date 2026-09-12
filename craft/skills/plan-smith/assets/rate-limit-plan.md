# Rate limiter plan

## Summary

| #  | Item             | Status |
|----|------------------|--------|
| 1  | Token bucket     | Y      |
| 2  | Redis counters   | N      |
| 3  | 429 responses    | N      |

Legend: Y implemented · N not yet · X rejected

## 1. Token bucket — [x]

Token-bucket algorithm, refill rate and burst size configurable per route.

Done when: a burst up to the configured size passes and the next request in
the same window does not.

## 2. Redis counters — [ ]

Counters live in the shared Redis cluster so every API process sees the same
budget, and a restart does not hand a caller a fresh allowance.

Done when: two processes share one budget for the same key, and counters
survive a process restart.

## 3. 429 responses — [ ]

A throttled request gets HTTP 429 with a `Retry-After` header holding the
seconds until the bucket refills.

Done when: a throttled request returns 429 and a `Retry-After` a client can
honour.
