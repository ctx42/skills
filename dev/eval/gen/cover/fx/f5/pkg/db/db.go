// Package db is part of the eval module.
package db

// Name returns the db label for n.
func Name(n int) string {
	if n < 0 {
		return "db-negative"
	}
	return "db"
}
