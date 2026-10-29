// Package beta is part of the eval module.
package beta

// Name returns the beta label for n.
func Name(n int) string {
	if n < 0 {
		return "beta-negative"
	}
	return "beta"
}
