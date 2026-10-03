#!/usr/bin/env bash
set -euo pipefail
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
cat > go.mod <<'EOF_0'
module example.com/app

go 1.22
EOF_0
mkdir -p page
cat > page/page.go <<'EOF_1'
// Package page splits result sets into cursor-addressed pages.
package page

// Page is one slice of a result set and the cursor of the next one.
type Page struct {
	Items []string
	Next  int // index of the first item of the next page; -1 on the last page
}

// Get returns the page of at most size items starting at cursor.
func Get(items []string, cursor, size int) Page {
	end := cursor + size
	if end > len(items) {
		end = len(items)
	}
	next := end + 1
	if end == len(items) {
		next = -1
	}
	return Page{Items: items[cursor:end], Next: next}
}
EOF_1
cat > .gitignore <<'EOF_2'
/bin/
EOF_2
git add -A
git commit -qm 'feat(page): add cursor pagination'
mkdir -p page
cat > page/page.go <<'EOF_0'
// Package page splits result sets into cursor-addressed pages.
package page

// Page is one slice of a result set and the cursor of the next one.
type Page struct {
	Items []string
	Next  int // index of the first item of the next page; -1 on the last page
}

// Get returns the page of at most size items starting at cursor.
func Get(items []string, cursor, size int) Page {
	end := cursor + size
	if end > len(items) {
		end = len(items)
	}
	next := end
	if end == len(items) {
		next = -1
	}
	return Page{Items: items[cursor:end], Next: next}
}
EOF_0
git add -A
git commit -qm 'fixes'
cat > .gitignore <<'EOF_0'
/bin/
/coverage.out
EOF_0
git add .gitignore
