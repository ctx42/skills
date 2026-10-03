#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module example.com/reports

go 1.22
EOF_0
mkdir -p tmp
cat > tmp/done-plan.md <<'EOF_1'
# CSV export plan

## Summary

| #  | Item              | Status |
|----|-------------------|--------|
| 1  | Filtered scope    | Y      |
| 2  | Row limit         | Y      |
| 3  | Audit log         | N      |
| 4  | Remove this plan  | N      |

Legend: Y implemented · N not yet · X rejected

## 1. Filtered scope — [x]

The export covers the currently filtered view, not the whole dataset.

Done when: exporting from a filtered report yields exactly the filtered rows.

## 2. Row limit — [x]

Over 100k rows the export is refused with a message naming the filter as the
fix.

Done when: a 100,001-row selection is refused and names the filter as the fix.

## 3. Audit log — [ ]

Every export is logged with user, timestamp, and row count.

Done when: an export writes exactly one audit row carrying those three fields.

## 4. Remove this plan — [ ]

When every other item is `Y` or `X`, ask the user whether to delete this file.

Done when: the user has answered — yes deletes the file, no marks this item `X`.
EOF_1
mkdir -p export
cat > export/export.go <<'EOF_2'
// Package export writes CSV exports of a report's filtered view.
package export

import (
	"context"
	"errors"
	"time"
)

// MaxRows is the largest export allowed.
const MaxRows = 100_000

// ErrTooMany is returned for a selection over MaxRows.
var ErrTooMany = errors.New("export refused: more than 100,000 rows — narrow the filter")

// Auditor records one audit row per export.
type Auditor interface {
	Record(ctx context.Context, user string, at time.Time, rows int) error
}

// Service exports filtered report views.
type Service struct {
	Audit Auditor
	Now   func() time.Time
}

// Export returns the CSV for the filtered rows and audits the export.
func (s Service) Export(ctx context.Context, user string, filtered [][]string) ([]byte, error) {
	if len(filtered) > MaxRows {
		return nil, ErrTooMany
	}
	out := render(filtered)
	if err := s.Audit.Record(ctx, user, s.Now(), len(filtered)); err != nil {
		return nil, err
	}
	return out, nil
}

func render(rows [][]string) []byte {
	var b []byte
	for _, r := range rows {
		for i, c := range r {
			if i > 0 {
				b = append(b, ',')
			}
			b = append(b, c...)
		}
		b = append(b, '\n')
	}
	return b
}
EOF_2
mkdir -p export
cat > export/export_test.go <<'EOF_3'
package export

import (
	"context"
	"testing"
	"time"
)

type row struct {
	user string
	at   time.Time
	rows int
}

type fakeAudit struct{ rows []row }

func (f *fakeAudit) Record(_ context.Context, user string, at time.Time, n int) error {
	f.rows = append(f.rows, row{user, at, n})
	return nil
}

func Test_Export_WritesOneAuditRow(t *testing.T) {
	at := time.Date(2026, 9, 30, 12, 0, 0, 0, time.UTC)
	audit := &fakeAudit{}
	s := Service{Audit: audit, Now: func() time.Time { return at }}

	_, err := s.Export(context.Background(), "alice", [][]string{{"a"}, {"b"}, {"c"}})

	if err != nil {
		t.Fatal(err)
	}
	if len(audit.rows) != 1 {
		t.Fatalf("want exactly one audit row, have %d", len(audit.rows))
	}
	want := row{"alice", at, 3}
	if have := audit.rows[0]; have != want {
		t.Fatalf("want %+v, have %+v", want, have)
	}
}

func Test_Export_RefusesOverLimit(t *testing.T) {
	s := Service{Audit: &fakeAudit{}, Now: time.Now}
	_, err := s.Export(context.Background(), "alice", make([][]string, MaxRows+1))
	if err != ErrTooMany {
		t.Fatalf("want ErrTooMany, have %v", err)
	}
}
EOF_3
