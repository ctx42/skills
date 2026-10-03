#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module github.com/acme/confy

go 1.22
EOF_0
cat > LICENSE <<'EOF_1'
MIT License

Copyright (c) 2026 Acme
EOF_1
mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'EOF_2'
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
      - run: go vet ./...
      - run: go test ./...
EOF_2
cat > confy.go <<'EOF_3'
// Package confy loads layered settings: env files, then flags, then defaults.
package confy

import (
	"bufio"
	"os"
	"strings"
)

// Settings holds resolved setting values by name.
type Settings map[string]string

// Load resolves settings from envFile, then from flags, then from defaults;
// the first layer that sets a name wins.
func Load(envFile string, flags, defaults map[string]string) (Settings, error) {
	s := Settings{}
	for k, v := range defaults {
		s[k] = v
	}
	for k, v := range flags {
		s[k] = v
	}
	f, err := os.Open(envFile)
	if err != nil {
		if os.IsNotExist(err) {
			return s, nil
		}
		return nil, err
	}
	defer f.Close()
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		k, v, ok := strings.Cut(sc.Text(), "=")
		if ok {
			s[strings.TrimSpace(k)] = strings.TrimSpace(v)
		}
	}
	return s, sc.Err()
}
EOF_3
cat > README.md <<'EOF_4'
<div align="center">

[![Go](https://github.com/acme/confy/actions/workflows/ci.yml/badge.svg)](https://github.com/acme/confy/actions/workflows/ci.yml)
[![Go Reference](https://pkg.go.dev/badge/github.com/acme/confy.svg)](https://pkg.go.dev/github.com/acme/confy)
[![Go Version](https://img.shields.io/github/go-mod/go-version/acme/confy)](go.mod)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Go Report Card](https://goreportcard.com/badge/github.com/acme/confy)](https://goreportcard.com/report/github.com/acme/confy)
[![Build Status](https://travis-ci.org/acme/confy.svg?branch=master)](https://travis-ci.org/acme/confy)
[![codecov](https://codecov.io/gh/acme/confy/branch/master/graph/badge.svg)](https://codecov.io/gh/acme/confy)
[![Docker Pulls](https://img.shields.io/docker/pulls/acme/confy.svg)](https://hub.docker.com/r/acme/confy)
[![Stars](https://img.shields.io/github/stars/acme/confy.svg)](https://github.com/acme/confy/stargazers)

# 🚀 confy

Layered configuration for Go services.

</div>

## 📖 Overview

confy reads layered settings from env files, command-line flags, and compiled-in defaults, in that order of precedence.

## ✨ Features

- 🗂️ Env-file layer
- 🚩 Flag layer
- 🧱 Defaults layer

## 📦 Installation

```shell
go get github.com/acme/confy
```

## 🛠️ Usage

```go
s, err := confy.Load(".env", map[string]string{"port": "9090"}, map[string]string{"port": "8080"})
if err != nil {
	log.Fatal(err)
}
fmt.Println(s["port"])
```

<details>
<summary>📝 Precedence details</summary>

The env file wins over flags, and flags win over defaults.

</details>
EOF_4
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
git remote add origin https://github.com/acme/confy.git
git add -A
git commit -q -m 'chore: initial import'
