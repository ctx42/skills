#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module example.com/svc

go 1.22
EOF_0
mkdir -p cmd/svc
cat > cmd/svc/main.go <<'EOF_1'
// Command svc serves the operator API.
package main

import (
	"log"
	"net/http"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
	})
	log.Fatal(http.ListenAndServe(":8080", mux))
}
EOF_1
