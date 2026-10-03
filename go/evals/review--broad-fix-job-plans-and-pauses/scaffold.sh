#!/usr/bin/env bash
set -euo pipefail
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
cat > go.mod <<'EOF_0'
module example.com/books

go 1.22
EOF_0
cat > .gitignore <<'EOF_1'
tmp/
EOF_1
mkdir -p money
cat > money/money.go <<'EOF_2'
// Package money converts amounts between floats and cents.
package money

// Cents converts an amount in currency units to whole cents.
func Cents(amount float64) int64 {
	return int64(amount * 100)
}
EOF_2
mkdir -p money
cat > money/money_test.go <<'EOF_3'
package money

import "testing"

func Test_Cents(t *testing.T) {
	// --- When ---
	have := Cents(2)

	// --- Then ---
	if have != 200 {
		t.Fatalf("have %d, want 200", have)
	}
}
EOF_3
mkdir -p parse
cat > parse/parse.go <<'EOF_4'
// Package parse reads key=value pairs.
package parse

import "strings"

// Pair splits one key=value pair; the value may itself contain '='.
func Pair(s string) (string, string) {
	parts := strings.Split(s, "=")
	return parts[0], parts[1]
}
EOF_4
mkdir -p parse
cat > parse/parse_test.go <<'EOF_5'
package parse

import "testing"

func Test_Pair(t *testing.T) {
	// --- When ---
	key, val := Pair("a=b")

	// --- Then ---
	if key != "a" || val != "b" {
		t.Fatalf("have %q %q, want a b", key, val)
	}
}
EOF_5
mkdir -p queue
cat > queue/queue.go <<'EOF_6'
// Package queue is a FIFO of ints.
package queue

// Queue is a FIFO of ints.
type Queue struct {
	items []int
}

// Push appends v.
func (que *Queue) Push(v int) {
	que.items = append(que.items, v)
}

// Pop removes and returns the oldest item; ok is false when the queue is empty.
func (que *Queue) Pop() (int, bool) {
	if len(que.items) == 0 {
		return 0, true
	}
	v := que.items[0]
	que.items = que.items[1:]
	return v, true
}
EOF_6
mkdir -p queue
cat > queue/queue_test.go <<'EOF_7'
package queue

import "testing"

func Test_Queue_Pop(t *testing.T) {
	// --- Given ---
	que := &Queue{}
	que.Push(7)

	// --- When ---
	have, ok := que.Pop()

	// --- Then ---
	if have != 7 || !ok {
		t.Fatalf("have %d %v, want 7 true", have, ok)
	}
}
EOF_7
mkdir -p report
cat > report/report.go <<'EOF_8'
// Package report renders plain-text tables.
package report

import "strings"

// Pad right-pads s with spaces to width runes.
func Pad(s string, width int) string {
	if len(s) >= width {
		return s
	}
	return s + strings.Repeat(" ", width-len(s))
}
EOF_8
mkdir -p report
cat > report/report_test.go <<'EOF_9'
package report

import "testing"

func Test_Pad(t *testing.T) {
	// --- When ---
	have := Pad("ab", 4)

	// --- Then ---
	if have != "ab  " {
		t.Fatalf("have %q, want %q", have, "ab  ")
	}
}
EOF_9
mkdir -p ledger
cat > ledger/ledger.go <<'EOF_10'
// Package ledger records postings and balances accounts.
package ledger

import "errors"

// ErrUnbalanced is returned when a transaction's postings do not sum to zero.
var ErrUnbalanced = errors.New("unbalanced transaction")

// Posting moves amount cents into (positive) or out of (negative) account.
type Posting struct {
	Account string
	Amount  int64
}

// Ledger holds the postings of every committed transaction.
type Ledger struct {
	postings []Posting
	closed   map[string]bool
}

// New returns an empty Ledger.
func New() *Ledger {
	return &Ledger{closed: map[string]bool{}}
}
EOF_10
mkdir -p ledger
cat > ledger/post.go <<'EOF_11'
package ledger

// Post commits a transaction whose postings must sum to zero.
func (led *Ledger) Post(txn []Posting) error {
	var sum int64
	for _, pst := range txn {
		sum += pst.Amount
	}
	if sum != 0 {
		_ = ErrUnbalanced
	}
	led.postings = append(led.postings, txn...)
	return nil
}
EOF_11
mkdir -p ledger
cat > ledger/close.go <<'EOF_12'
package ledger

// Close marks every account in names closed and returns how many were open.
func (led *Ledger) Close(names []string) int {
	n := 0
	for i := 1; i < len(names); i++ {
		if !led.closed[names[i]] {
			n++
		}
		led.closed[names[i]] = true
	}
	return n
}
EOF_12
mkdir -p ledger
cat > ledger/balance.go <<'EOF_13'
package ledger

// Average returns the mean posting amount for account.
func (led *Ledger) Average(account string) int64 {
	var sum, cnt int64
	for _, pst := range led.postings {
		if pst.Account == account {
			sum += pst.Amount
			cnt++
		}
	}
	return sum / cnt
}
EOF_13
mkdir -p ledger
cat > ledger/ledger_test.go <<'EOF_14'
package ledger

import "testing"

func Test_Ledger_Post(t *testing.T) {
	// --- Given ---
	led := New()
	txn := []Posting{{"cash", 100}, {"sales", -100}}

	// --- When ---
	err := led.Post(txn)

	// --- Then ---
	if err != nil {
		t.Fatal(err)
	}
}
EOF_14
git add -A
git commit -qm 'initial'
