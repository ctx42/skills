// Package wiretap renders HTTP/1.1 requests as the exact bytes sent on the wire.
package wiretap

import (
	"bytes"
	"fmt"
	"sort"
)

// Request renders an HTTP/1.1 request line, headers sorted by name, a blank
// line, and the body, exactly as they travel over the connection.
func Request(method, target, host string, header map[string]string, body string) []byte {
	var b bytes.Buffer
	fmt.Fprintf(&b, "%s %s HTTP/1.1\r\n", method, target)
	fmt.Fprintf(&b, "Host: %s\r\n", host)
	keys := make([]string, 0, len(header))
	for k := range header {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	for _, k := range keys {
		fmt.Fprintf(&b, "%s: %s\r\n", k, header[k])
	}
	fmt.Fprintf(&b, "Content-Length: %d\r\n\r\n", len(body))
	b.WriteString(body)
	return b.Bytes()
}
