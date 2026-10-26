// Package upstream is a client of the fleet inventory service, the system
// of record for sites and the devices installed at them.
package upstream

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"net/url"
	"time"
)

// ErrNotFound is returned when the inventory has no record of the asked ID.
var ErrNotFound = errors.New("not found")

// timeout bounds every call to the inventory.
const timeout = 10 * time.Second

// Device is a device as the inventory records it; LastSeen is nil for a
// device that never reported.
type Device struct {
	ID       string     `json:"id"`
	Serial   string     `json:"serial"`
	SiteID   string     `json:"site_id"`
	Model    string     `json:"model"`
	Added    time.Time  `json:"added"`
	LastSeen *time.Time `json:"last_seen,omitempty"`
}

// Site is a place devices are installed at.
type Site struct {
	ID   string `json:"id"`
	Name string `json:"name"`
	City string `json:"city"`
}

// list is the envelope the inventory wraps every list in.
type list[T any] struct {
	Items []T `json:"items"`
}

// Client calls the inventory at a base URL.
type Client struct {
	base string
	hc   *http.Client
}

// New returns a client of the inventory at base, such as
// "http://localhost:8191".
func New(base string) *Client {
	return &Client{base: base, hc: &http.Client{Timeout: timeout}}
}

// Devices returns the devices of the site with ID site, or of every site
// when site is empty.
func (cli *Client) Devices(ctx context.Context, site string) ([]Device, error) {
	path := "/devices"
	if site != "" {
		path += "?site=" + url.QueryEscape(site)
	}
	var lst list[Device]
	if err := cli.get(ctx, path, &lst); err != nil {
		return nil, err
	}
	return lst.Items, nil
}

// Device returns the device with ID id.
func (cli *Client) Device(ctx context.Context, id string) (Device, error) {
	var dev Device
	err := cli.get(ctx, "/devices/"+url.PathEscape(id), &dev)
	return dev, err
}

// Site returns the site with ID id.
func (cli *Client) Site(ctx context.Context, id string) (Site, error) {
	var sit Site
	err := cli.get(ctx, "/sites/"+url.PathEscape(id), &sit)
	return sit, err
}

// Sites returns every site.
func (cli *Client) Sites(ctx context.Context) ([]Site, error) {
	var lst list[Site]
	if err := cli.get(ctx, "/sites", &lst); err != nil {
		return nil, err
	}
	return lst.Items, nil
}

// get decodes the JSON answer to a GET of path into dst. A 404 answer
// returns [ErrNotFound]; any other non-200 answer an error naming its
// status.
func (cli *Client) get(ctx context.Context, path string, dst any) error {
	addr := cli.base + path
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, addr, nil)
	if err != nil {
		return fmt.Errorf("inventory: %w", err)
	}
	rsp, err := cli.hc.Do(req)
	if err != nil {
		return fmt.Errorf("inventory: %w", err)
	}
	defer func() { _ = rsp.Body.Close() }()
	switch rsp.StatusCode {
	case http.StatusOK:
		if err = json.NewDecoder(rsp.Body).Decode(dst); err != nil {
			return fmt.Errorf("inventory: GET %s: %w", path, err)
		}
		return nil

	case http.StatusNotFound:
		return ErrNotFound

	default:
		return fmt.Errorf("inventory: GET %s: %s", path, rsp.Status)
	}
}
