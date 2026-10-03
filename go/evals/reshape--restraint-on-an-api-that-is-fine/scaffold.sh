#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module example.com/blog

go 1.22

require example.com/tidy v0.0.0

replace example.com/tidy => ./third_party/tidy
EOF_0
mkdir -p third_party/tidy
cat > third_party/tidy/go.mod <<'EOF_1'
module example.com/tidy

go 1.22
EOF_1
mkdir -p third_party/tidy
cat > third_party/tidy/tidy.go <<'EOF_2'
// Package tidy normalizes user-entered text.
package tidy

import "strings"

// Clean trims s and collapses runs of whitespace to one space.
func Clean(s string) string { return strings.Join(strings.Fields(s), " ") }

// Slug returns a lowercase, dash-separated form of s.
func Slug(s string) string { return strings.ToLower(strings.Join(strings.Fields(s), "-")) }

// Words splits s into its whitespace-separated words.
func Words(s string) []string { return strings.Fields(s) }
EOF_2
mkdir -p blog
cat > blog/post.go <<'EOF_3'
// Package blog models blog posts.
package blog

import "example.com/tidy"

// Post is a blog post.
type Post struct {
	Title string
	Slug  string
	Body  string
	Tags  []string
}

// NewPost builds a post from raw form input.
func NewPost(title, body, tags string) Post {
	t := tidy.Clean(title)
	return Post{
		Title: t,
		Slug:  tidy.Slug(t),
		Body:  tidy.Clean(body),
		Tags:  tidy.Words(tags),
	}
}

// Rename changes the post title and its slug.
func (p *Post) Rename(title string) {
	p.Title = tidy.Clean(title)
	p.Slug = tidy.Slug(p.Title)
}
EOF_3
mkdir -p blog
cat > blog/search.go <<'EOF_4'
package blog

import (
	"strings"

	"example.com/tidy"
)

// Matches reports whether the post contains every word of query.
func (p Post) Matches(query string) bool {
	body := strings.ToLower(p.Body)
	for _, w := range tidy.Words(strings.ToLower(query)) {
		if !strings.Contains(body, w) {
			return false
		}
	}
	return true
}

// Titles returns the cleaned titles of raw.
func Titles(raw []string) []string {
	out := make([]string, 0, len(raw))
	for _, r := range raw {
		out = append(out, tidy.Clean(r))
	}
	return out
}

// Anchor returns the in-page anchor for a heading.
func Anchor(heading string) string { return "#" + tidy.Slug(heading) }
EOF_4
