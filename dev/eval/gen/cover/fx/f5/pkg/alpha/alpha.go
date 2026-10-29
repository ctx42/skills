// Package alpha is part of the eval module.
package alpha

// Name returns the alpha label for n.
func Name(n int) string {
	if n < 0 {
		return "alpha-negative"
	}
	return "alpha"
}
