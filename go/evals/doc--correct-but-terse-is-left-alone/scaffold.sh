#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module example.com/kv

go 1.22
EOF_0
mkdir -p kv
cat > kv/kv.go <<'EOF_1'
// Package kv holds string values in memory.
package kv

// Store maps keys to values.
type Store struct {
	m map[string]string
}

// NewStore returns an empty Store.
func NewStore() *Store {
	return &Store{m: map[string]string{}}
}

// Get returns the value stored under key, or the zero value when key
// is absent.
func Get(sto *Store, key string) string {
	return sto.m[key]
}
EOF_1
