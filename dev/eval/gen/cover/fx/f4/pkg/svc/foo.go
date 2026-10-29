// Package svc loads and stores service settings.
package svc

import (
	"errors"
	"fmt"
	"strconv"
	"strings"
)

// ErrNoPort is returned when a settings line carries no port.
var ErrNoPort = errors.New("no port")

// Settings are the parsed service settings.
type Settings struct {
	Host string
	Port int
}

// Addr returns the "host:port" form of s.
func Addr(s Settings) string {
	return s.Host + ":" + strconv.Itoa(s.Port)
}

// Valid reports whether s has a host and a port in range.
func Valid(s Settings) bool {
	if s.Host == "" {
		return false
	}
	return s.Port > 0 && s.Port < 65536
}

// Load parses a "host:port" settings line.
func Load(line string) (Settings, error) {
	host, port, ok := strings.Cut(line, ":")
	if !ok {
		return Settings{}, ErrNoPort
	}
	n, err := strconv.Atoi(port)
	if err != nil {
		return Settings{}, fmt.Errorf("bad port %q: %w", port, err)
	}
	if n <= 0 || n > 65535 {
		return Settings{}, fmt.Errorf("port %d out of range", n)
	}
	return Settings{Host: host, Port: n}, nil
}

// Store renders s as a settings line.
func Store(s Settings) string {
	return Addr(s)
}
