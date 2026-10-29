package svc

import "testing"

// skipPending skips a table row whose shape is not supported yet.
func skipPending(t *testing.T) {
	t.Helper()
	t.Skip("pending: shape not supported yet")
}
