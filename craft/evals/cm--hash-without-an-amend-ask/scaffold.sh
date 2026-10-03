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
mkdir -p mw
cat > mw/chain.go <<'EOF_1'
// Package mw holds the service's HTTP middleware.
package mw

import "net/http"

// Chain applies the middleware in order.
func Chain(h http.Handler, mws ...func(http.Handler) http.Handler) http.Handler {
	for i := len(mws) - 1; i >= 0; i-- {
		h = mws[i](h)
	}
	return h
}
EOF_1
git add -A
git commit -qm 'feat(mw): add middleware chain'
mkdir -p mw
cat > mw/requestid.go <<'EOF_0'
package mw

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"net/http"
)

// Header carries the request id between services.
const Header = "X-Request-Id"

type ridKey struct{}

// RequestID reuses the caller's X-Request-Id or mints one, stores it in the
// request context, and echoes it in the response.
func RequestID(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		id := r.Header.Get(Header)
		if id == "" {
			var b [8]byte
			_, _ = rand.Read(b[:])
			id = hex.EncodeToString(b[:])
		}
		w.Header().Set(Header, id)
		next.ServeHTTP(w, r.WithContext(context.WithValue(r.Context(), ridKey{}, id)))
	})
}

// FromContext returns the request id stored by RequestID, or "".
func FromContext(ctx context.Context) string {
	id, _ := ctx.Value(ridKey{}).(string)
	return id
}
EOF_0
git add -A
git commit -qm 'wip'
