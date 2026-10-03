#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module example.com/ratelimit

go 1.22
EOF_0
cat > rate-limit-plan.md <<'EOF_1'
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
EOF_1
cat > limiter.go <<'EOF_2'
package ratelimit

import (
	"net/http"
	"sync"
	"time"
)

// Limiter tracks per-key budgets for this process.
type Limiter struct {
	mu      sync.Mutex
	buckets map[string]*bucket
	rate    time.Duration
	burst   int
}

type bucket struct {
	tokens int
	last   time.Time
}

func New(rate time.Duration, burst int) *Limiter {
	return &Limiter{buckets: make(map[string]*bucket), rate: rate, burst: burst}
}

// Allow reports whether key may make a request now.
func (l *Limiter) Allow(key string) bool {
	l.mu.Lock()
	defer l.mu.Unlock()

	b, ok := l.buckets[key]
	if !ok {
		b = &bucket{tokens: l.burst, last: time.Now()}
		l.buckets[key] = b
	}
	refill := int(time.Since(b.last) / l.rate)
	if refill > 0 {
		b.tokens = min(b.tokens+refill, l.burst)
		b.last = time.Now()
	}
	if b.tokens == 0 {
		return false
	}
	b.tokens--
	return true
}

// Middleware rejects requests that exceed the caller's budget.
func (l *Limiter) Middleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if !l.Allow(r.Header.Get("X-API-Key")) {
			http.Error(w, "too many requests", http.StatusTooManyRequests)
			return
		}
		next.ServeHTTP(w, r)
	})
}
EOF_2
