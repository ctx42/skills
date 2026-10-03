package net

import "time"

// Retry calls fn up to n times and returns nil on the first success. Between
// attempts it waits 100ms. It returns the last error when every attempt fails.
func Retry(n int, fn func() error) error {
	var err error
	for i := 0; i < n; i++ {
		if err = fn(); err == nil {
			return nil
		}
		if i < n-1 {
			time.Sleep(100 * time.Millisecond)
		}
	}
	return err
}
