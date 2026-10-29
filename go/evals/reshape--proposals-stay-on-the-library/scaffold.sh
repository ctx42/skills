#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module example.com/site

go 1.22

require github.com/acme/oskit v1.4.0
EOF_0
mkdir -p pkg/render
cat > pkg/render/template.go <<'EOF_1'
// Package render renders pages from templates on disk.
package render

import (
	"fmt"
	"path/filepath"
	"strings"

	"github.com/acme/oskit"
)

// LoadTemplate returns the template called name.
func LoadTemplate(name string) (string, error) {
	f, err := oskit.Open(filepath.Join("templates", name))
	if err != nil {
		if strings.Contains(err.Error(), "does not exist") {
			return "", fmt.Errorf("template %q not found", name)
		}
		return "", err
	}
	defer f.Close()
	data, err := oskit.ReadAll(f)
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(string(data)), nil
}
EOF_1
mkdir -p pkg/render
cat > pkg/render/partial.go <<'EOF_2'
package render

import (
	"fmt"
	"path/filepath"
	"strings"

	"github.com/acme/oskit"
)

// LoadPartial returns the partial called name.
func LoadPartial(name string) (string, error) {
	f, err := oskit.Open(filepath.Join("partials", name))
	if err != nil {
		if strings.Contains(err.Error(), "does not exist") {
			return "", fmt.Errorf("partial %q not found", name)
		}
		return "", err
	}
	defer f.Close()
	data, err := oskit.ReadAll(f)
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(string(data)), nil
}
EOF_2
mkdir -p pkg/render
cat > pkg/render/layout.go <<'EOF_3'
package render

import (
	"fmt"
	"path/filepath"
	"strings"

	"github.com/acme/oskit"
)

// LoadLayout returns the layout called name.
func LoadLayout(name string) (string, error) {
	f, err := oskit.Open(filepath.Join("layouts", name))
	if err != nil {
		if strings.Contains(err.Error(), "does not exist") {
			return "", fmt.Errorf("layout %q not found", name)
		}
		return "", err
	}
	defer f.Close()
	data, err := oskit.ReadAll(f)
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(string(data)), nil
}
EOF_3
mkdir -p pkg/render
cat > pkg/render/asset.go <<'EOF_4'
package render

import (
	"fmt"
	"path/filepath"
	"strings"

	"github.com/acme/oskit"
)

// LoadAsset returns the asset called name.
func LoadAsset(name string) (string, error) {
	f, err := oskit.Open(filepath.Join("assets", name))
	if err != nil {
		if strings.Contains(err.Error(), "does not exist") {
			return "", fmt.Errorf("asset %q not found", name)
		}
		return "", err
	}
	defer f.Close()
	data, err := oskit.ReadAll(f)
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(string(data)), nil
}
EOF_4
mkdir -p pkg/render
cat > pkg/render/page.go <<'EOF_5'
package render

import "strings"

// Page renders the named page inside its layout.
func Page(name string) (string, error) {
	layout, err := LoadLayout("base.html")
	if err != nil {
		return "", err
	}
	body, err := LoadTemplate(name)
	if err != nil {
		return "", err
	}
	return strings.Replace(layout, "{{body}}", body, 1), nil
}
EOF_5
mkdir -p pkg/report
cat > pkg/report/report.go <<'EOF_6'
// Package report writes run reports.
package report

import "github.com/acme/oskit"

// Save writes data to path.
func Save(path string, data []byte) error {
	f, err := oskit.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	_, err = f.Write(data)
	return err
}

// Exists reports whether path exists.
func Exists(path string) bool {
	_, err := oskit.Stat(path)
	return err == nil
}
EOF_6
px=$(mktemp -d)
src=$px/src/github.com/acme/oskit@v1.4.0
at=$px/proxy/github.com/acme/oskit/@v
mkdir -p "$src" "$at"
printf 'module github.com/acme/oskit\n\ngo 1.22\n' > "$src/go.mod"
cat > "$src/oskit.go" <<'EOF_OSKIT'
// Package oskit wraps the operating system's file calls.
package oskit

import (
	"io"
	"os"
)

// File is an open file.
type File struct {
	fil *os.File
}

// Open opens name for reading.
func Open(name string) (*File, error) {
	fil, err := os.Open(name)
	if err != nil {
		return nil, err
	}
	return &File{fil: fil}, nil
}

// Create creates or truncates name for writing.
func Create(name string) (*File, error) {
	fil, err := os.Create(name)
	if err != nil {
		return nil, err
	}
	return &File{fil: fil}, nil
}

// Read reads up to len(p) bytes into p.
func (fl *File) Read(p []byte) (int, error) { return fl.fil.Read(p) }

// Write writes p to the file.
func (fl *File) Write(p []byte) (int, error) { return fl.fil.Write(p) }

// Close closes the file.
func (fl *File) Close() error { return fl.fil.Close() }

// ReadAll reads from fl until EOF.
func ReadAll(fl *File) ([]byte, error) { return io.ReadAll(fl) }

// Stat describes the named file.
func Stat(name string) (os.FileInfo, error) { return os.Stat(name) }
EOF_OSKIT
cp "$src/go.mod" "$at/v1.4.0.mod"
printf '{"Version":"v1.4.0","Time":"2026-01-01T00:00:00Z"}' > "$at/v1.4.0.info"
printf 'v1.4.0\n' > "$at/list"
(cd "$px/src" && zip -qr "$at/v1.4.0.zip" github.com/acme/oskit@v1.4.0)
GOPROXY="file://$px/proxy" GOSUMDB=off GOFLAGS=-mod=mod go get github.com/acme/oskit@v1.4.0
rm -rf "$px"
