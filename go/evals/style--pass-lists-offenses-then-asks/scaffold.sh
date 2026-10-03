#!/usr/bin/env bash
set -euo pipefail
mkdir -p pkg/foo
cat > go.mod <<'EOF_GO_MOD'
module example.com/foo

go 1.26
EOF_GO_MOD
cat > pkg/foo/foo.go <<'EOF_PKG_FOO_FOO_GO'
// Package foo keeps running totals of integer samples.
package foo

import "fmt"

var _ fmt.Stringer = (*Counter)(nil)

// Counter sums the samples added to it.
type Counter struct {
	samples []int
}

// Add appends n to the samples.
func (c *Counter) Add(n int) {
	c.samples = append(c.samples, n)
}

// Sum returns the total of the first k samples.
func (c *Counter) Sum(k int) int {
	total := 0
	for i := 0; i <= k; i++ {
		total += c.samples[i]
	}
	return total
}

// String returns a string representation of the value. It is the
// method the fmt.Stringer interface requires, used by fmt to print
// the value.
func (c *Counter) String() string {
	return fmt.Sprintf("Counter(%d samples)", len(c.samples))
}
EOF_PKG_FOO_FOO_GO
