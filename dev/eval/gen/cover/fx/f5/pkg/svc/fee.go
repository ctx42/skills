// Package svc computes order fees.
package svc

// Fee returns the handling fee in cents for an order of the given total.
func Fee(total int) int {
	if total <= 0 {
		return 0
	}
	if total >= 10000 {
		return 0
	}
	return 250
}

// Tax returns the tax in cents for amount at the given rate in percent.
func Tax(amount, rate int) int {
	if rate <= 0 {
		return 0
	}
	if amount <= 0 {
		return 0
	}
	return amount * rate / 100
}
