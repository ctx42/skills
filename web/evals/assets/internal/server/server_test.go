package server

import (
	"bytes"
	"context"
	"errors"
	"net/http"
	"net/http/httptest"
	"testing"
	"testing/fstest"
	"time"

	"github.com/ctx42/testing/pkg/assert"

	"example.com/fleet/internal/upstream"
)

// inventory is an [Inventory] answering from its fields; a set err fails
// every call.
type inventory struct {
	devs  []upstream.Device
	sites []upstream.Site
	err   error
}

func (inv inventory) Devices(
	_ context.Context,
	site string,
) ([]upstream.Device, error) {

	var out []upstream.Device
	for _, dev := range inv.devs {
		if site == "" || dev.SiteID == site {
			out = append(out, dev)
		}
	}
	return out, inv.err
}

func (inv inventory) Device(
	_ context.Context,
	id string,
) (upstream.Device, error) {

	for _, dev := range inv.devs {
		if dev.ID == id {
			return dev, inv.err
		}
	}
	return upstream.Device{}, upstream.ErrNotFound
}

func (inv inventory) Sites(_ context.Context) ([]upstream.Site, error) {
	return inv.sites, inv.err
}

func (inv inventory) Site(_ context.Context, id string) (upstream.Site, error) {
	for _, sit := range inv.sites {
		if sit.ID == id {
			return sit, inv.err
		}
	}
	return upstream.Site{}, upstream.ErrNotFound
}

// testSeen is when d1 of testInv last reported.
var testSeen = time.Date(2026, time.October, 20, 7, 0, 0, 0, time.UTC)

// testInv holds two devices at two sites; d2 never reported.
var testInv = inventory{
	devs: []upstream.Device{
		{
			ID:       "d1",
			Serial:   "SN-0001",
			SiteID:   "s1",
			Model:    "T-100",
			Added:    time.Date(2026, time.January, 5, 8, 0, 0, 0, time.UTC),
			LastSeen: new(testSeen),
		},
		{
			ID:     "d2",
			Serial: "SN-0002",
			SiteID: "s2",
			Model:  "T-200",
			Added:  time.Date(2026, time.March, 2, 14, 0, 0, 0, time.UTC),
		},
	},
	sites: []upstream.Site{{ID: "s1", Name: "North Yard", City: "Zurich"}},
}

// testDist is a built frontend of an index page and one asset.
var testDist = fstest.MapFS{
	"index.html":    {Data: []byte("<!doctype html>index")},
	"assets/app.js": {Data: []byte("app")},
}

func Test_New_tabular(t *testing.T) {
	tt := []struct {
		testN string

		inv    inventory
		path   string
		status int
		body   string
	}{
		{
			"devices",
			testInv,
			"/api/devices",
			http.StatusOK,
			`{"data":[{"id":"d1","serial":"SN-0001","site_id":"s1",` +
				`"model_name":"T-100","added":1767600000,` +
				`"last_seen":"2026-10-20T07:00:00Z"},{"id":"d2",` +
				`"serial":"SN-0002","site_id":"s2","model_name":"T-200",` +
				`"added":1772460000,"last_seen":null}]}` + "\n",
		},
		{
			"devices of a site",
			testInv,
			"/api/devices?site=s2",
			http.StatusOK,
			`{"data":[{"id":"d2","serial":"SN-0002","site_id":"s2",` +
				`"model_name":"T-200","added":1772460000,` +
				`"last_seen":null}]}` + "\n",
		},
		{
			"no devices",
			inventory{},
			"/api/devices",
			http.StatusOK,
			`{"data":[]}` + "\n",
		},
		{
			"device",
			testInv,
			"/api/devices/d2",
			http.StatusOK,
			`{"id":"d2","serial":"SN-0002","site_id":"s2",` +
				`"model_name":"T-200","added":1772460000,` +
				`"last_seen":null}` + "\n",
		},
		{
			"unknown device",
			testInv,
			"/api/devices/d9",
			http.StatusNotFound,
			`{"error":"not found"}` + "\n",
		},
		{
			"sites",
			testInv,
			"/api/sites",
			http.StatusOK,
			`{"data":[{"id":"s1","name":"North Yard","city":"Zurich"}]}` +
				"\n",
		},
		{
			"site",
			testInv,
			"/api/sites/s1",
			http.StatusOK,
			`{"id":"s1","name":"North Yard","city":"Zurich"}` + "\n",
		},
		{
			"unknown site",
			testInv,
			"/api/sites/s9",
			http.StatusNotFound,
			`{"error":"not found"}` + "\n",
		},
		{
			"unknown API path",
			testInv,
			"/api/nope",
			http.StatusNotFound,
			"404 page not found\n",
		},
		{
			"asset",
			testInv,
			"/assets/app.js",
			http.StatusOK,
			"app",
		},
		{
			"page path",
			testInv,
			"/devices/d1",
			http.StatusOK,
			"<!doctype html>index",
		},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- Given ---
			req := httptest.NewRequest(http.MethodGet, tc.path, nil)
			rec := httptest.NewRecorder()

			// --- When ---
			New(tc.inv, testDist).ServeHTTP(rec, req)

			// --- Then ---
			assert.Equal(t, tc.status, rec.Code)
			assert.Equal(t, tc.body, rec.Body.String())
		})
	}
}

func Test_New_inventory_errors_tabular(t *testing.T) {
	tt := []struct {
		testN string

		path string
	}{
		{"devices", "/api/devices"},
		{"device", "/api/devices/d1"},
		{"sites", "/api/sites"},
		{"site", "/api/sites/s1"},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- Given ---
			inv := testInv
			inv.err = errors.New("down")
			req := httptest.NewRequest(http.MethodGet, tc.path, nil)
			rec := httptest.NewRecorder()

			// --- When ---
			New(inv, testDist).ServeHTTP(rec, req)

			// --- Then ---
			assert.Equal(t, http.StatusBadGateway, rec.Code)
			want := `{"error":"inventory unavailable"}` + "\n"
			assert.Equal(t, want, rec.Body.String())
		})
	}
}

func Test_Logged(t *testing.T) {
	// --- Given ---
	var log bytes.Buffer
	next := http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusTeapot)
	})
	req := httptest.NewRequest(http.MethodPost, "/api/devices?site=s1", nil)
	rec := httptest.NewRecorder()

	// --- When ---
	Logged(next, &log).ServeHTTP(rec, req)

	// --- Then ---
	assert.Equal(t, "POST /api/devices?site=s1\n", log.String())
	assert.Equal(t, http.StatusTeapot, rec.Code)
}
