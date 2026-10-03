#!/usr/bin/env bash
set -euo pipefail
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
cat > go.mod <<'EOF_0'
module example.com/demo

go 1.22
EOF_0
mkdir -p pkg/foo
cat > pkg/foo/foo.go <<'EOF_1'
// Package foo computes statistics over integer samples.
package foo

import "errors"

// ErrEmpty is returned when a statistic needs at least one sample.
var ErrEmpty = errors.New("no samples")

// Series holds integer samples in arrival order.
type Series struct {
	vals []int
}

// Add appends v to the series.
func (s *Series) Add(v int) {
	s.vals = append(s.vals, v)
}

// Max returns the largest sample.
func (s *Series) Max() int {
	m := s.vals[0]
	for _, v := range s.vals[1:] {
		if v > m {
			m = v
		}
	}
	return m
}

// Mean returns the arithmetic mean of the samples.
func (s *Series) Mean() (float64, error) {
	if len(s.vals) == 0 {
		return 0, ErrEmpty
	}
	sum := 0
	for _, v := range s.vals {
		sum += v
	}
	return float64(sum) / float64(len(s.vals)), nil
}
EOF_1
git add -A
git commit -qm 'initial'
