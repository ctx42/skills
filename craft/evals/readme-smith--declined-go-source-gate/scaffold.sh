#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module github.com/acme/kit

go 1.22
EOF_0
cat > LICENSE <<'EOF_1'
MIT License

Copyright (c) 2026 Acme

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, subject to the following conditions:
the above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
EOF_1
cat > CONTRIBUTING.md <<'EOF_2'
# Contributing

1. Fork the repository and create a topic branch.
2. Run `go test ./...` before you push.
3. Sign off every commit (`git commit -s`).
4. Open a pull request against `master`.
EOF_2
mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'EOF_3'
name: ci
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
      - run: go install github.com/ctx42/gomake@latest
      - name: gomake check
        run: gomake :go:check
EOF_3
cat > README.md <<'EOF_4'
[![Go](https://github.com/acme/kit/actions/workflows/ci.yml/badge.svg)](https://github.com/acme/kit/actions/workflows/ci.yml)
[![Go Reference](https://pkg.go.dev/badge/github.com/acme/kit.svg)](https://pkg.go.dev/github.com/acme/kit)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

# kit

Small building blocks for Go services.

## Packages

| Package                          | Description                          |
|----------------------------------|--------------------------------------|
| [store](pkg/store/README.md)     | Embedded append-only key-value store |
| [cache](pkg/cache/README.md)     | In-memory TTL cache                  |

## Installation

```shell
go get github.com/acme/kit
```

## License

MIT; see [LICENSE](LICENSE).
EOF_4
mkdir -p pkg/cache
cat > pkg/cache/cache.go <<'EOF_5'
// Package cache is an in-memory cache whose entries expire after a TTL.
package cache

import (
	"sync"
	"time"
)

// Cache maps string keys to values that expire after a fixed TTL.
type Cache struct {
	mu  sync.Mutex
	ttl time.Duration
	m   map[string]entry
}

type entry struct {
	val []byte
	exp time.Time
}

// New returns an empty Cache whose entries live for ttl.
func New(ttl time.Duration) *Cache {
	return &Cache{ttl: ttl, m: map[string]entry{}}
}

// Set stores val under key.
func (c *Cache) Set(key string, val []byte) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.m[key] = entry{val: val, exp: time.Now().Add(c.ttl)}
}

// Get returns the value under key and whether it was present and unexpired.
func (c *Cache) Get(key string) ([]byte, bool) {
	c.mu.Lock()
	defer c.mu.Unlock()
	e, ok := c.m[key]
	if !ok || time.Now().After(e.exp) {
		return nil, false
	}
	return e.val, true
}
EOF_5
mkdir -p pkg/cache
cat > pkg/cache/README.md <<'EOF_6'
# cache

In-memory cache for Go services whose entries expire after a fixed TTL.

## Overview

`cache` keeps byte values in memory and forgets them once their TTL has passed.

## Usage

```go
c := cache.New(time.Minute)
c.Set("user:42", []byte("Ada"))
v, ok := c.Get("user:42")
fmt.Println(string(v), ok)
```
EOF_6
mkdir -p pkg/store
cat > pkg/store/store.go <<'EOF_7'
// Package store is an embedded key-value store that keeps one append-only log
// file per directory.
package store

import (
	"bufio"
	"encoding/base64"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"
)

// ErrNotFound is returned by Get for a key that was never put.
var ErrNotFound = errors.New("store: key not found")

// Store is an open store. It is safe for concurrent use.
type Store struct {
	mu sync.Mutex
	f  *os.File
	m  map[string][]byte
}

// Open opens the store in dir, creating dir and its log file when missing,
// and replays the log into memory.
func Open(dir string) (*Store, error) {
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return nil, err
	}
	f, err := os.OpenFile(filepath.Join(dir, "store.log"), os.O_CREATE|os.O_RDWR|os.O_APPEND, 0o644)
	if err != nil {
		return nil, err
	}
	s := &Store{f: f, m: map[string][]byte{}}
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		k, v, ok := strings.Cut(sc.Text(), "\t")
		if !ok {
			continue
		}
		b, err := base64.StdEncoding.DecodeString(v)
		if err != nil {
			return nil, fmt.Errorf("store: corrupt log: %w", err)
		}
		s.m[k] = b
	}
	return s, sc.Err()
}

// Put appends key and val to the log and makes val visible to Get.
func (s *Store) Put(key string, val []byte) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	line := key + "\t" + base64.StdEncoding.EncodeToString(val) + "\n"
	if _, err := s.f.WriteString(line); err != nil {
		return err
	}
	s.m[key] = val
	return nil
}

// Get returns the last value put under key, or ErrNotFound.
func (s *Store) Get(key string) ([]byte, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	v, ok := s.m[key]
	if !ok {
		return nil, ErrNotFound
	}
	return v, nil
}

// Close closes the log file.
func (s *Store) Close() error { return s.f.Close() }
EOF_7
mkdir -p pkg/store
cat > pkg/store/README.md <<'EOF_8'
# store

Embedded key-value store for Go services that keeps one append-only log per
directory.

## Overview

`store` replays its log into memory on `Open`, so reads never touch the disk.

## Installation

```
go get github.com/acme/kit
```

## Usage

```go
s := store.New("data")
s.Set("user:42", "Ada")
fmt.Println(s.Get("user:42"))
```

## License

MIT License. Copyright (c) 2026 Acme. Permission is hereby granted, free of
charge, to any person obtaining a copy of this software.
EOF_8
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
git remote add origin https://github.com/acme/kit.git
git add -A
git commit -q -m 'chore: initial import'
