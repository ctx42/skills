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
mkdir -p conf
cat > conf/duration.go <<'EOF_1'
// Package conf parses configuration values.
package conf

import (
	"fmt"
	"time"
)

// ParseDuration parses s as a time.Duration. It rejects negative values:
// every duration in the configuration is a wait, and a wait cannot be
// negative.
func ParseDuration(s string) (time.Duration, error) {
	d, err := time.ParseDuration(s)
	if err != nil {
		return 0, fmt.Errorf("parse duration %q: %w", s, err)
	}
	return d, nil
}
EOF_1
git add -A
git commit -qm 'feat(conf): add ParseDuration'
mkdir -p conf
cat > conf/duration.go <<'EOF_0'
// Package conf parses configuration values.
package conf

import (
	"fmt"
	"time"
)

// ParseDuration parses s as a time.Duration. It rejects negative values:
// every duration in the configuration is a wait, and a wait cannot be
// negative.
func ParseDuration(s string) (time.Duration, error) {
	d, err := time.ParseDuration(s)
	if err != nil {
		return 0, fmt.Errorf("parse duration %q: %w", s, err)
	}
	if d < 0 {
		return 0, fmt.Errorf("parse duration %q: negative", s)
	}
	return d, nil
}
EOF_0
mkdir -p conf
cat > conf/duration_test.go <<'EOF_1'
package conf

import "testing"

func TestParseDuration_negative(t *testing.T) {
	_, err := ParseDuration("-5s")
	if err == nil {
		t.Fatal("expected an error for a negative duration")
	}
}
EOF_1
git add -A
