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
	"strings"
)

// ErrMissing is returned when a key has no value.
var ErrMissing = errors.New("must: missing key")

// Options configures Load.
type Options struct {
	Dir    string // Directory holding the settings file.
	Ext    string // Settings file extension.
	Strict bool   // Fail on malformed lines.
}

// Source holds loaded settings.
type Source struct {
	vals map[string]string
}

// Load reads the settings file in opts.Dir with extension opts.Ext.
func Load(opts Options) *Source {
	src := &Source{vals: map[string]string{}}
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
	}
	return src
}

// Value returns the value of key, or ErrMissing when it is unset.
func Value(src *Source, key string) (string, error) {
	v, ok := src.vals[key]
	if !ok {
		return "", ErrMissing
	}
	return v, nil
}
EOF_2
mkdir -p config
cat > config/server.go <<'EOF_3'
// Package config loads the application settings.
package config

import "example.com/must"

// Settings maps setting names to values.
type Settings map[string]string

// Server returns the server settings.
func Server() (Settings, error) {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})

	host, err := must.Value(src, "SERVER_HOST")
	if err != nil {
		host = "localhost"
	}

	port, err := must.Value(src, "SERVER_PORT")
	if err != nil {
		port = "8080"
	}

	token, err := must.Value(src, "SERVER_TOKEN")
	if err != nil {
		return nil, err
	}
	return Settings{"host": host, "port": port, "token": token}, nil
}

// Admin returns the admin settings.
func Admin() (Settings, error) {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})

	addr, err := must.Value(src, "ADMIN_ADDR")
	if err != nil {
		addr = "127.0.0.1:9000"
	}

	user, err := must.Value(src, "ADMIN_USER")
	if err != nil {
		user = "admin"
	}

	theme, err := must.Value(src, "ADMIN_THEME")
	if err != nil {
		theme = "light"
	}
	return Settings{"addr": addr, "user": user, "theme": theme}, nil
}

// TLS returns the tls settings.
func TLS() (Settings, error) {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})

	cert, err := must.Value(src, "TLS_CERT")
	if err != nil {
		cert = "cert.pem"
	}

	key, err := must.Value(src, "TLS_KEY")
	if err != nil {
		key = "key.pem"
	}
	return Settings{"cert": cert, "key": key}, nil
}
EOF_3
mkdir -p config
cat > config/store.go <<'EOF_4'
package config

import "example.com/must"

// Database returns the database settings.
func Database() (Settings, error) {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})

	dsn, err := must.Value(src, "DB_DSN")
	if err != nil {
		return nil, err
	}

	pool, err := must.Value(src, "DB_POOL")
	if err != nil {
		pool = "10"
	}

	timeout, err := must.Value(src, "DB_TIMEOUT")
	if err != nil {
		timeout = "5s"
	}
	return Settings{"dsn": dsn, "pool": pool, "timeout": timeout}, nil
}

// Cache returns the cache settings.
func Cache() (Settings, error) {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})

	addr, err := must.Value(src, "CACHE_ADDR")
	if err != nil {
		addr = "localhost:6379"
	}

	ttl, err := must.Value(src, "CACHE_TTL")
	if err != nil {
		ttl = "60s"
	}

	prefix, err := must.Value(src, "CACHE_PREFIX")
	if err != nil {
		prefix = "app:"
	}
	return Settings{"addr": addr, "ttl": ttl, "prefix": prefix}, nil
}

// Queue returns the queue settings.
func Queue() (Settings, error) {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})

	url, err := must.Value(src, "QUEUE_URL")
	if err != nil {
		return nil, err
	}

	workers, err := must.Value(src, "QUEUE_WORKERS")
	if err != nil {
		workers = "4"
	}

	retry, err := must.Value(src, "QUEUE_RETRY")
	if err != nil {
		retry = "3"
	}
	return Settings{"url": url, "workers": workers, "retry": retry}, nil
}
EOF_4
mkdir -p config
cat > config/notify.go <<'EOF_5'
package config

import "example.com/must"

// Mail returns the mail settings.
func Mail() (Settings, error) {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})

	host, err := must.Value(src, "MAIL_HOST")
	if err != nil {
		host = "smtp.local"
	}

	from, err := must.Value(src, "MAIL_FROM")
	if err != nil {
		from = "noreply@example.com"
	}

	pass, err := must.Value(src, "MAIL_PASS")
	if err != nil {
		return nil, err
	}
	return Settings{"host": host, "from": from, "pass": pass}, nil
}

// Slack returns the slack settings.
func Slack() (Settings, error) {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})

	hook, err := must.Value(src, "SLACK_HOOK")
	if err != nil {
		return nil, err
	}

	channel, err := must.Value(src, "SLACK_CHANNEL")
	if err != nil {
		channel = "#ops"
	}

	name, err := must.Value(src, "SLACK_NAME")
	if err != nil {
		name = "bot"
	}
	return Settings{"hook": hook, "channel": channel, "name": name}, nil
}

// Pager returns the pager settings.
func Pager() (Settings, error) {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})

	key, err := must.Value(src, "PAGER_KEY")
	if err != nil {
		key = "none"
	}

	level, err := must.Value(src, "PAGER_LEVEL")
	if err != nil {
		level = "warn"
	}
	return Settings{"key": key, "level": level}, nil
}
EOF_5
mkdir -p config
cat > config/observe.go <<'EOF_6'
package config

import "example.com/must"

// Logging returns the logging settings.
func Logging() (Settings, error) {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})

	level, err := must.Value(src, "LOG_LEVEL")
	if err != nil {
		level = "info"
	}

	format, err := must.Value(src, "LOG_FORMAT")
	if err != nil {
		format = "json"
	}

	file, err := must.Value(src, "LOG_FILE")
	if err != nil {
		file = "app.log"
	}
	return Settings{"level": level, "format": format, "file": file}, nil
}

// Metrics returns the metrics settings.
func Metrics() (Settings, error) {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})

	addr, err := must.Value(src, "METRICS_ADDR")
	if err != nil {
		addr = ":9100"
	}

	path, err := must.Value(src, "METRICS_PATH")
	if err != nil {
		path = "/metrics"
	}

	ns, err := must.Value(src, "METRICS_NS")
	if err != nil {
		return nil, err
	}
	return Settings{"addr": addr, "path": path, "ns": ns}, nil
}

// Tracing returns the tracing settings.
func Tracing() (Settings, error) {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})

	url, err := must.Value(src, "TRACE_URL")
	if err != nil {
		url = "http://localhost:4318"
	}

	rate, err := must.Value(src, "TRACE_RATE")
	if err != nil {
		rate = "0.1"
	}

	svc, err := must.Value(src, "TRACE_SERVICE")
	if err != nil {
		svc = "app"
	}
	return Settings{"url": url, "rate": rate, "svc": svc}, nil
}
EOF_6
