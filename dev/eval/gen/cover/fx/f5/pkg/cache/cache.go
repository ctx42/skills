// Package cache is part of the eval module.
package cache

// Name returns the cache label for n.
func Name(n int) string {
	if n < 0 {
		return "cache-negative"
	}
	return "cache"
}
