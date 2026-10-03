#!/usr/bin/env bash
set -euo pipefail
cat > .gitignore <<'EOF_0'
tmp/
EOF_0
cat > go.mod <<'EOF_1'
module example.com/evalmod

go 1.22
EOF_1
mkdir -p pkg/alpha
cat > pkg/alpha/alpha.go <<'EOF_2'
// Package alpha is part of the eval module.
package alpha

// Name returns the alpha label for n.
func Name(n int) string {
	if n < 0 {
		return "alpha-negative"
	}
	return "alpha"
}
EOF_2
cat > pkg/alpha/alpha_test.go <<'EOF_3'
package alpha

import "testing"

func Test_Name(t *testing.T) {
	// --- Given ---
	n := 1

	// --- When ---
	have := Name(n)

	// --- Then ---
	if have != "alpha" {
		t.Errorf("want %q, have %q", "alpha", have)
	}
}
EOF_3
mkdir -p pkg/api
cat > pkg/api/route.go <<'EOF_4'
// Package api maps request paths to handlers.
package api

import "strings"

// Route returns the handler name for path.
func Route(path string) string {
	if path == "" || path == "/" {
		return "index"
	}
	if strings.HasPrefix(path, "/admin") {
		return "admin"
	}
	return "page"
}

// Method normalizes an HTTP method name.
func Method(m string) string {
	if m == "" {
		return "GET"
	}
	if strings.EqualFold(m, "head") {
		return "GET"
	}
	return strings.ToUpper(m)
}
EOF_4
cat > pkg/api/route_test.go <<'EOF_5'
package api

import "testing"

func Test_Route_tabular(t *testing.T) {
	tt := []struct {
		testN string

		path string
		want string
	}{
		{"page", "/about", "page"},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Route(tc.path)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %q, have %q", tc.want, have)
			}
		})
	}
}

func Test_Method_tabular(t *testing.T) {
	tt := []struct {
		testN string

		m    string
		want string
	}{
		{"post", "post", "POST"},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Method(tc.m)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %q, have %q", tc.want, have)
			}
		})
	}
}
EOF_5
mkdir -p pkg/beta
cat > pkg/beta/beta.go <<'EOF_6'
// Package beta is part of the eval module.
package beta

// Name returns the beta label for n.
func Name(n int) string {
	if n < 0 {
		return "beta-negative"
	}
	return "beta"
}
EOF_6
cat > pkg/beta/beta_test.go <<'EOF_7'
package beta

import "testing"

func Test_Name(t *testing.T) {
	// --- Given ---
	n := 1

	// --- When ---
	have := Name(n)

	// --- Then ---
	if have != "beta" {
		t.Errorf("want %q, have %q", "beta", have)
	}
}
EOF_7
mkdir -p pkg/cache
cat > pkg/cache/cache.go <<'EOF_8'
// Package cache is part of the eval module.
package cache

// Name returns the cache label for n.
func Name(n int) string {
	if n < 0 {
		return "cache-negative"
	}
	return "cache"
}
EOF_8
cat > pkg/cache/cache_test.go <<'EOF_9'
package cache

import "testing"

func Test_Name(t *testing.T) {
	// --- Given ---
	n := 1

	// --- When ---
	have := Name(n)

	// --- Then ---
	if have != "cache" {
		t.Errorf("want %q, have %q", "cache", have)
	}
}
EOF_9
mkdir -p pkg/db
cat > pkg/db/db.go <<'EOF_10'
// Package db is part of the eval module.
package db

// Name returns the db label for n.
func Name(n int) string {
	if n < 0 {
		return "db-negative"
	}
	return "db"
}
EOF_10
cat > pkg/db/db_test.go <<'EOF_11'
package db

import "testing"

func Test_Name(t *testing.T) {
	// --- Given ---
	n := 1

	// --- When ---
	have := Name(n)

	// --- Then ---
	if have != "db" {
		t.Errorf("want %q, have %q", "db", have)
	}
}
EOF_11
mkdir -p pkg/logs
cat > pkg/logs/logs.go <<'EOF_12'
// Package logs is part of the eval module.
package logs

// Name returns the logs label for n.
func Name(n int) string {
	if n < 0 {
		return "logs-negative"
	}
	return "logs"
}
EOF_12
cat > pkg/logs/logs_test.go <<'EOF_13'
package logs

import "testing"

func Test_Name(t *testing.T) {
	// --- Given ---
	n := 1

	// --- When ---
	have := Name(n)

	// --- Then ---
	if have != "logs" {
		t.Errorf("want %q, have %q", "logs", have)
	}
}
EOF_13
mkdir -p pkg/queue
cat > pkg/queue/queue.go <<'EOF_14'
// Package queue is part of the eval module.
package queue

// Name returns the queue label for n.
func Name(n int) string {
	if n < 0 {
		return "queue-negative"
	}
	return "queue"
}
EOF_14
cat > pkg/queue/queue_test.go <<'EOF_15'
package queue

import "testing"

func Test_Name(t *testing.T) {
	// --- Given ---
	n := 1

	// --- When ---
	have := Name(n)

	// --- Then ---
	if have != "queue" {
		t.Errorf("want %q, have %q", "queue", have)
	}
}
EOF_15
mkdir -p pkg/svc
cat > pkg/svc/fee.go <<'EOF_16'
// Package svc computes order fees.
package svc

// Fee returns the handling fee in cents for an order of the given total.
func Fee(total int) int {
	if total <= 0 {
		return 0
	}
	if total >= 10000 {
		return 0
	}
	return 250
}

// Tax returns the tax in cents for amount at the given rate in percent.
func Tax(amount, rate int) int {
	if rate <= 0 {
		return 0
	}
	if amount <= 0 {
		return 0
	}
	return amount * rate / 100
}
EOF_16
cat > pkg/svc/fee_test.go <<'EOF_17'
package svc

import "testing"

func Test_Fee_tabular(t *testing.T) {
	tt := []struct {
		testN string

		total int
		want  int
	}{
		{"small order", 500, 250},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Fee(tc.total)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %d, have %d", tc.want, have)
			}
		})
	}
}

func Test_Tax_tabular(t *testing.T) {
	tt := []struct {
		testN string

		amount int
		rate   int
		want   int
	}{
		{"standard", 1000, 8, 80},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Tax(tc.amount, tc.rate)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %d, have %d", tc.want, have)
			}
		})
	}
}
EOF_17
mkdir -p pkg/util
cat > pkg/util/util.go <<'EOF_18'
// Package util is part of the eval module.
package util

// Name returns the util label for n.
func Name(n int) string {
	if n < 0 {
		return "util-negative"
	}
	return "util"
}
EOF_18
cat > pkg/util/util_test.go <<'EOF_19'
package util

import "testing"

func Test_Name(t *testing.T) {
	// --- Given ---
	n := 1

	// --- When ---
	have := Name(n)

	// --- Then ---
	if have != "util" {
		t.Errorf("want %q, have %q", "util", have)
	}
}
EOF_19
