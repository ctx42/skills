package upstream

import (
	"net/http"
	"testing"
	"time"

	"github.com/ctx42/testing/pkg/assert"
	"github.com/ctx42/testkit/pkg/httpkit"
)

// devicesRsp is an inventory answer listing one device.
const devicesRsp = `{
  "items": [
    {
      "id": "d1",
      "serial": "SN-0001",
      "site_id": "s1",
      "model": "T-100",
      "added": "2026-01-05T08:00:00Z"
    }
  ]
}`

// unreachable is a base URL nothing listens on.
const unreachable = "http://127.0.0.1:1"

// testDevice is the device devicesRsp lists.
var testDevice = Device{
	ID:     "d1",
	Serial: "SN-0001",
	SiteID: "s1",
	Model:  "T-100",
	Added:  time.Date(2026, time.January, 5, 8, 0, 0, 0, time.UTC),
}

func Test_New(t *testing.T) {
	// --- When ---
	have := New("http://inv.test")

	// --- Then ---
	assert.Equal(t, "http://inv.test", have.base)
	assert.Equal(t, timeout, have.hc.Timeout)
	assert.Fields(t, 2, have)
}

func Test_Client_Devices(t *testing.T) {
	t.Run("every site", func(t *testing.T) {
		// --- Given ---
		srv := httpkit.NewServer(t).Rsp(http.StatusOK, []byte(devicesRsp))
		cli := New(srv.URL())

		// --- When ---
		have, err := cli.Devices(t.Context(), "")

		// --- Then ---
		assert.NoError(t, err)
		assert.Equal(t, []Device{testDevice}, have)
		assert.Equal(t, "/devices", srv.Request(0).URL.RequestURI())
	})

	t.Run("one site", func(t *testing.T) {
		// --- Given ---
		srv := httpkit.NewServer(t).Rsp(http.StatusOK, []byte(devicesRsp))
		cli := New(srv.URL())

		// --- When ---
		_, err := cli.Devices(t.Context(), "s 1")

		// --- Then ---
		assert.NoError(t, err)

		have := srv.Request(0).URL.RequestURI()
		assert.Equal(t, "/devices?site=s+1", have)
	})

	t.Run("error - status", func(t *testing.T) {
		// --- Given ---
		srv := httpkit.NewServer(t).Rsp(http.StatusInternalServerError, nil)
		cli := New(srv.URL())

		// --- When ---
		have, err := cli.Devices(t.Context(), "")

		// --- Then ---
		want := "inventory: GET /devices: 500 Internal Server Error"
		assert.ErrorEqual(t, want, err)
		assert.Nil(t, have)
	})
}

func Test_Client_Device(t *testing.T) {
	t.Run("found", func(t *testing.T) {
		// --- Given ---
		rsp := `{"id": "d1", "added": "2026-01-05T08:00:00Z"}`
		srv := httpkit.NewServer(t).Rsp(http.StatusOK, []byte(rsp))
		cli := New(srv.URL())

		// --- When ---
		have, err := cli.Device(t.Context(), "d1")

		// --- Then ---
		assert.NoError(t, err)
		assert.Equal(t, "d1", have.ID)
		assert.Equal(t, "/devices/d1", srv.Request(0).URL.RequestURI())
	})

	t.Run("error - not found", func(t *testing.T) {
		// --- Given ---
		srv := httpkit.NewServer(t).Rsp(http.StatusNotFound, nil)
		cli := New(srv.URL())

		// --- When ---
		_, err := cli.Device(t.Context(), "d9")

		// --- Then ---
		assert.ErrorIs(t, ErrNotFound, err)
	})
}

func Test_Client_Site(t *testing.T) {
	t.Run("found", func(t *testing.T) {
		// --- Given ---
		rsp := `{"id": "s1", "name": "North Yard", "city": "Zurich"}`
		srv := httpkit.NewServer(t).Rsp(http.StatusOK, []byte(rsp))
		cli := New(srv.URL())

		// --- When ---
		have, err := cli.Site(t.Context(), "s1")

		// --- Then ---
		assert.NoError(t, err)
		want := Site{ID: "s1", Name: "North Yard", City: "Zurich"}
		assert.Equal(t, want, have)
		assert.Equal(t, "/sites/s1", srv.Request(0).URL.RequestURI())
	})

	t.Run("error - not found", func(t *testing.T) {
		// --- Given ---
		srv := httpkit.NewServer(t).Rsp(http.StatusNotFound, nil)
		cli := New(srv.URL())

		// --- When ---
		_, err := cli.Site(t.Context(), "s9")

		// --- Then ---
		assert.ErrorIs(t, ErrNotFound, err)
	})
}

func Test_Client_Sites(t *testing.T) {
	t.Run("listed", func(t *testing.T) {
		// --- Given ---
		rsp := `{"items": [{"id": "s1", "name": "North Yard"}]}`
		srv := httpkit.NewServer(t).Rsp(http.StatusOK, []byte(rsp))
		cli := New(srv.URL())

		// --- When ---
		have, err := cli.Sites(t.Context())

		// --- Then ---
		assert.NoError(t, err)
		want := []Site{{ID: "s1", Name: "North Yard"}}
		assert.Equal(t, want, have)
	})

	t.Run("error - invalid JSON", func(t *testing.T) {
		// --- Given ---
		srv := httpkit.NewServer(t).Rsp(http.StatusOK, []byte("{"))
		cli := New(srv.URL())

		// --- When ---
		have, err := cli.Sites(t.Context())

		// --- Then ---
		assert.ErrorEqual(t, "inventory: GET /sites: unexpected EOF", err)
		assert.Nil(t, have)
	})

	t.Run("error - unreachable", func(t *testing.T) {
		// --- Given ---
		cli := New(unreachable)

		// --- When ---
		have, err := cli.Sites(t.Context())

		// --- Then ---
		assert.ErrorContain(t, "connection refused", err)
		assert.Nil(t, have)
	})

	t.Run("error - invalid base URL", func(t *testing.T) {
		// --- Given ---
		cli := New("http://in valid")

		// --- When ---
		have, err := cli.Sites(t.Context())

		// --- Then ---
		assert.ErrorContain(t, "invalid character", err)
		assert.Nil(t, have)
	})
}
