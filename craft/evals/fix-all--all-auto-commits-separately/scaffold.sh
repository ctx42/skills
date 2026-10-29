#!/usr/bin/env bash
set -euo pipefail
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
cat > go.mod <<'EOF_0'
module example.com/fetch

go 1.22
EOF_0
cat > fetch.go <<'EOF_1'
// Package fetch downloads documents over HTTP.
package fetch

import (
	"fmt"
	"io"
	"net/http"
)

// Fetch returns the body of the document at url. Callers recieve an error
// for any status other than 200.
func Fetch(c *http.Client, url string) ([]byte, error) {
	resp, err := c.Get(url)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("fetch %s: %s", url, resp.Status)
	}
	defer resp.Body.Close()
	return io.ReadAll(resp.Body)
}
EOF_1
cat > util.go <<'EOF_2'
package fetch

import "strings"

// trimAll trims the space around every string in ss.
func trimAll(ss []string) []string {
	out := make([]string, len(ss))
	for i, s := range ss {
		out[i] = strings.TrimSpace(s)
	}
	return out
}
EOF_2
cat > fetch_test.go <<'EOF_3'
package fetch

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func Test_Fetch(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/missing" {
			http.NotFound(w, r)
			return
		}
		_, _ = w.Write([]byte("ok"))
	}))
	defer srv.Close()

	have, err := Fetch(srv.Client(), srv.URL+"/doc")
	if err != nil || string(have) != "ok" {
		t.Fatalf("Fetch() = %q, %v", have, err)
	}
	if _, err := Fetch(srv.Client(), srv.URL+"/missing"); err == nil {
		t.Fatal("Fetch(/missing) error = nil")
	}
}
EOF_3
go vet ./... && go test ./... >/dev/null
git add -A
git commit -qm 'initial'
