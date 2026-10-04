#!/usr/bin/env python3
"""Generate craft/evals/readme-smith--* native eval cases."""
import os
import shutil
import textwrap

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
EVALS = os.path.join(ROOT, "craft/evals")
HERE = os.path.dirname(os.path.abspath(__file__))

ENGLISH = "The user writes English; reply in English."
PERSONA = """Automated eval: the user is absent. Whenever the skill would stop and wait
for the user, take the next scripted answer below as the reply and continue
in this same run; never end the run to wait. If none fits, give the most
plausible answer and continue.
Before taking a scripted answer, write out in full, as your reply text, the
message you would send the user at that point."""
PERSONA_GATE = """Automated eval: the user is absent. Only the answers below are scripted.
Whenever the skill would stop and wait for the user, take the next scripted
answer below as the reply and continue in this same run. Once the scripted
answers are used up, at the next point where the skill would wait for the
user, end the run there: that message is your final reply."""

TOOLS = ("[Read, Glob, Grep, Skill, Write, Edit, Bash(go:*), Bash(gomake:*), "
         "Bash(make:*), Bash(git:*), Bash(ls:*)]")

T = ["skill:readme-smith", "sec:readme-smith:usage",
     "sec:readme-smith:non-negotiables-both-modes", "sec:readme-smith:verify",
     "sec:readme-smith:self-learning", "ref:readme-smith/template"]
CREATE = T + ["sec:readme-smith:create-mode"]
IMPROVE = T + ["sec:readme-smith:improve-mode"]
GOMAKE = ["sec:readme-smith:go-example-injection-gomake", "ref:readme-smith/gomake"]

# ---------------------------------------------------------------- fixtures

PNG = ("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGA"
       "hKmMIQAAAABJRU5ErkJggg==")

CI_PLAIN = """name: ci
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
"""

CI_GOMAKE = """name: ci
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
"""


def portcheck(go_directive=True, editorconfig=True, bench_comment=False):
    files = {}
    files["go.mod"] = "module github.com/acme/portcheck\n" + ("\ngo 1.22\n" if go_directive else "")
    files["cmd/portcheck/main.go"] = '''// Command portcheck reports which host:port targets accept TCP connections.
package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"time"

	"github.com/acme/portcheck/internal/scan"
)

func main() {
	timeout := flag.Duration("timeout", 2*time.Second, "per-target dial timeout")
	asJSON := flag.Bool("json", false, "print one JSON object per target")
	concurrency := flag.Int("concurrency", 64, "maximum simultaneous dials")
	flag.Usage = func() {
		fmt.Fprintln(os.Stderr, "usage: portcheck [flags] host:port...")
		flag.PrintDefaults()
	}
	flag.Parse()
	if flag.NArg() == 0 {
		flag.Usage()
		os.Exit(2)
	}

	results := scan.Check(context.Background(), flag.Args(), *timeout, *concurrency)
	failed := false
	for _, r := range results {
		if !r.Open {
			failed = true
		}
		if *asJSON {
			_ = json.NewEncoder(os.Stdout).Encode(r)
			continue
		}
		state := "open"
		if !r.Open {
			state = "closed: " + r.Err
		}
		fmt.Printf("%-24s %s (%s)\\n", r.Target, state, r.Took.Round(time.Millisecond))
	}
	if failed {
		os.Exit(1)
	}
}
'''
    bench = ("// Throughput: feels like ~10k ports/s on a laptop; never measured,\n"
             "// there is no benchmark yet.\n") if bench_comment else ""
    files["internal/scan/scan.go"] = '''// Package scan dials host:port targets concurrently.
package scan

import (
	"context"
	"net"
	"sync"
	"time"
)

// Result is the outcome of dialing one target.
type Result struct {
	Target string        `json:"target"`
	Open   bool          `json:"open"`
	Err    string        `json:"error,omitempty"`
	Took   time.Duration `json:"took_ns"`
}

// Check dials every target over TCP with at most concurrency dials in flight
// and returns one Result per target, in input order.
''' + bench + '''func Check(ctx context.Context, targets []string, timeout time.Duration, concurrency int) []Result {
	if concurrency < 1 {
		concurrency = 1
	}
	out := make([]Result, len(targets))
	sem := make(chan struct{}, concurrency)
	var wg sync.WaitGroup
	for i, t := range targets {
		wg.Add(1)
		sem <- struct{}{}
		go func(i int, t string) {
			defer wg.Done()
			defer func() { <-sem }()
			start := time.Now()
			d := net.Dialer{Timeout: timeout}
			conn, err := d.DialContext(ctx, "tcp", t)
			r := Result{Target: t, Took: time.Since(start)}
			if err != nil {
				r.Err = err.Error()
			} else {
				r.Open = true
				_ = conn.Close()
			}
			out[i] = r
		}(i, t)
	}
	wg.Wait()
	return out
}
'''
    files[".github/workflows/ci.yml"] = CI_PLAIN
    files["@assets/logo.png"] = PNG
    if editorconfig:
        files[".editorconfig"] = """root = true

[*]
end_of_line = lf
insert_final_newline = true

[*.go]
indent_style = tab

[*.md]
max_line_length = 100
"""
    return files


def kit_store(gomake=False, member_variant="audit"):
    files = {}
    files["go.mod"] = "module github.com/acme/kit\n\ngo 1.22\n"
    files["LICENSE"] = """MIT License

Copyright (c) 2026 Acme

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, subject to the following conditions:
the above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
"""
    files["CONTRIBUTING.md"] = """# Contributing

1. Fork the repository and create a topic branch.
2. Run `go test ./...` before you push.
3. Sign off every commit (`git commit -s`).
4. Open a pull request against `master`.
"""
    files[".github/workflows/ci.yml"] = CI_GOMAKE if gomake else CI_PLAIN
    files["README.md"] = """[![Go](https://github.com/acme/kit/actions/workflows/ci.yml/badge.svg)](https://github.com/acme/kit/actions/workflows/ci.yml)
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
"""
    files["pkg/cache/cache.go"] = '''// Package cache is an in-memory cache whose entries expire after a TTL.
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
'''
    files["pkg/cache/README.md"] = """# cache

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
"""
    files["pkg/store/store.go"] = '''// Package store is an embedded key-value store that keeps one append-only log
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
		k, v, ok := strings.Cut(sc.Text(), "\\t")
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
	line := key + "\\t" + base64.StdEncoding.EncodeToString(val) + "\\n"
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
'''
    if member_variant == "audit":
        files["pkg/store/README.md"] = """[![Go](https://github.com/acme/kit/actions/workflows/ci.yml/badge.svg)](https://github.com/acme/kit/actions/workflows/ci.yml)
[![Go Reference](https://pkg.go.dev/badge/github.com/acme/kit/pkg/store.svg)](https://pkg.go.dev/github.com/acme/kit/pkg/store)

# store

[Overview](#overview) • [Installation](#installation) • [Usage](#usage)

Embedded key-value store for Go services that keeps one append-only log per
directory.

## Overview

`store` replays its log into memory on `Open`, so reads never touch the disk.

## Installation

```
go get github.com/acme/kit
```

## Using the store

```
s, err := store.Open("data")
if err != nil {
	log.Fatal(err)
}
defer s.Close()
_ = s.Put("user:42", []byte("Ada"))
```

## Contributing

1. Fork the repository and create a topic branch.
2. Run `go test ./...` before you push.
3. Sign off every commit (`git commit -s`).
4. Open a pull request against `master`.

## License

MIT License

Copyright (c) 2026 Acme

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, subject to the following conditions.
"""
    else:  # declined-go-source-gate: README-only findings + a broken go snippet
        files["pkg/store/README.md"] = """# store

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
"""
    files["@git"] = "https://github.com/acme/kit.git"
    return files


def httpc():
    files = {}
    files["go.mod"] = "module github.com/acme/httpc\n\ngo 1.22\n"
    files[".github/workflows/ci.yml"] = CI_GOMAKE
    files["LICENSE"] = "MIT License\n\nCopyright (c) 2026 Acme\n"
    files["client.go"] = '''// Package httpc is a small HTTP client that resolves request paths against a
// base URL.
package httpc

import (
	"context"
	"io"
	"net/http"
	"strings"
)

// Client sends requests to paths below one base URL.
type Client struct {
	base string
	hc   *http.Client
}

// New returns a Client for base, e.g. "https://api.example.com/v1".
func New(base string) *Client {
	return &Client{base: strings.TrimRight(base, "/"), hc: http.DefaultClient}
}

// Response is a fully read HTTP response.
type Response struct {
	Status int
	Body   string
}

// Do sends a request with method to path below the base URL and reads the
// whole response body.
func (c *Client) Do(ctx context.Context, method, path string) (*Response, error) {
	req, err := http.NewRequestWithContext(ctx, method, c.base+"/"+strings.TrimLeft(path, "/"), nil)
	if err != nil {
		return nil, err
	}
	res, err := c.hc.Do(req)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	b, err := io.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}
	return &Response{Status: res.StatusCode, Body: string(b)}, nil
}
'''
    files["header.go"] = '''package httpc

import (
	"fmt"
	"strings"
)

// Header maps canonical header names to values.
type Header map[string]string

// Parse parses "Name: value" lines into a Header. Blank lines are skipped.
func Parse(raw string) (Header, error) {
	h := Header{}
	for _, line := range strings.Split(raw, "\\n") {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		k, v, ok := strings.Cut(line, ":")
		if !ok {
			return nil, fmt.Errorf("httpc: malformed header line %q", line)
		}
		h[strings.TrimSpace(k)] = strings.TrimSpace(v)
	}
	return h, nil
}
'''
    files["client_test.go"] = '''package httpc

import "testing"

func TestParse(t *testing.T) {
	h, err := Parse("Accept: text/plain\\n\\nX-Id: 7")
	if err != nil {
		t.Fatal(err)
	}
	if h["Accept"] != "text/plain" || h["X-Id"] != "7" {
		t.Fatalf("unexpected header %v", h)
	}
}
'''
    files["@git"] = "https://github.com/acme/httpc.git"
    return files


def confy():
    files = {}
    files["go.mod"] = "module github.com/acme/confy\n\ngo 1.22\n"
    files["LICENSE"] = "MIT License\n\nCopyright (c) 2026 Acme\n"
    files[".github/workflows/ci.yml"] = CI_PLAIN
    files["confy.go"] = '''// Package confy loads layered settings: env files, then flags, then defaults.
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
'''
    files["README.md"] = """<div align="center">

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
"""
    files["@git"] = "https://github.com/acme/confy.git"
    return files


def foo_bitbucket():
    files = {}
    files["go.mod"] = "module bitbucket.org/acme/foo\n\ngo 1.22\n"
    files["pkg/foo/queue.go"] = '''// Package foo is an in-process job queue with bounded capacity, retries with
// backoff, and drain-on-shutdown.
package foo

import (
	"context"
	"errors"
	"sync"
	"time"
)

// ErrFull is returned by Push when the queue is at capacity.
var ErrFull = errors.New("foo: queue full")

// ErrClosed is returned by Push after Drain has been called.
var ErrClosed = errors.New("foo: queue closed")

// Job is a unit of work. A Job that returns an error is retried.
type Job func(ctx context.Context) error

// Option configures a Queue.
type Option func(*Queue)

// WithCapacity bounds how many jobs may wait; the default is 128.
func WithCapacity(n int) Option { return func(q *Queue) { q.capacity = n } }

// WithWorkers sets how many jobs run at once; the default is 4.
func WithWorkers(n int) Option { return func(q *Queue) { q.workers = n } }

// WithRetry sets the attempts per job and the base backoff, doubled after each
// failure; the default is 3 attempts from 100ms.
func WithRetry(attempts int, base time.Duration) Option {
	return func(q *Queue) { q.attempts, q.backoff = attempts, base }
}

// Stats reports queue counters.
type Stats struct {
	Pending   int
	Succeeded int
	Failed    int
	Retried   int
}

// Queue runs Jobs on a fixed pool of workers.
type Queue struct {
	capacity, workers, attempts int
	backoff                     time.Duration

	mu     sync.Mutex
	jobs   chan Job
	closed bool
	stats  Stats
	wg     sync.WaitGroup
}

// New starts a Queue with its workers running.
func New(opts ...Option) *Queue {
	q := &Queue{capacity: 128, workers: 4, attempts: 3, backoff: 100 * time.Millisecond}
	for _, o := range opts {
		o(q)
	}
	q.jobs = make(chan Job, q.capacity)
	for i := 0; i < q.workers; i++ {
		q.wg.Add(1)
		go q.work()
	}
	return q
}

// Push enqueues job without blocking.
func (q *Queue) Push(job Job) error {
	q.mu.Lock()
	defer q.mu.Unlock()
	if q.closed {
		return ErrClosed
	}
	select {
	case q.jobs <- job:
		q.stats.Pending++
		return nil
	default:
		return ErrFull
	}
}

// Stats returns a snapshot of the counters.
func (q *Queue) Stats() Stats {
	q.mu.Lock()
	defer q.mu.Unlock()
	return q.stats
}

// Drain stops accepting jobs and waits until queued jobs finish or ctx ends.
func (q *Queue) Drain(ctx context.Context) error {
	q.mu.Lock()
	if !q.closed {
		q.closed = true
		close(q.jobs)
	}
	q.mu.Unlock()
	done := make(chan struct{})
	go func() { q.wg.Wait(); close(done) }()
	select {
	case <-done:
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

func (q *Queue) work() {
	defer q.wg.Done()
	for job := range q.jobs {
		q.run(job)
	}
}

func (q *Queue) run(job Job) {
	wait := q.backoff
	for i := 0; i < q.attempts; i++ {
		if err := job(context.Background()); err == nil {
			q.count(func(s *Stats) { s.Pending--; s.Succeeded++ })
			return
		}
		if i < q.attempts-1 {
			q.count(func(s *Stats) { s.Retried++ })
			time.Sleep(wait)
			wait *= 2
		}
	}
	q.count(func(s *Stats) { s.Pending--; s.Failed++ })
}

func (q *Queue) count(f func(*Stats)) {
	q.mu.Lock()
	f(&q.stats)
	q.mu.Unlock()
}
'''
    files["pkg/foo/queue_test.go"] = '''package foo

import (
	"context"
	"testing"
)

func TestQueueRunsJob(t *testing.T) {
	q := New(WithWorkers(1))
	ran := make(chan struct{})
	if err := q.Push(func(context.Context) error { close(ran); return nil }); err != nil {
		t.Fatal(err)
	}
	<-ran
	if err := q.Drain(context.Background()); err != nil {
		t.Fatal(err)
	}
}
'''
    files["@git"] = "git@bitbucket.org:acme/foo.git"
    return files


def wiretap():
    files = {}
    files["go.mod"] = "module github.com/acme/wiretap\n\ngo 1.22\n"
    files[".github/workflows/ci.yml"] = CI_GOMAKE
    files["LICENSE"] = "MIT License\n\nCopyright (c) 2026 Acme\n"
    files["wiretap.go"] = open(os.path.join(HERE, "wire/wiretap.go")).read()
    files["example_test.go"] = open(os.path.join(HERE, "wire/example_test.go")).read()
    files["@git"] = "https://github.com/acme/wiretap.git"
    return files


def linecount():
    files = {}
    files["go.mod"] = "module github.com/acme/linecount\n\ngo 1.22\n"
    files[".github/workflows/ci.yml"] = CI_PLAIN
    files["LICENSE"] = "MIT License\n\nCopyright (c) 2026 Acme\n"
    files["cmd/linecount/main.go"] = '''// Command linecount prints the number of non-blank lines in each file.
package main

import (
	"flag"
	"fmt"
	"os"

	"github.com/acme/linecount/internal/count"
)

func main() {
	all := flag.Bool("all", false, "count blank lines too")
	flag.Parse()
	for _, name := range flag.Args() {
		n, err := count.File(name, *all)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		fmt.Printf("%8d %s\\n", n, name)
	}
}
'''
    files["internal/count/count.go"] = '''// Package count counts lines.
package count

import (
	"bufio"
	"os"
	"strings"
)

// File returns the number of lines in name, skipping blank ones unless all.
func File(name string, all bool) (int, error) {
	f, err := os.Open(name)
	if err != nil {
		return 0, err
	}
	defer f.Close()
	n := 0
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		if all || strings.TrimSpace(sc.Text()) != "" {
			n++
		}
	}
	return n, sc.Err()
}
'''
    files["internal/count/count_test.go"] = '''package count

import (
	"os"
	"path/filepath"
	"testing"
)

func TestFile(t *testing.T) {
	p := filepath.Join(t.TempDir(), "a.txt")
	if err := os.WriteFile(p, []byte("a\\n\\nb\\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	n, err := File(p, false)
	if err != nil || n != 2 {
		t.Fatalf("File = %d, %v; want 2", n, err)
	}
}
'''
    files["@git"] = "https://github.com/acme/linecount.git"
    return files


def tally():
    files = {}
    files["go.mod"] = "module github.com/acme/tally\n\ngo 1.22\n"
    files[".github/workflows/ci.yml"] = CI_PLAIN
    files["LICENSE"] = "MIT License\n\nCopyright (c) 2026 Acme\n"
    files["cmd/tally/main.go"] = '''// Command tally prints count, sum, min, and max of every numeric CSV column.
package main

import (
	"encoding/csv"
	"fmt"
	"math"
	"os"
	"strconv"
)

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintln(os.Stderr, "usage: tally file.csv")
		os.Exit(2)
	}
	f, err := os.Open(os.Args[1])
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	defer f.Close()
	rows, err := csv.NewReader(f).ReadAll()
	if err != nil || len(rows) == 0 {
		fmt.Fprintln(os.Stderr, "tally: no rows")
		os.Exit(1)
	}
	for c, name := range rows[0] {
		n, sum, lo, hi := 0, 0.0, math.Inf(1), math.Inf(-1)
		for _, r := range rows[1:] {
			v, err := strconv.ParseFloat(r[c], 64)
			if err != nil {
				continue
			}
			n++
			sum += v
			lo, hi = math.Min(lo, v), math.Max(hi, v)
		}
		if n > 0 {
			fmt.Printf("%-10s count=%d sum=%g min=%g max=%g\\n", name, n, sum, lo, hi)
		}
	}
}
'''
    files["Makefile"] = """.PHONY: demo test

# demo generates sample data with the Zig generator, then tallies it.
demo:
	zig run tools/gen.zig > testdata/sample.csv
	go run ./cmd/tally testdata/sample.csv

test:
	go test ./...
"""
    files["tools/gen.zig"] = '''const std = @import("std");

pub fn main() !void {
    const out = std.io.getStdOut().writer();
    try out.print("region,orders,revenue\\n", .{});
    var i: u32 = 1;
    while (i <= 5) : (i += 1) {
        try out.print("r{d},{d},{d}.50\\n", .{ i, i * 3, i * 120 });
    }
}
'''
    files["testdata/.gitkeep"] = ""
    files["HACKING.md"] = """# Hacking on tally

The quickstart demo (`make demo`) needs Zig 0.13 on PATH: `tools/gen.zig`
generates the sample CSV that `go run ./cmd/tally` then summarizes. Go alone
builds and tests the CLI (`go test ./...`).
"""
    files["RELEASING.md"] = """# Releasing

tally is not published yet. The repository at github.com/acme/tally is still
private and has no tag; it goes public with the first tag, v0.1.0, after the
security review. Until then `go install github.com/acme/tally/cmd/tally@latest`
fails for everyone outside the team.
"""
    files["@git"] = "https://github.com/acme/tally.git"
    return files


# ---------------------------------------------------------------- writers


def scaffold(files):
    out = ["#!/usr/bin/env bash", "set -euo pipefail"]
    n = 0
    for path, body in files.items():
        if path == "@git":
            continue
        if path.startswith("@"):
            p = path[1:]
            d = os.path.dirname(p)
            if d:
                out.append(f"mkdir -p {d}")
            out.append(f"printf '%s' '{body}' | base64 -d > {p}")
            continue
        d = os.path.dirname(path)
        if d:
            out.append(f"mkdir -p {d}")
        tag = f"EOF_{n}"
        n += 1
        if body == "":
            out.append(f": > {path}")
            continue
        out.append(f"cat > {path} <<'{tag}'")
        out.append(body.rstrip("\n"))
        out.append(tag)
    if "@git" in files:
        out += ["git init -q", "git config user.email eval@example.com",
                "git config user.name Eval", "git config commit.gpgsign false",
                f"git remote add origin {files['@git']}",
                "git add -A", "git commit -q -m 'chore: initial import'"]
    return "\n".join(out) + "\n"


def g_regex(pattern, target="last_message", flags=None, match=None):
    h = ["---", "type: regex"]
    if target == "last_message":
        h.append("target: last_message")
    else:
        h.append(f"target: {{source: file, path: {target}}}")
    if match:
        h.append(f'match: "{match}"')
    if flags:
        h.append(f'flags: "{flags}"')
    h.append("---")
    return "\n".join(h) + "\n" + pattern + "\n"


def g_tool(tool, input_match=None, mn=None, mx=None, arm=None):
    h = ["---", "type: tool_used", f"tool: {tool}"]
    if input_match:
        h.append(f"input_match: '{input_match}'")
    if mn is not None:
        h.append(f"min: {mn}")
    if mx is not None:
        h.append(f"max: {mx}")
    if arm:
        h.append(f"arm: {arm}")
    h.append("---")
    return "\n".join(h) + "\n"


def g_never(tool, input_match=None):
    return g_tool(tool, input_match, 0, 0, "both")


def g_read_before_readme(path_re):
    """The file was read (Read, or a Bash cat/sed with a shell) before any
    README.md Write; tool_order can't take two tools on one side."""
    return ("---\ntype: regex\ntarget: trace\n---\n"
            r'^(?:(?!"name":"Write","input":\{"file_path":"[^"]*README\.md")[\s\S])*?'
            r'"name":"(?:Read|Bash)","input":\{"(?:file_path|command)":"(?:[^"\\]|\\.)*?'
            + path_re + "\n")


def case(name, tags, query, files, graders, answers=None, gate_answers=None,
         max_turns=60, timeout=300, tools=TOOLS):
    d = os.path.join(EVALS, name)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, "graders"))
    asp = [ENGLISH]
    if answers is not None:
        asp += [PERSONA, ""] + answers
    elif gate_answers is not None:
        asp += [PERSONA_GATE, ""] + gate_answers
    body = "\n".join(asp)
    prompt = ["---",
              f"tags: [case:{name}, " + ", ".join(tags) + "]",
              "runs: 1",
              f"max_turns: {max_turns}",
              f"timeout_seconds: {timeout}",
              f"allowed_tools: {tools}",
              "append_system_prompt: |",
              textwrap.indent(body, "  "),
              "---", "", query, ""]
    open(os.path.join(d, "prompt.md"), "w").write("\n".join(prompt))
    open(os.path.join(d, "case.yaml"), "w").write(
        f'schema_version: "1.1"\nname: {name}\ncontext:\n  scaffold_script: scaffold.sh\n')
    sp = os.path.join(d, "scaffold.sh")
    open(sp, "w").write(scaffold(files))
    os.chmod(sp, 0o755)
    for gname, content in graders.items():
        open(os.path.join(d, "graders", gname + ".md"), "w").write(content)


R = "README.md"
SHELL = ["needs-shell"]

POS_PORTCHECK = ("1. Positioning: portcheck is for SREs and on-call engineers who must\n"
                 "   confirm, before a deploy, that every host:port a service depends on\n"
                 "   accepts connections. Lead with concurrent dials, the per-target\n"
                 "   timeout, and JSON output for scripts. No roadmap to mention.")


def main():
    pfx = "readme-smith--"

    # 1 create-from-scan ------------------------------------------------
    f = portcheck()
    case(pfx + "create-from-scan", CREATE + SHELL, "/craft:readme-smith write a README for this project", f, {
        "b1-reads-gomod-first": g_read_before_readme(r"go\.mod"),
        "b1-reads-main-first": g_read_before_readme(r"cmd/portcheck/main\.go"),
        "b1-reads-ci-first": g_read_before_readme(r"\.github/workflows/ci\.yml"),
        "b1-logo-used": g_regex(r"^# [^\n]*\n[\s\S]*?!\[[^\]\n]*\]\((\./)?assets/logo\.png\)[\s\S]*?^## ", R, "m"),
        "b3-blueprint-order": g_regex(r"^## Features[\s\S]*?^## Install(ation)?\b[\s\S]*?^## Usage[\s\S]*?^##+ (Configuration|Flags|Options)", R, "m"),
        "b3-module-path": g_regex(r"github\.com/acme/portcheck", R),
        "b3-real-flags": g_regex(r"^(?=[\s\S]*-timeout\b)(?=[\s\S]*-json\b)(?=[\s\S]*-concurrency\b)", R),
        "b3-real-defaults": g_regex(r"^(?=[\s\S]*\b2s\b)(?=[\s\S]*\b64\b)", R),
        "b3-no-invented-flags": g_regex(r"(^|[\s`])--?(verbose|retries|retry|format|output|quiet|ports?)\b", R, match="not_contains"),
        "b4-runs-commands": g_tool("Bash", r"go (build|install|run)\b", 1),
        "b5-uses-100-cols": g_regex(r"^[A-Za-z`*][^\n]{80,99}$", R, "m"),
        "b5-not-past-100": g_regex(r"^[A-Za-z`*][^\n]{100,}$", R, "m", "not_contains"),
    }, answers=[POS_PORTCHECK])

    # 3 improve-member-readme -------------------------------------------
    f = kit_store()
    M = "pkg/store/README.md"
    case(pfx + "improve-member-readme", IMPROVE + SHELL, "/craft:readme-smith improve pkg/store/README.md", f, {
        "b4-no-badges": g_regex(r"^\[!\[", M, "m", "not_contains"),
        "b4-no-license": g_regex(r"^##+ License", M, "m", "not_contains"),
        "b4-no-contributing": g_regex(r"^##+ Contributing", M, "m", "not_contains"),
        "b4-fences-have-language": g_regex(r"\n\n```[ \t]*\n", M, match="not_contains"),
        "b4-anchor-resolves": g_regex(r"^(?![\s\S]*\(#usage\))|\n## Usage[ \t]*(\n|$)", M),
        "b4-states-what-changed": g_regex(r"pkg/store/README\.md"),
    }, answers=["1. Approved. Apply all the findings.",
                "2. To any other question: \"No, leave it.\""])

    # 4 gomake-example-injection ----------------------------------------
    f = httpc()
    POS_HTTPC = ("1. Positioning: httpc is for Go developers who call one JSON API from\n"
                 "   many places and want paths resolved against a single base URL.\n"
                 "   Lead with base-URL resolution and fully read responses. No roadmap.")
    case(pfx + "gomake-example-injection", CREATE + GOMAKE + SHELL, "/craft:readme-smith write a README", f, {
        # By Write or by a shell cp: either way the file ends up holding it.
        "b3-writes-example-func": g_regex(r"func Example", "example_test.go"),
        "b3-runs-go-test": g_tool("Bash", r"go test", 1),
        "b4-marker-above-go-fence": g_regex(r"<!-- gmmce:(\./)?Example\w+ -->\n```go\n", R),
        "b4-runs-mce": g_tool("Bash", r"gomake[^\n]*:doc:mce", 1),
        "b5-names-found-keys": g_regex(r"^(?=[\s\S]*\bExampleParse\b)(?=[\s\S]*\bExample(New|Client_Do|Client)\b)"),
        "b6-no-hand-filled-fence-write": g_never("Write", r"gmmce:.{0,80}?-->\\n```go\\n(?!```)"),
        "b6-no-hand-filled-fence-edit": g_never("Edit", r"gmmce:.{0,80}?-->\\n```go\\n(?!```)"),
        "b6-no-hand-written-fence": g_regex(r"<!-- gmmce:[^\n]*-->\n```go\n(?:(?!```)[^\n]*\n)*?[ \t]*(package |func |import )", R, match="not_contains"),
    }, answers=[POS_HTTPC, "2. Yes, create those example files."])

    f = kit_store(gomake=True, member_variant="declined")


if __name__ == "__main__":
    main()
