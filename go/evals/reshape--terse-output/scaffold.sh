#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module example.com/app

go 1.22

require example.com/must v0.0.0

replace example.com/must => ./third_party/must
EOF_0
mkdir -p third_party/must
cat > third_party/must/go.mod <<'EOF_1'
module example.com/must

go 1.22
EOF_1
mkdir -p third_party/must
cat > third_party/must/must.go <<'EOF_2'
// Package must reads settings from env-style files.
package must

import (
	"errors"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

// Options configures Load.
type Options struct {
	Dir    string // Directory holding the settings file.
	Ext    string // Settings file extension.
	Strict bool   // Fail on malformed lines.
}

// Source holds loaded settings.
type Source struct {
	vals map[string]string
	raw  map[string]any
}

// Load reads the settings file in opts.Dir with extension opts.Ext.
func Load(opts Options) *Source {
	src := &Source{vals: map[string]string{}, raw: map[string]any{}}
	data, err := os.ReadFile(filepath.Join(opts.Dir, "settings"+opts.Ext))
	if err != nil {
		return src
	}
	for _, line := range strings.Split(string(data), "\n") {
		k, v, ok := strings.Cut(line, "=")
		if !ok {
			continue
		}
		src.vals[strings.TrimSpace(k)] = strings.TrimSpace(v)
		src.raw[strings.TrimSpace(k)] = strings.TrimSpace(v)
	}
	return src
}

// Value returns the value of key.
func (s *Source) Value(key string) (string, error) {
	v, ok := s.vals[key]
	if !ok {
		return "", errors.New("must: missing key " + key)
	}
	return v, nil
}

// Lookup returns the value of key, whether it is set, and a parse error.
func (s *Source) Lookup(key string) (string, bool, error) {
	v, ok := s.vals[key]
	return v, ok, nil
}

// Raw returns the parsed value of key.
func (s *Source) Raw(key string) any { return s.raw[key] }

// Cursor walks the keys of a Source.
type Cursor struct {
	keys []string
	i    int
}

// Keys returns a cursor positioned before the first key.
func (s *Source) Keys() *Cursor {
	c := &Cursor{i: -1}
	for k := range s.vals {
		c.keys = append(c.keys, k)
	}
	sort.Strings(c.keys)
	return c
}

// Next advances the cursor and reports whether a key is available.
func (c *Cursor) Next() bool {
	c.i++
	return c.i < len(c.keys)
}

// Key returns the current key.
func (c *Cursor) Key() string { return c.keys[c.i] }

// Watch polls key every interval and calls onChange when its value changes,
// giving up after retries failed reads.
func Watch(s *Source, key string, interval time.Duration, retries int, onChange func(string)) error {
	last, _ := s.Value(key)
	fails := 0
	for fails < retries {
		time.Sleep(interval)
		v, err := s.Value(key)
		if err != nil {
			fails++
			continue
		}
		if v != last {
			onChange(v)
			last = v
		}
	}
	return errors.New("must: watch gave up on " + key)
}
EOF_2
mkdir -p app
cat > app/server.go <<'EOF_3'
// Package app wires the service from its settings.
package app

import (
	"strings"
	"time"

	"example.com/must"
)

// valuer is the part of must.Source the app reads from.
type valuer interface {
	Value(key string) (string, error)
}

// Server holds the HTTP server settings.
type Server struct {
	Host    string
	Port    int
	Workers int
}

// LoadServer reads the server settings.
func LoadServer() Server {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})
	host, err := src.Value("HOST")
	if err != nil {
		host = "localhost"
	}
	port, _ := src.Raw("PORT").(int)
	workers, _ := src.Raw("WORKERS").(int)
	return Server{Host: host, Port: port, Workers: workers}
}

// Mode returns the run mode, defaulting to "prod" when unset.
func Mode(v valuer) string {
	mode, err := v.Value("MODE")
	if err != nil && strings.Contains(err.Error(), "missing key") {
		return "prod"
	}
	return mode
}

// WatchMode reports run-mode changes to onChange.
func WatchMode(onChange func(string)) error {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})
	return must.Watch(src, "MODE", time.Second, 3, onChange)
}
EOF_3
mkdir -p app
cat > app/store.go <<'EOF_4'
package app

import (
	"strings"
	"time"

	"example.com/must"
)

// Store holds the database settings.
type Store struct {
	DSN     string
	Pool    int
	Replica string
}

// LoadStore reads the database settings.
func LoadStore() (Store, error) {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})
	dsn, err := src.Value("DB_DSN")
	if err != nil {
		if strings.Contains(err.Error(), "missing key") {
			dsn = "postgres://localhost/app"
		} else {
			return Store{}, err
		}
	}
	pool, _ := src.Raw("DB_POOL").(int)
	replica, ok, err := src.Lookup("DB_REPLICA")
	if err != nil {
		return Store{}, err
	}
	if !ok {
		replica = dsn
	}
	return Store{DSN: dsn, Pool: pool, Replica: replica}, nil
}

// WatchDSN reports DSN changes to onChange.
func WatchDSN(onChange func(string)) error {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})
	return must.Watch(src, "DB_DSN", time.Second, 3, onChange)
}
EOF_4
mkdir -p app
cat > app/dump.go <<'EOF_5'
package app

import (
	"fmt"
	"strings"

	"example.com/must"
)

// Dump renders every setting as KEY=VALUE lines.
func Dump() string {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})
	var b strings.Builder
	keys := src.Keys()
	for keys.Next() {
		v, err := src.Value(keys.Key())
		if err != nil {
			continue
		}
		fmt.Fprintf(&b, "%s=%s\n", keys.Key(), v)
	}
	return b.String()
}

// Prefixed returns the keys that start with prefix.
func Prefixed(prefix string) []string {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})
	var out []string
	keys := src.Keys()
	for keys.Next() {
		if strings.HasPrefix(keys.Key(), prefix) {
			out = append(out, keys.Key())
		}
	}
	return out
}

// Timeout returns the request timeout in seconds.
func Timeout() int {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})
	t, _ := src.Raw("TIMEOUT").(int)
	if t == 0 {
		t = 30
	}
	return t
}
EOF_5
mkdir -p app
cat > app/app_test.go <<'EOF_6'
package app

import "testing"

type fakeValuer struct {
	vals map[string]string
	err  error
}

func (f fakeValuer) Value(key string) (string, error) {
	if f.err != nil {
		return "", f.err
	}
	return f.vals[key], nil
}

func Test_Mode(t *testing.T) {
	t.Run("set", func(t *testing.T) {
		// --- Given ---
		v := fakeValuer{vals: map[string]string{"MODE": "dev"}}

		// --- When ---
		have := Mode(v)

		// --- Then ---
		if have != "dev" {
			t.Errorf("have %q, want %q", have, "dev")
		}
	})
}
EOF_6
mkdir -p internal/feed
cat > internal/feed/feed.go <<'EOF_7'
// Package feed polls the upstream feeds named in the settings.
package feed

import (
	"time"

	"example.com/must"
)

// valuer is the part of must.Source the feed reads from.
type valuer interface {
	Value(key string) (string, error)
}

// URLs returns the feed URLs, one per FEED_* key.
func URLs() []string {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})
	var urls []string
	keys := src.Keys()
	for keys.Next() {
		u, err := src.Value(keys.Key())
		if err != nil {
			continue
		}
		urls = append(urls, u)
	}
	return urls
}

// Interval returns the poll interval read from v.
func Interval(v valuer) time.Duration {
	s, err := v.Value("FEED_INTERVAL")
	if err != nil {
		s = "1m"
	}
	d, err := time.ParseDuration(s)
	if err != nil {
		return time.Minute
	}
	return d
}

// Agent returns the user agent, falling back to a fixed name.
func Agent() string {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})
	agent, ok, err := src.Lookup("FEED_AGENT")
	if err != nil || !ok {
		agent = "feedbot"
	}
	return agent
}

// WatchURLs reports feed list changes to onChange.
func WatchURLs(onChange func(string)) error {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})
	return must.Watch(src, "FEED_URLS", time.Second, 3, onChange)
}
EOF_7
mkdir -p internal/feed
cat > internal/feed/feed_test.go <<'EOF_8'
package feed

import (
	"errors"
	"testing"
	"time"
)

type stubValuer map[string]string

func (s stubValuer) Value(key string) (string, error) {
	v, ok := s[key]
	if !ok {
		return "", errors.New("must: missing key " + key)
	}
	return v, nil
}

func Test_Interval(t *testing.T) {
	t.Run("default", func(t *testing.T) {
		// --- Given ---
		v := stubValuer{}

		// --- When ---
		have := Interval(v)

		// --- Then ---
		if have != time.Minute {
			t.Errorf("have %v, want %v", have, time.Minute)
		}
	})
}
EOF_8
