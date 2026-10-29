// Package svc encodes values for the wire format.
package svc

import (
	"fmt"
	"strconv"
	"strings"
)

// Encode renders v in the compact wire format.
func Encode(v any) string {
	switch x := v.(type) {
	case int:
		return strconv.Itoa(x)
	case string:
		return strconv.Quote(x)
	case bool:
		return strconv.FormatBool(x)
	case []int:
		parts := make([]string, len(x))
		for i, n := range x {
			parts[i] = strconv.Itoa(n)
		}
		return "[" + strings.Join(parts, ",") + "]"
	default:
		return fmt.Sprintf("%v", x)
	}
}
