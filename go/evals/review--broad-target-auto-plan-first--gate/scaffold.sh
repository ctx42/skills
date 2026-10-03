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
mkdir -p auth
cat > auth/auth.go <<'EOF_2'
// Package auth checks bearer tokens.
package auth

import "strings"

// Token returns the bearer token from an Authorization header value.
func Token(header string) string {
	return strings.TrimPrefix(header, "Bearer ")[0:32]
}
EOF_2
mkdir -p cache
cat > cache/cache.go <<'EOF_3'
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
EOF_3
mkdir -p config
cat > config/config.go <<'EOF_4'
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
EOF_4
mkdir -p events
cat > events/events.go <<'EOF_5'
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
EOF_5
mkdir -p httpx
cat > httpx/httpx.go <<'EOF_6'
// Package httpx holds HTTP helpers.
package httpx

import "net/http"

// IsOK reports whether resp has a 2xx status.
func IsOK(resp *http.Response) bool {
	return resp.StatusCode >= 200 && resp.StatusCode <= 300
}
EOF_6
mkdir -p logx
cat > logx/logx.go <<'EOF_7'
// Package logx formats log lines.
package logx

import "fmt"

// Line formats one log line.
func Line(level, msg string) string {
	return fmt.Sprintf("[%s] %s", level, msg)
}
EOF_7
mkdir -p metrics
cat > metrics/metrics.go <<'EOF_8'
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
EOF_8
mkdir -p queue
cat > queue/queue.go <<'EOF_9'
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
EOF_9
mkdir -p retry
cat > retry/retry.go <<'EOF_10'
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
EOF_10
mkdir -p worker
cat > worker/worker.go <<'EOF_11'
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
EOF_11
git add -A
git commit -qm 'initial'
