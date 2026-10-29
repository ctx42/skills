#!/usr/bin/env bash
set -euo pipefail
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
cat > go.mod <<'EOF_0'
module example.com/app

go 1.22
EOF_0
cat > config.go <<'EOF_1'
package app

import "time"

// config holds the resolved runtime settings.
type config struct {
	tmo time.Duration
}

func newConfig(o Options) config {
	return config{tmo: o.Timeout}
}
EOF_1
cat > options.go <<'EOF_2'
// Package app runs the service.
package app

import "time"

// Options configures the service.
type Options struct {
	Timeout time.Duration
	// Legacy is no longer read.
	Legacy bool
}

// Timeout returns the timeout the service runs with.
func Timeout(o Options) time.Duration {
	return newConfig(o).tmo
}
EOF_2
cat > app_test.go <<'EOF_3'
package app

import (
	"testing"
	"time"
)

func Test_Timeout(t *testing.T) {
	if have := Timeout(Options{Timeout: time.Second}); have != time.Second {
		t.Fatalf("Timeout() = %v", have)
	}
}
EOF_3
mkdir -p examples
cat > examples/main.go <<'EOF_4'
package main

import (
	"fmt"
	"time"

	"example.com/app"
)

func main() {
	fmt.Println(app.Timeout(app.Options{Timeout: time.Second, Legacy: true}))
}
EOF_4
go vet ./... && go test ./... >/dev/null
git add -A
git commit -qm 'initial'
