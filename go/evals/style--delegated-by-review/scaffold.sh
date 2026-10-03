#!/usr/bin/env bash
set -euo pipefail
mkdir -p pkg/store
cat > go.mod <<'EOF_GO_MOD'
module example.com/store

go 1.26

require github.com/ctx42/testing v0.56.0
EOF_GO_MOD
cat > go.sum <<'EOF_GO_SUM'
github.com/ctx42/testing v0.56.0 h1:+yZwRy+5JQb+14YtRTGJxWbAMAP9qlU9pMa8TPqgdzE=
github.com/ctx42/testing v0.56.0/go.mod h1:wRBqNRtlxDZnXIjgCX3zr05Acl6JC1D6cSBN2IpaMIs=
EOF_GO_SUM
cat > pkg/store/store.go <<'EOF_PKG_STORE_STORE_GO'
// Package store keeps named counters in memory.
package store

// Store holds counters by name.
type Store struct {
	counts map[string]int
}

// New returns an empty Store.
func New() *Store {
	return &Store{counts: map[string]int{}}
}

// Inc adds one to the counter called name.
func (sto *Store) Inc(name string) {
	sto.counts[name]++
}
EOF_PKG_STORE_STORE_GO
cat > pkg/store/store_test.go <<'EOF_PKG_STORE_STORE_TEST_GO'
package store

import (
	"testing"

	"github.com/ctx42/testing/pkg/assert"
)

func Test_Store_Inc(t *testing.T) {
	// --- Given ---
	sto := New()

	name := "a"

	// --- When ---
	sto.Inc(name)

	// --- Then ---
	assert.Equal(t, 1, sto.counts["a"])
}
EOF_PKG_STORE_STORE_TEST_GO
git init -q -b main
git add -A
git -c user.name=eval -c user.email=eval@example.com commit -qm init
cat >> pkg/store/store.go <<'EOF_DIFF'

// Total returns the sum of the counters named in names.
func (s *Store) Total(names []string) int {
	total := 0
	for i := 1; i < len(names); i++ {
		total += s.counts[names[i]]
	}
	return total
}
EOF_DIFF
