// Package util is part of the eval module.
package util

// Name returns the util label for n.
func Name(n int) string {
	if n < 0 {
		return "util-negative"
	}
	return "util"
}
