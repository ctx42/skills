// Package svc holds small numeric and text helpers.
package svc

// Abs returns the absolute value of n.
func Abs(n int) int {
	if n < 0 {
		return -n
	}
	return n
}

// Clamp limits n to the range [lo, hi].
func Clamp(n, lo, hi int) int {
	if n < lo {
		return lo
	}
	if n > hi {
		return hi
	}
	return n
}

// Sign returns -1, 0, or 1 for negative, zero, and positive n.
func Sign(n int) int {
	if n < 0 {
		return -1
	}
	if n == 0 {
		return 0
	}
	return 1
}
