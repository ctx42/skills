// Package api maps request paths to handlers.
package api

import "strings"

// Route returns the handler name for path.
func Route(path string) string {
	if path == "" || path == "/" {
		return "index"
	}
	if strings.HasPrefix(path, "/admin") {
		return "admin"
	}
	return "page"
}

// Method normalizes an HTTP method name.
func Method(m string) string {
	if m == "" {
		return "GET"
	}
	if strings.EqualFold(m, "head") {
		return "GET"
	}
	return strings.ToUpper(m)
}
