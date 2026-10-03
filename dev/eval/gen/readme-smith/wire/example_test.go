package wiretap_test

import (
	"fmt"

	"github.com/acme/wiretap"
)

func ExampleRequest() {
	wire := wiretap.Request("POST", "/v1/orders", "api.shop.example", map[string]string{
		"Accept":        "application/json",
		"Authorization": "Bearer 7f3c9a1e",
		"Content-Type":  "application/json",
		"User-Agent":    "wiretap/0.3",
		"X-Request-Id":  "c0ffee-42-b7d1",
	}, `{"sku":"KB-104","qty":2,"note":"gift wrap"}`)
	fmt.Printf("%q\n", wire)
	// Output:
	// "POST /v1/orders HTTP/1.1\r\nHost: api.shop.example\r\nAccept: application/json\r\nAuthorization: Bearer 7f3c9a1e\r\nContent-Type: application/json\r\nUser-Agent: wiretap/0.3\r\nX-Request-Id: c0ffee-42-b7d1\r\nContent-Length: 43\r\n\r\n{\"sku\":\"KB-104\",\"qty\":2,\"note\":\"gift wrap\"}"
}
