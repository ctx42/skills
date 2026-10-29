#!/usr/bin/env bash
set -euo pipefail
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
cat > go.mod <<'EOF_0'
module example.com/client

go 1.22
EOF_0
cat > client.go <<'EOF_1'
// Package client sends HTTP requests with retries.
package client

import "net/http"

// Client retries a failed request up to MaxRetries times.
type Client struct {
	HTTP       *http.Client
	MaxRetries int
}

// Do sends req, retrying on a 5xx status.
func (c *Client) Do(req *http.Request) (*http.Response, error) {
	var resp *http.Response
	var err error
	for i := 0; i <= c.MaxRetries; i++ {
		resp, err = c.HTTP.Do(req)
		if err != nil {
			return nil, err
		}
		if resp.StatusCode < 500 {
			return resp, nil
		}
	}
	return resp, nil
}
EOF_1
cat > client_test.go <<'EOF_2'
package client

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func Test_Client_Do(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))
	defer srv.Close()

	c := &Client{HTTP: srv.Client()}
	req, _ := http.NewRequest(http.MethodGet, srv.URL, nil)
	have, err := c.Do(req)
	if err != nil || have.StatusCode != http.StatusOK {
		t.Fatalf("Do() = %v, %v", have, err)
	}
	have.Body.Close()
}
EOF_2
cat > README.md <<'EOF_3'
# client

HTTP client with retries. `MaxRetries` defaults to 0: a request is sent once.
EOF_3
go vet ./... && go test ./... >/dev/null
git add -A
git commit -qm 'initial'
