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
