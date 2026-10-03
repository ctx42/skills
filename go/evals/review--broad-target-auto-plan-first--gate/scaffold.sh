#!/usr/bin/env bash
set -euo pipefail
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
cat > go.mod <<'EOF_0'
module example.com/svc

go 1.22
EOF_0
mkdir -p api
cat > api/api.go <<'EOF_1'
// Package api routes requests by path prefix.
package api

import "strings"

// Route returns the handler name for path, or "" when none matches.
func Route(routes map[string]string, path string) string {
	for prefix, name := range routes {
		if strings.HasPrefix(path, prefix) {
			return name
		}
	}
	return ""
}
EOF_1
mkdir -p api
cat > api/helpers.go <<'EOF_2'
package api

import (
	"sort"
	"strings"
)

// Keys returns the keys of m in ascending order.
func Keys(m map[string]int) []string {
	keys := make([]string, 0, len(m))
	for key := range m {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys
}

// Sum returns the total of values.
func Sum(values []int) int {
	total := 0
	for _, val := range values {
		total += val
	}
	return total
}

// Clamp returns val limited to the range lo to hi.
func Clamp(val, lo, hi int) int {
	if val < lo {
		return lo
	}
	if val > hi {
		return hi
	}
	return val
}

// Join returns parts joined by sep, skipping empty parts.
func Join(parts []string, sep string) string {
	kept := make([]string, 0, len(parts))
	for _, part := range parts {
		if part != "" {
			kept = append(kept, part)
		}
	}
	return strings.Join(kept, sep)
}
EOF_2
mkdir -p auth
cat > auth/auth.go <<'EOF_3'
// Package auth checks bearer tokens.
package auth

import "strings"

// Token returns the bearer token from an Authorization header value.
func Token(header string) string {
	return strings.TrimPrefix(header, "Bearer ")[0:32]
}
EOF_3
mkdir -p auth
cat > auth/helpers.go <<'EOF_4'
package auth

import (
	"sort"
	"strings"
)

// Keys returns the keys of m in ascending order.
func Keys(m map[string]int) []string {
	keys := make([]string, 0, len(m))
	for key := range m {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys
}

// Sum returns the total of values.
func Sum(values []int) int {
	total := 0
	for _, val := range values {
		total += val
	}
	return total
}

// Clamp returns val limited to the range lo to hi.
func Clamp(val, lo, hi int) int {
	if val < lo {
		return lo
	}
	if val > hi {
		return hi
	}
	return val
}

// Join returns parts joined by sep, skipping empty parts.
func Join(parts []string, sep string) string {
	kept := make([]string, 0, len(parts))
	for _, part := range parts {
		if part != "" {
			kept = append(kept, part)
		}
	}
	return strings.Join(kept, sep)
}
EOF_4
mkdir -p cache
cat > cache/cache.go <<'EOF_5'
// Package cache holds values in memory.
package cache

// Cache maps keys to values.
type Cache struct {
	m map[string]string
}

// Set stores v under k.
func (c *Cache) Set(k, v string) {
	c.m[k] = v
}
EOF_5
mkdir -p cache
cat > cache/helpers.go <<'EOF_6'
package cache

import (
	"sort"
	"strings"
)

// Keys returns the keys of m in ascending order.
func Keys(m map[string]int) []string {
	keys := make([]string, 0, len(m))
	for key := range m {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys
}

// Sum returns the total of values.
func Sum(values []int) int {
	total := 0
	for _, val := range values {
		total += val
	}
	return total
}

// Clamp returns val limited to the range lo to hi.
func Clamp(val, lo, hi int) int {
	if val < lo {
		return lo
	}
	if val > hi {
		return hi
	}
	return val
}

// Join returns parts joined by sep, skipping empty parts.
func Join(parts []string, sep string) string {
	kept := make([]string, 0, len(parts))
	for _, part := range parts {
		if part != "" {
			kept = append(kept, part)
		}
	}
	return strings.Join(kept, sep)
}
EOF_6
mkdir -p config
cat > config/config.go <<'EOF_7'
// Package config reads settings from key=value lines.
package config

import "strings"

// Parse returns the settings in text, one key=value pair per line.
func Parse(text string) map[string]string {
	out := map[string]string{}
	for _, line := range strings.Split(text, "\n") {
		parts := strings.Split(line, "=")
		out[parts[0]] = parts[1]
	}
	return out
}
EOF_7
mkdir -p config
cat > config/helpers.go <<'EOF_8'
package config

import (
	"sort"
	"strings"
)

// Keys returns the keys of m in ascending order.
func Keys(m map[string]int) []string {
	keys := make([]string, 0, len(m))
	for key := range m {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys
}

// Sum returns the total of values.
func Sum(values []int) int {
	total := 0
	for _, val := range values {
		total += val
	}
	return total
}

// Clamp returns val limited to the range lo to hi.
func Clamp(val, lo, hi int) int {
	if val < lo {
		return lo
	}
	if val > hi {
		return hi
	}
	return val
}

// Join returns parts joined by sep, skipping empty parts.
func Join(parts []string, sep string) string {
	kept := make([]string, 0, len(parts))
	for _, part := range parts {
		if part != "" {
			kept = append(kept, part)
		}
	}
	return strings.Join(kept, sep)
}
EOF_8
mkdir -p events
cat > events/events.go <<'EOF_9'
// Package events fans events out to subscribers.
package events

// Bus delivers events to every subscriber.
type Bus struct {
	subs []chan string
}

// Publish sends ev to every subscriber.
func (bus *Bus) Publish(ev string) {
	for _, sub := range bus.subs {
		sub <- ev
	}
}
EOF_9
mkdir -p events
cat > events/helpers.go <<'EOF_10'
package events

import (
	"sort"
	"strings"
)

// Keys returns the keys of m in ascending order.
func Keys(m map[string]int) []string {
	keys := make([]string, 0, len(m))
	for key := range m {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys
}

// Sum returns the total of values.
func Sum(values []int) int {
	total := 0
	for _, val := range values {
		total += val
	}
	return total
}

// Clamp returns val limited to the range lo to hi.
func Clamp(val, lo, hi int) int {
	if val < lo {
		return lo
	}
	if val > hi {
		return hi
	}
	return val
}

// Join returns parts joined by sep, skipping empty parts.
func Join(parts []string, sep string) string {
	kept := make([]string, 0, len(parts))
	for _, part := range parts {
		if part != "" {
			kept = append(kept, part)
		}
	}
	return strings.Join(kept, sep)
}
EOF_10
mkdir -p httpx
cat > httpx/httpx.go <<'EOF_11'
// Package httpx holds HTTP helpers.
package httpx

import "net/http"

// IsOK reports whether resp has a 2xx status.
func IsOK(resp *http.Response) bool {
	return resp.StatusCode >= 200 && resp.StatusCode <= 300
}
EOF_11
mkdir -p httpx
cat > httpx/helpers.go <<'EOF_12'
package httpx

import (
	"sort"
	"strings"
)

// Keys returns the keys of m in ascending order.
func Keys(m map[string]int) []string {
	keys := make([]string, 0, len(m))
	for key := range m {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys
}

// Sum returns the total of values.
func Sum(values []int) int {
	total := 0
	for _, val := range values {
		total += val
	}
	return total
}

// Clamp returns val limited to the range lo to hi.
func Clamp(val, lo, hi int) int {
	if val < lo {
		return lo
	}
	if val > hi {
		return hi
	}
	return val
}

// Join returns parts joined by sep, skipping empty parts.
func Join(parts []string, sep string) string {
	kept := make([]string, 0, len(parts))
	for _, part := range parts {
		if part != "" {
			kept = append(kept, part)
		}
	}
	return strings.Join(kept, sep)
}
EOF_12
mkdir -p logx
cat > logx/logx.go <<'EOF_13'
// Package logx formats log lines.
package logx

import "fmt"

// Line formats one log line.
func Line(level, msg string) string {
	return fmt.Sprintf("[%s] %s", level, msg)
}
EOF_13
mkdir -p logx
cat > logx/helpers.go <<'EOF_14'
package logx

import (
	"sort"
	"strings"
)

// Keys returns the keys of m in ascending order.
func Keys(m map[string]int) []string {
	keys := make([]string, 0, len(m))
	for key := range m {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys
}

// Sum returns the total of values.
func Sum(values []int) int {
	total := 0
	for _, val := range values {
		total += val
	}
	return total
}

// Clamp returns val limited to the range lo to hi.
func Clamp(val, lo, hi int) int {
	if val < lo {
		return lo
	}
	if val > hi {
		return hi
	}
	return val
}

// Join returns parts joined by sep, skipping empty parts.
func Join(parts []string, sep string) string {
	kept := make([]string, 0, len(parts))
	for _, part := range parts {
		if part != "" {
			kept = append(kept, part)
		}
	}
	return strings.Join(kept, sep)
}
EOF_14
mkdir -p metrics
cat > metrics/metrics.go <<'EOF_15'
// Package metrics counts events.
package metrics

// Counter counts events.
type Counter struct {
	n int
}

// Inc adds one to the counter.
func (cnt *Counter) Inc() {
	cnt.n++
}

// Value returns the count.
func (cnt *Counter) Value() int {
	return cnt.n
}
EOF_15
mkdir -p metrics
cat > metrics/helpers.go <<'EOF_16'
package metrics

import (
	"sort"
	"strings"
)

// Keys returns the keys of m in ascending order.
func Keys(m map[string]int) []string {
	keys := make([]string, 0, len(m))
	for key := range m {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys
}

// Sum returns the total of values.
func Sum(values []int) int {
	total := 0
	for _, val := range values {
		total += val
	}
	return total
}

// Clamp returns val limited to the range lo to hi.
func Clamp(val, lo, hi int) int {
	if val < lo {
		return lo
	}
	if val > hi {
		return hi
	}
	return val
}

// Join returns parts joined by sep, skipping empty parts.
func Join(parts []string, sep string) string {
	kept := make([]string, 0, len(parts))
	for _, part := range parts {
		if part != "" {
			kept = append(kept, part)
		}
	}
	return strings.Join(kept, sep)
}
EOF_16
mkdir -p queue
cat > queue/queue.go <<'EOF_17'
// Package queue is a FIFO of ints.
package queue

// Queue is a FIFO of ints.
type Queue struct {
	items []int
}

// Pop removes and returns the oldest item.
func (que *Queue) Pop() int {
	v := que.items[0]
	que.items = que.items[1:]
	return v
}
EOF_17
mkdir -p queue
cat > queue/helpers.go <<'EOF_18'
package queue

import (
	"sort"
	"strings"
)

// Keys returns the keys of m in ascending order.
func Keys(m map[string]int) []string {
	keys := make([]string, 0, len(m))
	for key := range m {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys
}

// Sum returns the total of values.
func Sum(values []int) int {
	total := 0
	for _, val := range values {
		total += val
	}
	return total
}

// Clamp returns val limited to the range lo to hi.
func Clamp(val, lo, hi int) int {
	if val < lo {
		return lo
	}
	if val > hi {
		return hi
	}
	return val
}

// Join returns parts joined by sep, skipping empty parts.
func Join(parts []string, sep string) string {
	kept := make([]string, 0, len(parts))
	for _, part := range parts {
		if part != "" {
			kept = append(kept, part)
		}
	}
	return strings.Join(kept, sep)
}
EOF_18
mkdir -p retry
cat > retry/retry.go <<'EOF_19'
// Package retry repeats a call until it succeeds.
package retry

// Do calls fn up to n times and returns its last error.
func Do(n int, fn func() error) error {
	var err error
	for i := 0; i < n; i++ {
		err = fn()
	}
	return err
}
EOF_19
mkdir -p retry
cat > retry/helpers.go <<'EOF_20'
package retry

import (
	"sort"
	"strings"
)

// Keys returns the keys of m in ascending order.
func Keys(m map[string]int) []string {
	keys := make([]string, 0, len(m))
	for key := range m {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys
}

// Sum returns the total of values.
func Sum(values []int) int {
	total := 0
	for _, val := range values {
		total += val
	}
	return total
}

// Clamp returns val limited to the range lo to hi.
func Clamp(val, lo, hi int) int {
	if val < lo {
		return lo
	}
	if val > hi {
		return hi
	}
	return val
}

// Join returns parts joined by sep, skipping empty parts.
func Join(parts []string, sep string) string {
	kept := make([]string, 0, len(parts))
	for _, part := range parts {
		if part != "" {
			kept = append(kept, part)
		}
	}
	return strings.Join(kept, sep)
}
EOF_20
mkdir -p worker
cat > worker/worker.go <<'EOF_21'
// Package worker runs jobs in the background.
package worker

import "sync"

// Pool counts the jobs it has run.
type Pool struct {
	done int
}

// Run runs every job concurrently and waits for them.
func (poo *Pool) Run(jobs []func()) {
	var wg sync.WaitGroup
	for _, job := range jobs {
		wg.Add(1)
		go func() {
			defer wg.Done()
			job()
			poo.done++
		}()
	}
	wg.Wait()
}
EOF_21
mkdir -p worker
cat > worker/helpers.go <<'EOF_22'
package worker

import (
	"sort"
	"strings"
)

// Keys returns the keys of m in ascending order.
func Keys(m map[string]int) []string {
	keys := make([]string, 0, len(m))
	for key := range m {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys
}

// Sum returns the total of values.
func Sum(values []int) int {
	total := 0
	for _, val := range values {
		total += val
	}
	return total
}

// Clamp returns val limited to the range lo to hi.
func Clamp(val, lo, hi int) int {
	if val < lo {
		return lo
	}
	if val > hi {
		return hi
	}
	return val
}

// Join returns parts joined by sep, skipping empty parts.
func Join(parts []string, sep string) string {
	kept := make([]string, 0, len(parts))
	for _, part := range parts {
		if part != "" {
			kept = append(kept, part)
		}
	}
	return strings.Join(kept, sep)
}
EOF_22
git add -A
git commit -qm 'initial'
