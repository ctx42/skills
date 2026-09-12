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
