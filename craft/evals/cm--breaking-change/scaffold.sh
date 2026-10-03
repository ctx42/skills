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
mkdir -p api
cat > api/client.go <<'EOF_1'
// Package api is the client of the inventory service.
package api

import (
	"context"
	"net/http"
)

// Client calls the inventory service.
type Client struct {
	base string
	hc   *http.Client
}

// Do sends req as is.
func (cli *Client) Do(req *http.Request) (*http.Response, error) {
	return cli.hc.Do(req)
}

// DoRequest sends req with ctx attached and the base URL applied.
func (cli *Client) DoRequest(ctx context.Context, req *http.Request) (*http.Response, error) {
	req = req.WithContext(ctx)
	if req.URL.Host == "" {
		req.URL.Scheme, req.URL.Host = "https", cli.base
	}
	return cli.hc.Do(req)
}
EOF_1
mkdir -p api
cat > api/items.go <<'EOF_2'
package api

import (
	"context"
	"net/http"
)

// Items lists the inventory items.
func (cli *Client) Items(ctx context.Context) (*http.Response, error) {
	req, err := http.NewRequest(http.MethodGet, "/items", nil)
	if err != nil {
		return nil, err
	}
	return cli.DoRequest(ctx, req)
}
EOF_2
git add -A
git commit -qm 'feat(api): add inventory client'
mkdir -p api
cat > api/client.go <<'EOF_0'
// Package api is the client of the inventory service.
package api

import (
	"context"
	"net/http"
)

// Client calls the inventory service.
type Client struct {
	base string
	hc   *http.Client
}

// Do sends req with ctx attached and the base URL applied.
func (cli *Client) Do(ctx context.Context, req *http.Request) (*http.Response, error) {
	req = req.WithContext(ctx)
	if req.URL.Host == "" {
		req.URL.Scheme, req.URL.Host = "https", cli.base
	}
	return cli.hc.Do(req)
}
EOF_0
mkdir -p api
cat > api/items.go <<'EOF_1'
package api

import (
	"context"
	"net/http"
)

// Items lists the inventory items.
func (cli *Client) Items(ctx context.Context) (*http.Response, error) {
	req, err := http.NewRequest(http.MethodGet, "/items", nil)
	if err != nil {
		return nil, err
	}
	return cli.Do(ctx, req)
}
EOF_1
git add -A
