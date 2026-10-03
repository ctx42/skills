#!/usr/bin/env bash
set -euo pipefail
cat > .editorconfig <<'EOF__EDITORCONFIG'
root = true

[*.go]
indent_style = tab
tab_width = 4
max_line_length = 72
EOF__EDITORCONFIG
cat > go.mod <<'EOF_GO_MOD'
module example.com/svc

go 1.26
EOF_GO_MOD
cat > service.go <<'EOF_SERVICE_GO'
// Package svc serves records from a store and keeps an audit log.
package svc

import "io"

// Service serves records from a store and writes an audit log.
type Service struct {
	store  io.Closer
	audit  io.Closer
	served int
}

// New returns a Service over store that logs to audit.
func New(store, audit io.Closer) *Service {
	return &Service{store: store, audit: audit}
}

// Served returns the number of records served so far.
func (svc *Service) Served() int {
	return svc.served
}
EOF_SERVICE_GO
