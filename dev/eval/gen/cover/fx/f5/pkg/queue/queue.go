// Package queue is part of the eval module.
package queue

// Name returns the queue label for n.
func Name(n int) string {
	if n < 0 {
		return "queue-negative"
	}
	return "queue"
}
