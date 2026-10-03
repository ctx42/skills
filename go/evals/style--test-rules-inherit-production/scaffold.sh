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

require github.com/ctx42/testing v0.56.0
EOF_GO_MOD
cat > go.sum <<'EOF_GO_SUM'
github.com/ctx42/testing v0.56.0 h1:+yZwRy+5JQb+14YtRTGJxWbAMAP9qlU9pMa8TPqgdzE=
github.com/ctx42/testing v0.56.0/go.mod h1:wRBqNRtlxDZnXIjgCX3zr05Acl6JC1D6cSBN2IpaMIs=
EOF_GO_SUM
cat > service.go <<'EOF_SERVICE_GO'
// Package svc serves records from a store and keeps an audit log.
package svc

import (
	"fmt"
	"io"
)

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

// Close closes the store, then the audit log.
func (svc *Service) Close() error {
	if err := svc.store.Close(); err != nil {
		return fmt.Errorf("close store: %w", err)
	}
	if err := svc.audit.Close(); err != nil {
		return fmt.Errorf("close audit: %w", err)
	}
	return nil
}
EOF_SERVICE_GO
