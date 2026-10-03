// Package num describes numbers.
package num

// Foo names the sign of n.
func Foo(n int) string {
	if n < 0 {
		return "negative"
	}
	if n == 0 {
		return "zero"
	}
	return "positive"
}
