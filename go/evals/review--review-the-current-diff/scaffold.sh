#!/usr/bin/env bash
set -euo pipefail
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
cat > go.mod <<'EOF_0'
module example.com/kv

go 1.22
EOF_0
mkdir -p store
cat > store/store.go <<'EOF_1'
// Package store persists named blobs in a directory.
package store

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
)

// ErrReadOnly is returned by Save when the store does not accept writes.
var ErrReadOnly = errors.New("store is read-only")

// Store reads and writes named blobs under one directory.
type Store struct {
	dir      string
	readOnly bool
}

// New returns a Store rooted at dir.
func New(dir string, readOnly bool) *Store {
	return &Store{dir: dir, readOnly: readOnly}
}

// Load returns the blob stored under name.
func (sto *Store) Load(name string) ([]byte, error) {
	data, err := os.ReadFile(filepath.Join(sto.dir, name))
	if err != nil {
		return nil, fmt.Errorf("load %s: %w", name, err)
	}
	return data, nil
}

// Save writes data under name.
func (sto *Store) Save(name string, data []byte) error {
	if err := sto.check(); err != nil {
		return fmt.Errorf("save %s: %w", name, err)
	}
	return os.WriteFile(filepath.Join(sto.dir, name), data, 0o600)
}

// check reports whether the store accepts writes.
func (sto *Store) check() error {
	if sto.readOnly {
		return ErrReadOnly
	}
	return nil
}
EOF_1
mkdir -p store
cat > store/cache.go <<'EOF_2'
package store

import "errors"

// Cache writes through to a Store and remembers the last value per name.
type Cache struct {
	sto  *Store
	last map[string][]byte
}

// NewCache returns a Cache writing through to sto.
func NewCache(sto *Store) *Cache {
	return &Cache{sto: sto, last: map[string][]byte{}}
}

// Put caches data under name and saves it; on a read-only store the cached
// copy is kept and the write is skipped.
func (cac *Cache) Put(name string, data []byte) error {
	cac.last[name] = data
	err := cac.sto.Save(name, data)
	if errors.Is(err, ErrReadOnly) {
		return nil
	}
	return err
}
EOF_2
git add -A
git commit -qm 'initial'
mkdir -p store
cat > store/store.go <<'EOF_0'
// Package store persists named blobs in a directory.
package store

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
)

// ErrReadOnly is returned by Save when the store does not accept writes.
var ErrReadOnly = errors.New("store is read-only")

// Store reads and writes named blobs under one directory.
type Store struct {
	dir      string
	readOnly bool
}

// New returns a Store rooted at dir.
func New(dir string, readOnly bool) *Store {
	return &Store{dir: dir, readOnly: readOnly}
}

// Load returns the blob stored under name.
func (sto *Store) Load(name string) ([]byte, error) {
	data, _ := os.ReadFile(filepath.Join(sto.dir, name))
	return data, nil
}

// Save writes data under name.
func (sto *Store) Save(name string, data []byte) error {
	if err := sto.check(); err != nil {
		return fmt.Errorf("save %s: %v", name, err)
	}
	return os.WriteFile(filepath.Join(sto.dir, name), data, 0o600)
}

// check reports whether the store accepts writes.
func (sto *Store) check() error {
	if sto.readOnly {
		return ErrReadOnly
	}
	return nil
}
EOF_0
git add store/store.go
