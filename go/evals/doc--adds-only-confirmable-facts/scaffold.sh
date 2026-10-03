#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module example.com/archive

go 1.22
EOF_0
mkdir -p archive
cat > archive/archive.go <<'EOF_1'
// Package archive keeps records in ID order.
package archive

import "sort"

// Record is one archived entry.
type Record struct {
	ID   int
	Body string
}

// Archive holds records.
type Archive struct {
	items []Record
}

// Store adds recs to the archive.
func (arc *Archive) Store(recs []Record) {
	sort.Slice(recs, func(i, j int) bool { return recs[i].ID < recs[j].ID })
	arc.items = append(arc.items, recs...)
}

// Len returns the number of archived records.
func (arc *Archive) Len() int {
	return len(arc.items)
}
EOF_1
