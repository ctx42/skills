// Package fake is a fake fleet inventory: it answers the inventory API from
// a fixed set of sites and devices, for the end-to-end tests.
package fake

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// Site is a site of the fake inventory.
type Site struct {
	ID   string `json:"id"`
	Name string `json:"name"`
	City string `json:"city"`
}

// Device is a device of the fake inventory.
type Device struct {
	ID       string     `json:"id"`
	Serial   string     `json:"serial"`
	SiteID   string     `json:"site_id"`
	Model    string     `json:"model"`
	Added    time.Time  `json:"added"`
	LastSeen *time.Time `json:"last_seen,omitempty"`
}

// on returns hour:minute UTC on day of month mon, 2026.
func on(mon time.Month, day, hour, minute int) time.Time {
	return time.Date(2026, mon, day, hour, minute, 0, 0, time.UTC)
}

// Sites returns the sites the fake inventory holds.
func Sites() []Site {
	return []Site{
		{ID: "s1", Name: "North Yard", City: "Zurich"},
		{ID: "s2", Name: "Harbour", City: "Basel"},
		{ID: "s3", Name: "Depot", City: "Bern"},
	}
}

// Devices returns the devices the fake inventory holds; d4 never reported.
func Devices() []Device {
	return []Device{
		{
			"d1", "SN-0001", "s1", "T-100",
			on(time.January, 5, 8, 0),
			new(on(time.October, 20, 7, 15)),
		},
		{
			"d2", "SN-0002", "s1", "T-100",
			on(time.January, 5, 8, 10),
			new(on(time.October, 21, 11, 40)),
		},
		{
			"d3", "SN-0003", "s2", "T-200",
			on(time.February, 11, 9, 30),
			new(on(time.October, 19, 22, 5)),
		},
		{
			"d4", "SN-0004", "s2", "T-200",
			on(time.March, 2, 14, 0),
			nil,
		},
		{
			"d5", "SN-0005", "s3", "H-10",
			on(time.April, 18, 6, 45),
			new(on(time.October, 22, 5, 0)),
		},
		{
			"d6", "SN-0006", "s3", "H-10",
			on(time.May, 23, 10, 20),
			new(on(time.October, 22, 5, 30)),
		},
	}
}

// Generated returns n more devices, after [Devices]: IDs "g0001" on,
// serials "GN-0001" on, spread over the sites in turn; every seventh never
// reported.
func Generated(n int) []Device {
	sites := Sites()
	models := []string{"T-100", "T-200", "H-10"}
	added := on(time.June, 1, 0, 0)
	devs := make([]Device, 0, n)
	for i := range n {
		dev := Device{
			ID:     fmt.Sprintf("g%04d", i+1),
			Serial: fmt.Sprintf("GN-%04d", i+1),
			SiteID: sites[i%len(sites)].ID,
			Model:  models[i%len(models)],
			Added:  added.Add(time.Duration(i) * time.Minute),
		}
		if i%7 != 6 {
			dev.LastSeen = new(dev.Added.Add(24 * time.Hour))
		}
		devs = append(devs, dev)
	}
	return devs
}

// Handler returns the fake inventory API over [Devices] and extra more
// [Generated] devices:
//
//	GET /sites          every site
//	GET /devices        every device, or a site's with ?site=<id>
//	GET /devices/{id}   one device; 404 for an unknown ID
func Handler(extra int) http.Handler {
	inv := &inventory{devs: append(Devices(), Generated(extra)...)}
	mux := http.NewServeMux()
	mux.HandleFunc("GET /sites", sites)
	mux.HandleFunc("GET /devices", inv.devices)
	mux.HandleFunc("GET /devices/{id}", inv.device)
	return mux
}

// inventory answers the device requests from its devices.
type inventory struct {
	devs []Device
}

// sites answers every site.
func sites(w http.ResponseWriter, _ *http.Request) {
	write(w, http.StatusOK, map[string]any{"items": Sites()})
}

// devices answers every device, or those of the site the query names.
func (inv *inventory) devices(w http.ResponseWriter, r *http.Request) {
	want := r.URL.Query().Get("site")
	items := make([]Device, 0)
	for _, dev := range inv.devs {
		if want == "" || dev.SiteID == want {
			items = append(items, dev)
		}
	}
	write(w, http.StatusOK, map[string]any{"items": items})
}

// device answers the device the path names.
func (inv *inventory) device(w http.ResponseWriter, r *http.Request) {
	for _, dev := range inv.devs {
		if dev.ID == r.PathValue("id") {
			write(w, http.StatusOK, dev)
			return
		}
	}
	rsp := map[string]string{"error": "no such device"}
	write(w, http.StatusNotFound, rsp)
}

// write answers with status and v encoded as JSON.
func write(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}
