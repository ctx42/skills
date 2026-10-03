#!/usr/bin/env bash
set -euo pipefail
cat > .gitignore <<'EOF_0'
tmp/
EOF_0
cat > go.mod <<'EOF_1'
module example.com/evalmod

go 1.22
EOF_1
mkdir -p pkg/net
cat > pkg/net/dial.go <<'EOF_2'
// Package net opens TCP connections to configured endpoints.
package net

import (
	"errors"
	"fmt"
	stdnet "net"
	"time"
)

// ErrNoAddr is returned when the address is empty.
var ErrNoAddr = errors.New("no address")

// Dialer opens network connections.
type Dialer interface {
	Dial(network, address string) (stdnet.Conn, error)
}

// dialer is the Dialer used by Dial.
var dialer Dialer = &stdnet.Dialer{Timeout: 5 * time.Second}

// Dial opens a TCP connection to addr, given as "host:port".
func Dial(addr string) (stdnet.Conn, error) {
	if addr == "" {
		return nil, ErrNoAddr
	}
	host, port, err := stdnet.SplitHostPort(addr)
	if err != nil {
		return nil, fmt.Errorf("bad address %q: %w", addr, err)
	}
	hp := stdnet.JoinHostPort(host, port)
	if hp == "" {
		return nil, errors.New("empty host:port")
	}
	conn, err := dialer.Dial("tcp", hp)
	if err != nil {
		return nil, fmt.Errorf("dial %s: %w", hp, err)
	}
	return conn, nil
}

// MustDial is like Dial but panics when addr is empty or not a valid
// "host:port" address, or when the connection cannot be opened.
func MustDial(addr string) stdnet.Conn {
	conn, err := Dial(addr)
	if err != nil {
		panic(err)
	}
	return conn
}
EOF_2
cat > pkg/net/dial_test.go <<'EOF_3'
package net

import (
	"errors"
	"testing"
)

func Test_Dial_emptyAddress(t *testing.T) {
	// --- Given ---
	addr := ""

	// --- When ---
	have, err := Dial(addr)

	// --- Then ---
	if !errors.Is(err, ErrNoAddr) {
		t.Errorf("want ErrNoAddr, have %v", err)
	}
	if have != nil {
		t.Errorf("want nil conn, have %v", have)
	}
}
EOF_3
cat > pkg/net/retry.go <<'EOF_4'
package net

import "time"

// Retry calls fn up to n times and returns nil on the first success. Between
// attempts it waits 100ms. It returns the last error when every attempt fails.
func Retry(n int, fn func() error) error {
	var err error
	for i := 0; i < n; i++ {
		if err = fn(); err == nil {
			return nil
		}
		if i < n-1 {
			time.Sleep(100 * time.Millisecond)
		}
	}
	return err
}
EOF_4
cat > pkg/net/retry_test.go <<'EOF_5'
package net

import "testing"

func Test_Retry_firstTry(t *testing.T) {
	// --- Given ---
	calls := 0
	fn := func() error { calls++; return nil }

	// --- When ---
	err := Retry(3, fn)

	// --- Then ---
	if err != nil {
		t.Errorf("want nil error, have %v", err)
	}
	if calls != 1 {
		t.Errorf("want 1 call, have %d", calls)
	}
}
EOF_5
