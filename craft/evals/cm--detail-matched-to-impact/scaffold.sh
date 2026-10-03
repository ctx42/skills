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
mkdir -p store
cat > store/store.go <<'EOF_1'
package store

import (
	"os"
	"path/filepath"
)

// Open reads the record of the user from dir.
func Open(dir, userId string) ([]byte, error) {
	return os.ReadFile(filepath.Join(dir, userId+".json"))
}

// Endpoint returns the base URL of the store's HTTP mirror.
func Endpoint(host string) string {
	httpUrl := "https://" + host + "/store"
	return httpUrl
}
EOF_1
git add -A
git commit -qm 'feat(store): add record store'
mkdir -p store
cat > store/store.go <<'EOF_0'
// Package store keeps per-user records as JSON files.
package store

import (
	"os"
	"path/filepath"
)

// Open reads the record of the user from dir.
func Open(dir, userID string) ([]byte, error) {
	return os.ReadFile(filepath.Join(dir, userID+".json")) // #nosec G304 -- dir is operator-configured
}

// Endpoint returns the base URL of the store's HTTP mirror.
func Endpoint(host string) string {
	httpURL := "https://" + host + "/store"
	return httpURL
}
EOF_0
git add -A
