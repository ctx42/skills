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
