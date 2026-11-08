#!/usr/bin/env bash
set -euo pipefail
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
cat > go.mod <<'EOF_0'
module example.com/mem

go 1.22
EOF_0
mkdir -p mem
cat > mem/mem.go <<'EOF_1'
// Package mem keeps decoded blobs in memory.
package mem

import "errors"

var cache = map[string][]byte{}

// Put decodes raw and stores it under key.
func Put(key string, raw []byte) error {
	data, err := decode(raw)
	if err != nil {
		return err
	} else {
		cache[key] = data
	}
	return nil
}

// Drop removes key.
func Drop(key string) error {
	if len(key) == 0 {
		return errors.New("empty key")
	} else {
		delete(cache, key)
	}
	return nil
}

func decode(raw []byte) ([]byte, error) { return raw, nil }
EOF_1
git add -A
git commit -qm 'initial'
mkdir -p mem
cat > mem/mem.go <<'EOF_0'
// Package mem keeps decoded blobs in memory.
package mem

import "errors"

var cache = map[string][]byte{}

// Put decodes raw and stores it under key.
func Put(key string, raw []byte) error {
	data, err := decode(raw)
	if err != nil {
		return err
	}
	cache[key] = data
	return nil
}

// Drop removes key.
func Drop(key string) error {
	if len(key) == 0 {
		return errors.New("empty key")
	}
	delete(cache, key)
	return nil
}

func decode(raw []byte) ([]byte, error) { return raw, nil }
EOF_0
git add mem/mem.go
