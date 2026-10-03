// Package logs is part of the eval module.
package logs

// Name returns the logs label for n.
func Name(n int) string {
	if n < 0 {
		return "logs-negative"
	}
	return "logs"
}
