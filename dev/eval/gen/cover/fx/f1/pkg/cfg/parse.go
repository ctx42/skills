// Package cfg parses key=value configuration lines.
package cfg

import (
	"errors"
	"fmt"
	"strings"
)

// ErrEmpty is returned for an empty line.
var ErrEmpty = errors.New("empty line")

// Config is one parsed key=value pair.
type Config struct {
	Key   string
	Value string
}

// Parse parses a "key=value" line.
func Parse(s string) (Config, error) {
	if s == "" {
		return Config{}, ErrEmpty
	}
	k, v, ok := strings.Cut(s, "=")
	if !ok {
		return Config{}, fmt.Errorf("missing '=' in %q", s)
	}
	return Config{Key: k, Value: v}, nil
}

// Load parses a line read from a file, trimming surrounding space.
func Load(line string) (Config, error) {
	cfg, err := Parse(strings.TrimSpace(line))
	if err != nil {
		return Config{}, fmt.Errorf("load: %w", err)
	}
	return cfg, nil
}
