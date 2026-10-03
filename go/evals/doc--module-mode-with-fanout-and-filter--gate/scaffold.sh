#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module example.com/mod

go 1.22
EOF_0
mkdir -p api
cat > api/api.go <<'EOF_1'
// Package api routes request paths to handler names.
package api

import "strings"

// Router maps path prefixes to handler names.
type Router struct {
	routes map[string]string
}

// NewRouter returns an empty Router.
func NewRouter() *Router {
	return &Router{routes: map[string]string{}}
}

func (rtr *Router) Handle(prefix, name string) {
	rtr.routes[prefix] = name
}

// match finds the handler
func (rtr *Router) Match(path string) string {
	for prefix, name := range rtr.routes {
		if strings.HasPrefix(path, prefix) {
			return name
		}
	}
	return ""
}
EOF_1
mkdir -p svc
cat > svc/svc.go <<'EOF_2'
// Package svc wires the api package into a running service.
package svc

import "example.com/mod/api"

// Service serves requests through a Router.
type Service struct {
	rtr *api.Router
}

func New(rtr *api.Router) *Service {
	return &Service{rtr: rtr}
}

// Lookup returns the handler name for path.
func (srv *Service) Lookup(path string) string {
	// call Match
	return srv.rtr.Match(path)
}
EOF_2
mkdir -p auth
cat > auth/auth.go <<'EOF_3'
// Package auth checks bearer tokens.
package auth

import "strings"

func Token(header string) string {
	return strings.TrimPrefix(header, "Bearer ")
}
EOF_3
mkdir -p cache
cat > cache/cache.go <<'EOF_4'
// Package cache holds values in memory.
package cache

// Cache maps keys to values.
type Cache struct {
	m map[string]string
}

func (cac *Cache) Set(k, v string) {
	cac.m[k] = v
}
EOF_4
mkdir -p config
cat > config/config.go <<'EOF_5'
// Package config reads key=value settings.
package config

import "strings"

func Parse(text string) map[string]string {
	out := map[string]string{}
	for _, line := range strings.Split(text, "\n") {
		k, v, _ := strings.Cut(line, "=")
		out[k] = v
	}
	return out
}
EOF_5
mkdir -p events
cat > events/events.go <<'EOF_6'
// Package events fans events out to subscribers.
package events

// Bus delivers events to subscribers.
type Bus struct {
	subs []chan string
}

// publish sends ev
func (bus *Bus) Publish(ev string) {
	for _, sub := range bus.subs {
		sub <- ev
	}
}
EOF_6
mkdir -p httpx
cat > httpx/httpx.go <<'EOF_7'
// Package httpx holds HTTP helpers.
package httpx

import "net/http"

func IsOK(resp *http.Response) bool {
	return resp.StatusCode >= 200 && resp.StatusCode < 300
}
EOF_7
mkdir -p logx
cat > logx/logx.go <<'EOF_8'
// Package logx formats log lines.
package logx

import "fmt"

func Line(level, msg string) string {
	return fmt.Sprintf("[%s] %s", level, msg)
}
EOF_8
mkdir -p metrics
cat > metrics/metrics.go <<'EOF_9'
// Package metrics counts events.
package metrics

// Counter counts events.
type Counter struct {
	n int
}

func (cnt *Counter) Inc() {
	// add one
	cnt.n++
}
EOF_9
mkdir -p queue
cat > queue/queue.go <<'EOF_10'
package queue

// Queue is a FIFO of ints.
type Queue struct {
	items []int
}

// Push appends v.
func (que *Queue) Push(v int) {
	que.items = append(que.items, v)
}
EOF_10
mkdir -p retry
cat > retry/retry.go <<'EOF_11'
// Package retry repeats a call until it succeeds.
package retry

func Do(n int, fn func() error) error {
	var err error
	for range n {
		if err = fn(); err == nil {
			return nil
		}
	}
	return err
}
EOF_11
