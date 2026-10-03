#!/usr/bin/env bash
set -euo pipefail
mkdir -p internal/alpha internal/bravo internal/charlie internal/delta internal/echo internal/foxtrot internal/golf internal/hotel
cat > go.mod <<'EOF_GO_MOD'
module example.com/shop

go 1.26

require github.com/ctx42/testing v0.56.0
EOF_GO_MOD
cat > go.sum <<'EOF_GO_SUM'
github.com/ctx42/testing v0.56.0 h1:+yZwRy+5JQb+14YtRTGJxWbAMAP9qlU9pMa8TPqgdzE=
github.com/ctx42/testing v0.56.0/go.mod h1:wRBqNRtlxDZnXIjgCX3zr05Acl6JC1D6cSBN2IpaMIs=
EOF_GO_SUM
cat > internal/alpha/alpha.go <<'EOF_INTERNAL_ALPHA_ALPHA_GO'
// Package alpha parses key-value records.
package alpha

import (
	"fmt"
	"strconv"
	"strings"
)

// Record is one key-value pair.
type Record struct {
	Key   string
	Value int
}

// Pair returns the record in the form "key=value".
func (rec Record) Pair() string {
	return rec.Key + "=" + strconv.Itoa(rec.Value)
}

// Add adds n to the record's value and returns the new value.
func (rec *Record) Add(n int) int {
	rec.Value += n
	return rec.Value
}

// Parse parses s in the form "key=value".
func Parse(s string) (Record, error) {
	key, raw, _ := strings.Cut(s, "=")
	val, err := strconv.Atoi(raw)
	if err != nil {
		return Record{}, fmt.Errorf("parse value: %w", err)
	}
	return Record{Key: key, Value: val}, nil
}

// Split parses every sep-separated record in s.
func Split(s, sep string) ([]Record, error) {
	var recs []Record
	for i, part := range strings.Split(s, sep) {
		rec, err := Parse(part)
		if err != nil {
			return nil, fmt.Errorf("record %d: %w", i, err)
		}
		recs = append(recs, rec)
	}
	return recs, nil
}
EOF_INTERNAL_ALPHA_ALPHA_GO
cat > internal/alpha/alpha_test.go <<'EOF_INTERNAL_ALPHA_ALPHA_TEST_GO'
package alpha

import (
	"testing"

	"github.com/ctx42/testing/pkg/assert"
)

func Test_Record_Pair(t *testing.T) {
	// --- Given ---
	rec := Record{Key: "a", Value: 1}

	// --- When ---
	have := rec.Pair()

	// --- Then ---
	assert.Equal(t, "a=1", have)
}

func Test_Record_Add(t *testing.T) {
	// --- Given ---
	rec := &Record{Key: "a", Value: 1}

	n := 2

	// --- When ---
	have := rec.Add(n)

	// --- Then ---
	assert.Equal(t, 3, have)

	assert.Equal(t, 3, rec.Value)
}

func Test_Parse(t *testing.T) {
	t.Run("valid", func(t *testing.T) {
		// --- Given ---
		s := "a=1"

		// --- When ---
		have, err := Parse(s)

		// --- Then ---
		assert.NoError(t, err)
		assert.Equal(t, Record{Key: "a", Value: 1}, have)
	})

	t.Run("error - value not a number", func(t *testing.T) {
		// --- Given ---
		s := "a=x"

		// --- When ---
		have, err := Parse(s)

		// --- Then ---
		assert.ErrorContain(t, "invalid syntax", err)
		assert.Zero(t, have)
	})
}

func Test_Split(t *testing.T) {
	t.Run("valid", func(t *testing.T) {
		// --- Given ---
		s := "a=1"
		sep := ";"

		// --- When ---
		have, err := Split(s, sep)

		// --- Then ---
		assert.NoError(t, err)
		assert.Equal(t, []Record{{Key: "a", Value: 1}}, have)
	})

	t.Run("error - bad record", func(t *testing.T) {
		// --- Given ---
		s := "a=1;b=x"
		sep := ";"

		// --- When ---
		have, err := Split(s, sep)

		// --- Then ---
		assert.ErrorContain(t, "invalid syntax", err)
		assert.Nil(t, have)
	})
}
EOF_INTERNAL_ALPHA_ALPHA_TEST_GO
cat > internal/bravo/bravo.go <<'EOF_INTERNAL_BRAVO_BRAVO_GO'
// Package bravo parses key-value records.
package bravo

import (
	"fmt"
	"strconv"
	"strings"
)

// Record is one key-value pair.
type Record struct {
	Key   string
	Value int
}

// Pair returns the record in the form "key=value".
func (rec Record) Pair() string {
	return rec.Key + "=" + strconv.Itoa(rec.Value)
}

// Add adds n to the record's value and returns the new value.
func (rec *Record) Add(n int) int {
	rec.Value += n
	return rec.Value
}

// Parse parses s in the form "key=value".
func Parse(s string) (Record, error) {
	key, raw, _ := strings.Cut(s, "=")
	val, err := strconv.Atoi(raw)
	if err != nil {
		return Record{}, fmt.Errorf("parse value: %w", err)
	}
	return Record{Key: key, Value: val}, nil
}

// Split parses every sep-separated record in s.
func Split(s, sep string) ([]Record, error) {
	var recs []Record
	for i, part := range strings.Split(s, sep) {
		rec, err := Parse(part)
		if err != nil {
			return nil, fmt.Errorf("record %d: %w", i, err)
		}
		recs = append(recs, rec)
	}
	return recs, nil
}
EOF_INTERNAL_BRAVO_BRAVO_GO
cat > internal/bravo/bravo_test.go <<'EOF_INTERNAL_BRAVO_BRAVO_TEST_GO'
package bravo

import (
	"testing"

	"github.com/ctx42/testing/pkg/assert"
)

func Test_Record_Pair(t *testing.T) {
	// --- Given ---
	rec := Record{Key: "a", Value: 1}

	// --- When ---
	have := rec.Pair()

	// --- Then ---
	assert.Equal(t, "a=1", have)
}

func Test_Record_Add(t *testing.T) {
	// --- Given ---
	rec := &Record{Key: "a", Value: 1}

	n := 2

	// --- When ---
	have := rec.Add(n)

	// --- Then ---
	assert.Equal(t, 3, have)

	assert.Equal(t, 3, rec.Value)
}

func Test_Parse(t *testing.T) {
	t.Run("valid", func(t *testing.T) {
		// --- Given ---
		s := "a=1"

		// --- When ---
		have, err := Parse(s)

		// --- Then ---
		assert.NoError(t, err)
		assert.Equal(t, Record{Key: "a", Value: 1}, have)
	})

	t.Run("error - value not a number", func(t *testing.T) {
		// --- Given ---
		s := "a=x"

		// --- When ---
		have, err := Parse(s)

		// --- Then ---
		assert.ErrorContain(t, "invalid syntax", err)
		assert.Zero(t, have)
	})
}

func Test_Split(t *testing.T) {
	t.Run("valid", func(t *testing.T) {
		// --- Given ---
		s := "a=1"
		sep := ";"

		// --- When ---
		have, err := Split(s, sep)

		// --- Then ---
		assert.NoError(t, err)
		assert.Equal(t, []Record{{Key: "a", Value: 1}}, have)
	})

	t.Run("error - bad record", func(t *testing.T) {
		// --- Given ---
		s := "a=1;b=x"
		sep := ";"

		// --- When ---
		have, err := Split(s, sep)

		// --- Then ---
		assert.ErrorContain(t, "invalid syntax", err)
		assert.Nil(t, have)
	})
}
EOF_INTERNAL_BRAVO_BRAVO_TEST_GO
cat > internal/charlie/charlie.go <<'EOF_INTERNAL_CHARLIE_CHARLIE_GO'
// Package charlie parses key-value records.
package charlie

import (
	"fmt"
	"strconv"
	"strings"
)

// Record is one key-value pair.
type Record struct {
	Key   string
	Value int
}

// Pair returns the record in the form "key=value".
func (rec Record) Pair() string {
	return rec.Key + "=" + strconv.Itoa(rec.Value)
}

// Add adds n to the record's value and returns the new value.
func (rec *Record) Add(n int) int {
	rec.Value += n
	return rec.Value
}

// Parse parses s in the form "key=value".
func Parse(s string) (Record, error) {
	key, raw, _ := strings.Cut(s, "=")
	val, err := strconv.Atoi(raw)
	if err != nil {
		return Record{}, fmt.Errorf("parse value: %w", err)
	}
	return Record{Key: key, Value: val}, nil
}

// Split parses every sep-separated record in s.
func Split(s, sep string) ([]Record, error) {
	var recs []Record
	for i, part := range strings.Split(s, sep) {
		rec, err := Parse(part)
		if err != nil {
			return nil, fmt.Errorf("record %d: %w", i, err)
		}
		recs = append(recs, rec)
	}
	return recs, nil
}
EOF_INTERNAL_CHARLIE_CHARLIE_GO
cat > internal/charlie/charlie_test.go <<'EOF_INTERNAL_CHARLIE_CHARLIE_TEST_GO'
package charlie

import (
	"testing"

	"github.com/ctx42/testing/pkg/assert"
)

func Test_Record_Pair(t *testing.T) {
	// --- Given ---
	rec := Record{Key: "a", Value: 1}

	// --- When ---
	have := rec.Pair()

	// --- Then ---
	assert.Equal(t, "a=1", have)
}

func Test_Record_Add(t *testing.T) {
	// --- Given ---
	rec := &Record{Key: "a", Value: 1}

	n := 2

	// --- When ---
	have := rec.Add(n)

	// --- Then ---
	assert.Equal(t, 3, have)

	assert.Equal(t, 3, rec.Value)
}

func Test_Parse(t *testing.T) {
	t.Run("valid", func(t *testing.T) {
		// --- Given ---
		s := "a=1"

		// --- When ---
		have, err := Parse(s)

		// --- Then ---
		assert.NoError(t, err)
		assert.Equal(t, Record{Key: "a", Value: 1}, have)
	})

	t.Run("error - value not a number", func(t *testing.T) {
		// --- Given ---
		s := "a=x"

		// --- When ---
		have, err := Parse(s)

		// --- Then ---
		assert.ErrorContain(t, "invalid syntax", err)
		assert.Zero(t, have)
	})
}

func Test_Split(t *testing.T) {
	t.Run("valid", func(t *testing.T) {
		// --- Given ---
		s := "a=1"
		sep := ";"

		// --- When ---
		have, err := Split(s, sep)

		// --- Then ---
		assert.NoError(t, err)
		assert.Equal(t, []Record{{Key: "a", Value: 1}}, have)
	})

	t.Run("error - bad record", func(t *testing.T) {
		// --- Given ---
		s := "a=1;b=x"
		sep := ";"

		// --- When ---
		have, err := Split(s, sep)

		// --- Then ---
		assert.ErrorContain(t, "invalid syntax", err)
		assert.Nil(t, have)
	})
}
EOF_INTERNAL_CHARLIE_CHARLIE_TEST_GO
cat > internal/delta/delta.go <<'EOF_INTERNAL_DELTA_DELTA_GO'
// Package delta parses key-value records.
package delta

import (
	"fmt"
	"strconv"
	"strings"
)

// Record is one key-value pair.
type Record struct {
	Key   string
	Value int
}

// Pair returns the record in the form "key=value".
func (rec Record) Pair() string {
	return rec.Key + "=" + strconv.Itoa(rec.Value)
}

// Add adds n to the record's value and returns the new value.
func (rec *Record) Add(n int) int {
	rec.Value += n
	return rec.Value
}

// Parse parses s in the form "key=value".
func Parse(s string) (Record, error) {
	key, raw, _ := strings.Cut(s, "=")
	val, err := strconv.Atoi(raw)
	if err != nil {
		return Record{}, fmt.Errorf("parse value: %w", err)
	}
	return Record{Key: key, Value: val}, nil
}

// Split parses every sep-separated record in s.
func Split(s, sep string) ([]Record, error) {
	var recs []Record
	for i, part := range strings.Split(s, sep) {
		rec, err := Parse(part)
		if err != nil {
			return nil, fmt.Errorf("record %d: %w", i, err)
		}
		recs = append(recs, rec)
	}
	return recs, nil
}
EOF_INTERNAL_DELTA_DELTA_GO
cat > internal/delta/delta_test.go <<'EOF_INTERNAL_DELTA_DELTA_TEST_GO'
package delta

import (
	"testing"

	"github.com/ctx42/testing/pkg/assert"
)

func Test_Record_Pair(t *testing.T) {
	// --- Given ---
	rec := Record{Key: "a", Value: 1}

	// --- When ---
	have := rec.Pair()

	// --- Then ---
	assert.Equal(t, "a=1", have)
}

func Test_Record_Add(t *testing.T) {
	// --- Given ---
	rec := &Record{Key: "a", Value: 1}

	n := 2

	// --- When ---
	have := rec.Add(n)

	// --- Then ---
	assert.Equal(t, 3, have)

	assert.Equal(t, 3, rec.Value)
}

func Test_Parse(t *testing.T) {
	t.Run("valid", func(t *testing.T) {
		// --- Given ---
		s := "a=1"

		// --- When ---
		have, err := Parse(s)

		// --- Then ---
		assert.NoError(t, err)
		assert.Equal(t, Record{Key: "a", Value: 1}, have)
	})

	t.Run("error - value not a number", func(t *testing.T) {
		// --- Given ---
		s := "a=x"

		// --- When ---
		have, err := Parse(s)

		// --- Then ---
		assert.ErrorContain(t, "invalid syntax", err)
		assert.Zero(t, have)
	})
}

func Test_Split(t *testing.T) {
	t.Run("valid", func(t *testing.T) {
		// --- Given ---
		s := "a=1"
		sep := ";"

		// --- When ---
		have, err := Split(s, sep)

		// --- Then ---
		assert.NoError(t, err)
		assert.Equal(t, []Record{{Key: "a", Value: 1}}, have)
	})

	t.Run("error - bad record", func(t *testing.T) {
		// --- Given ---
		s := "a=1;b=x"
		sep := ";"

		// --- When ---
		have, err := Split(s, sep)

		// --- Then ---
		assert.ErrorContain(t, "invalid syntax", err)
		assert.Nil(t, have)
	})
}
EOF_INTERNAL_DELTA_DELTA_TEST_GO
cat > internal/echo/echo.go <<'EOF_INTERNAL_ECHO_ECHO_GO'
// Package echo parses key-value records.
package echo

import (
	"fmt"
	"strconv"
	"strings"
)

// Record is one key-value pair.
type Record struct {
	Key   string
	Value int
}

// Pair returns the record in the form "key=value".
func (rec Record) Pair() string {
	return rec.Key + "=" + strconv.Itoa(rec.Value)
}

// Add adds n to the record's value and returns the new value.
func (rec *Record) Add(n int) int {
	rec.Value += n
	return rec.Value
}

// Parse parses s in the form "key=value".
func Parse(s string) (Record, error) {
	key, raw, _ := strings.Cut(s, "=")
	val, err := strconv.Atoi(raw)
	if err != nil {
		return Record{}, fmt.Errorf("parse value: %w", err)
	}
	return Record{Key: key, Value: val}, nil
}

// Split parses every sep-separated record in s.
func Split(s, sep string) ([]Record, error) {
	var recs []Record
	for i, part := range strings.Split(s, sep) {
		rec, err := Parse(part)
		if err != nil {
			return nil, fmt.Errorf("record %d: %w", i, err)
		}
		recs = append(recs, rec)
	}
	return recs, nil
}
EOF_INTERNAL_ECHO_ECHO_GO
cat > internal/echo/echo_test.go <<'EOF_INTERNAL_ECHO_ECHO_TEST_GO'
package echo

import (
	"testing"

	"github.com/ctx42/testing/pkg/assert"
)

func Test_Record_Pair(t *testing.T) {
	// --- Given ---
	rec := Record{Key: "a", Value: 1}

	// --- When ---
	have := rec.Pair()

	// --- Then ---
	assert.Equal(t, "a=1", have)
}

func Test_Record_Add(t *testing.T) {
	// --- Given ---
	rec := &Record{Key: "a", Value: 1}

	n := 2

	// --- When ---
	have := rec.Add(n)

	// --- Then ---
	assert.Equal(t, 3, have)

	assert.Equal(t, 3, rec.Value)
}

func Test_Parse(t *testing.T) {
	t.Run("valid", func(t *testing.T) {
		// --- Given ---
		s := "a=1"

		// --- When ---
		have, err := Parse(s)

		// --- Then ---
		assert.NoError(t, err)
		assert.Equal(t, Record{Key: "a", Value: 1}, have)
	})

	t.Run("error - value not a number", func(t *testing.T) {
		// --- Given ---
		s := "a=x"

		// --- When ---
		have, err := Parse(s)

		// --- Then ---
		assert.ErrorContain(t, "invalid syntax", err)
		assert.Zero(t, have)
	})
}

func Test_Split(t *testing.T) {
	t.Run("valid", func(t *testing.T) {
		// --- Given ---
		s := "a=1"

		sep := ";"

		// --- When ---
		have, err := Split(s, sep)

		// --- Then ---
		assert.NoError(t, err)

		assert.Equal(t, []Record{{Key: "a", Value: 1}}, have)
	})

	t.Run("error - bad record", func(t *testing.T) {
		// --- Given ---
		s := "a=1;b=x"

		sep := ";"

		// --- When ---
		have, err := Split(s, sep)

		// --- Then ---
		assert.ErrorContain(t, "invalid syntax", err)
		assert.Nil(t, have)
	})
}
EOF_INTERNAL_ECHO_ECHO_TEST_GO
cat > internal/foxtrot/foxtrot.go <<'EOF_INTERNAL_FOXTROT_FOXTROT_GO'
// Package foxtrot parses key-value records.
package foxtrot

import (
	"fmt"
	"strconv"
	"strings"
)

// Record is one key-value pair.
type Record struct {
	Key   string
	Value int
}

// Pair returns the record in the form "key=value".
func (rec Record) Pair() string {
	return rec.Key + "=" + strconv.Itoa(rec.Value)
}

// Add adds n to the record's value and returns the new value.
func (rec *Record) Add(n int) int {
	rec.Value += n
	return rec.Value
}

// Parse parses s in the form "key=value".
func Parse(s string) (Record, error) {
	key, raw, _ := strings.Cut(s, "=")
	val, err := strconv.Atoi(raw)
	if err != nil {
		return Record{}, fmt.Errorf("parse value: %w", err)
	}
	return Record{Key: key, Value: val}, nil
}

// Split parses every sep-separated record in s.
func Split(s, sep string) ([]Record, error) {
	var recs []Record
	for i, part := range strings.Split(s, sep) {
		rec, err := Parse(part)
		if err != nil {
			return nil, fmt.Errorf("record %d: %w", i, err)
		}
		recs = append(recs, rec)
	}
	return recs, nil
}
EOF_INTERNAL_FOXTROT_FOXTROT_GO
cat > internal/foxtrot/foxtrot_test.go <<'EOF_INTERNAL_FOXTROT_FOXTROT_TEST_GO'
package foxtrot

import (
	"testing"

	"github.com/ctx42/testing/pkg/assert"
)

func Test_Record_Pair(t *testing.T) {
	// --- Given ---
	rec := Record{Key: "a", Value: 1}

	// --- When ---
	have := rec.Pair()

	// --- Then ---
	assert.Equal(t, "a=1", have)
}

func Test_Record_Add(t *testing.T) {
	// --- Given ---
	rec := &Record{Key: "a", Value: 1}

	n := 2

	// --- When ---
	have := rec.Add(n)

	// --- Then ---
	assert.Equal(t, 3, have)

	assert.Equal(t, 3, rec.Value)
}

func Test_Parse(t *testing.T) {
	t.Run("valid", func(t *testing.T) {
		// --- Given ---
		s := "a=1"

		// --- When ---
		have, err := Parse(s)

		// --- Then ---
		assert.NoError(t, err)
		assert.Equal(t, Record{Key: "a", Value: 1}, have)
	})

	t.Run("error - value not a number", func(t *testing.T) {
		// --- Given ---
		s := "a=x"

		// --- When ---
		have, err := Parse(s)

		// --- Then ---
		assert.ErrorContain(t, "invalid syntax", err)
		assert.Zero(t, have)
	})
}

func Test_Split(t *testing.T) {
	t.Run("valid", func(t *testing.T) {
		// --- Given ---
		s := "a=1"

		sep := ";"

		// --- When ---
		have, err := Split(s, sep)

		// --- Then ---
		assert.NoError(t, err)

		assert.Equal(t, []Record{{Key: "a", Value: 1}}, have)
	})

	t.Run("error - bad record", func(t *testing.T) {
		// --- Given ---
		s := "a=1;b=x"

		sep := ";"

		// --- When ---
		have, err := Split(s, sep)

		// --- Then ---
		assert.ErrorContain(t, "invalid syntax", err)
		assert.Nil(t, have)
	})
}
EOF_INTERNAL_FOXTROT_FOXTROT_TEST_GO
cat > internal/golf/golf.go <<'EOF_INTERNAL_GOLF_GOLF_GO'
// Package golf parses key-value records.
package golf

import (
	"fmt"
	"strconv"
	"strings"
)

// Record is one key-value pair.
type Record struct {
	Key   string
	Value int
}

// Pair returns the record in the form "key=value".
func (rec Record) Pair() string {
	return rec.Key + "=" + strconv.Itoa(rec.Value)
}

// Add adds n to the record's value and returns the new value.
func (rec *Record) Add(n int) int {
	rec.Value += n
	return rec.Value
}

// Parse parses s in the form "key=value".
func Parse(s string) (Record, error) {
	key, raw, _ := strings.Cut(s, "=")
	val, err := strconv.Atoi(raw)
	if err != nil {
		return Record{}, fmt.Errorf("parse value: %w", err)
	}
	return Record{Key: key, Value: val}, nil
}

// Split parses every sep-separated record in s.
func Split(s, sep string) ([]Record, error) {
	var recs []Record
	for i, part := range strings.Split(s, sep) {
		rec, err := Parse(part)
		if err != nil {
			return nil, fmt.Errorf("record %d: %w", i, err)
		}
		recs = append(recs, rec)
	}
	return recs, nil
}
EOF_INTERNAL_GOLF_GOLF_GO
cat > internal/golf/golf_test.go <<'EOF_INTERNAL_GOLF_GOLF_TEST_GO'
package golf

import (
	"testing"

	"github.com/ctx42/testing/pkg/assert"
)

func Test_Record_Pair(t *testing.T) {
	// --- Given ---
	rec := Record{Key: "a", Value: 1}

	// --- When ---
	have := rec.Pair()

	// --- Then ---
	assert.Equal(t, "a=1", have)
}

func Test_Record_Add(t *testing.T) {
	// --- Given ---
	rec := &Record{Key: "a", Value: 1}

	n := 2

	// --- When ---
	have := rec.Add(n)

	// --- Then ---
	assert.Equal(t, 3, have)

	assert.Equal(t, 3, rec.Value)
}

func Test_Parse(t *testing.T) {
	t.Run("valid", func(t *testing.T) {
		// --- Given ---
		s := "a=1"

		// --- When ---
		have, err := Parse(s)

		// --- Then ---
		assert.NoError(t, err)
		assert.Equal(t, Record{Key: "a", Value: 1}, have)
	})

	t.Run("error - value not a number", func(t *testing.T) {
		// --- Given ---
		s := "a=x"

		// --- When ---
		have, err := Parse(s)

		// --- Then ---
		assert.ErrorContain(t, "invalid syntax", err)
		assert.Zero(t, have)
	})
}

func Test_Split(t *testing.T) {
	t.Run("valid", func(t *testing.T) {
		// --- Given ---
		s := "a=1"

		sep := ";"

		// --- When ---
		have, err := Split(s, sep)

		// --- Then ---
		assert.NoError(t, err)

		assert.Equal(t, []Record{{Key: "a", Value: 1}}, have)
	})

	t.Run("error - bad record", func(t *testing.T) {
		// --- Given ---
		s := "a=1;b=x"

		sep := ";"

		// --- When ---
		have, err := Split(s, sep)

		// --- Then ---
		assert.ErrorContain(t, "invalid syntax", err)
		assert.Nil(t, have)
	})
}
EOF_INTERNAL_GOLF_GOLF_TEST_GO
cat > internal/hotel/hotel.go <<'EOF_INTERNAL_HOTEL_HOTEL_GO'
// Package hotel parses key-value records.
package hotel

import (
	"fmt"
	"strconv"
	"strings"
)

// Record is one key-value pair.
type Record struct {
	Key   string
	Value int
}

// Pair returns the record in the form "key=value".
func (rec Record) Pair() string {
	return rec.Key + "=" + strconv.Itoa(rec.Value)
}

// Add adds n to the record's value and returns the new value.
func (rec *Record) Add(n int) int {
	rec.Value += n
	return rec.Value
}

// Parse parses s in the form "key=value".
func Parse(s string) (Record, error) {
	key, raw, _ := strings.Cut(s, "=")
	val, err := strconv.Atoi(raw)
	if err != nil {
		return Record{}, fmt.Errorf("parse value: %w", err)
	}
	return Record{Key: key, Value: val}, nil
}

// Split parses every sep-separated record in s.
func Split(s, sep string) ([]Record, error) {
	var recs []Record
	for i, part := range strings.Split(s, sep) {
		rec, err := Parse(part)
		if err != nil {
			return nil, fmt.Errorf("record %d: %w", i, err)
		}
		recs = append(recs, rec)
	}
	return recs, nil
}
EOF_INTERNAL_HOTEL_HOTEL_GO
cat > internal/hotel/hotel_test.go <<'EOF_INTERNAL_HOTEL_HOTEL_TEST_GO'
package hotel

import (
	"testing"

	"github.com/ctx42/testing/pkg/assert"
)

func Test_Record_Pair(t *testing.T) {
	// --- Given ---
	rec := Record{Key: "a", Value: 1}

	// --- When ---
	have := rec.Pair()

	// --- Then ---
	assert.Equal(t, "a=1", have)
}

func Test_Record_Add(t *testing.T) {
	// --- Given ---
	rec := &Record{Key: "a", Value: 1}

	n := 2

	// --- When ---
	have := rec.Add(n)

	// --- Then ---
	assert.Equal(t, 3, have)

	assert.Equal(t, 3, rec.Value)
}

func Test_Parse(t *testing.T) {
	t.Run("valid", func(t *testing.T) {
		// --- Given ---
		s := "a=1"

		// --- When ---
		have, err := Parse(s)

		// --- Then ---
		assert.NoError(t, err)
		assert.Equal(t, Record{Key: "a", Value: 1}, have)
	})

	t.Run("error - value not a number", func(t *testing.T) {
		// --- Given ---
		s := "a=x"

		// --- When ---
		have, err := Parse(s)

		// --- Then ---
		assert.ErrorContain(t, "invalid syntax", err)
		assert.Zero(t, have)
	})
}

func Test_Split(t *testing.T) {
	t.Run("valid", func(t *testing.T) {
		// --- Given ---
		s := "a=1"

		sep := ";"

		// --- When ---
		have, err := Split(s, sep)

		// --- Then ---
		assert.NoError(t, err)

		assert.Equal(t, []Record{{Key: "a", Value: 1}}, have)
	})

	t.Run("error - bad record", func(t *testing.T) {
		// --- Given ---
		s := "a=1;b=x"

		sep := ";"

		// --- When ---
		have, err := Split(s, sep)

		// --- Then ---
		assert.ErrorContain(t, "invalid syntax", err)
		assert.Nil(t, have)
	})
}
EOF_INTERNAL_HOTEL_HOTEL_TEST_GO
# Runs have no network: fill the run's module cache now, from the local cache
# that dev/eval-changed.sh serves as GOPROXY.
go mod download
