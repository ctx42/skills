// Package web embeds the built frontend. Run "bun run build" in this
// directory before building the server; without it, the server has only the
// placeholder dist/.gitkeep to serve.
package web

import (
	"embed"
	"io/fs"
)

// dist holds the Vite build output.
//
//go:embed all:dist
var dist embed.FS

// Dist returns the built frontend with index.html at its root.
func Dist() (fs.FS, error) { return fs.Sub(dist, "dist") }
