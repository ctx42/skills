package fake

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/ctx42/testing/pkg/assert"
)

func Test_Sites(t *testing.T) {
	// --- When ---
	have := Sites()

	// --- Then ---
	assert.Len(t, 3, have)
	assert.Equal(t, "s1", have[0].ID)
}

func Test_Devices(t *testing.T) {
	// --- When ---
	have := Devices()

	// --- Then ---
	assert.Len(t, 6, have)
	assert.Nil(t, have[3].LastSeen)
	assert.NotNil(t, have[0].LastSeen)
}

func Test_Generated(t *testing.T) {
	// --- When ---
	have := Generated(8)

	// --- Then ---
	assert.Len(t, 8, have)
	assert.Equal(t, "g0001", have[0].ID)
	assert.Equal(t, "GN-0008", have[7].Serial)
	assert.Equal(t, "s2", have[1].SiteID)
	assert.Equal(t, "H-10", have[2].Model)
	assert.Nil(t, have[6].LastSeen)
	assert.NotNil(t, have[7].LastSeen)
}

func Test_Handler(t *testing.T) {
	t.Run("extra devices listed and found", func(t *testing.T) {
		// --- Given ---
		hnd := Handler(3)
		req := httptest.NewRequest(http.MethodGet, "/devices/g0003", nil)
		rec := httptest.NewRecorder()

		// --- When ---
		hnd.ServeHTTP(rec, req)

		// --- Then ---
		assert.Equal(t, http.StatusOK, rec.Code)
		assert.Contain(t, `"serial":"GN-0003"`, rec.Body.String())
	})
}

func Test_Handler_tabular(t *testing.T) {
	tt := []struct {
		testN string

		path   string
		status int
		body   string
	}{
		{
			"sites",
			"/sites",
			http.StatusOK,
			`"name":"North Yard"`,
		},
		{
			"devices",
			"/devices",
			http.StatusOK,
			`"id":"d6"`,
		},
		{
			"devices of a site",
			"/devices?site=s2",
			http.StatusOK,
			`{"items":[{"id":"d3",`,
		},
		{
			"device",
			"/devices/d4",
			http.StatusOK,
			`{"id":"d4","serial":"SN-0004",`,
		},
		{
			"unknown device",
			"/devices/d9",
			http.StatusNotFound,
			`{"error":"no such device"}`,
		},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- Given ---
			req := httptest.NewRequest(http.MethodGet, tc.path, nil)
			rec := httptest.NewRecorder()

			// --- When ---
			Handler(0).ServeHTTP(rec, req)

			// --- Then ---
			assert.Equal(t, tc.status, rec.Code)
			assert.Contain(t, tc.body, rec.Body.String())
		})
	}
}
