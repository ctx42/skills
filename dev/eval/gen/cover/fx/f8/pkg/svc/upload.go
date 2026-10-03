// Package svc uploads reports to the collection service.
package svc

import (
	"bytes"
	"errors"
	"fmt"
	"net/http"
	"time"
)

// endpoint is the collection service URL.
const endpoint = "https://collect.example.com/v1/reports"

// ErrEmpty is returned when there is nothing to upload.
var ErrEmpty = errors.New("empty report")

// Upload posts the report body to the collection service.
func Upload(body []byte) error {
	if len(body) == 0 {
		return ErrEmpty
	}
	client := &http.Client{Transport: &http.Transport{}, Timeout: 10 * time.Second}
	resp, err := client.Post(endpoint, "application/json", bytes.NewReader(body))
	if err != nil {
		return fmt.Errorf("upload: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("upload: status %d", resp.StatusCode)
	}
	return nil
}
