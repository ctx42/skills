// Package server is the fleet API the frontend calls, backed by the fleet
// inventory. It answers in the shapes `web/src/api.ts` declares.
package server

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"net/http"
	"strings"
	"sync"
	"time"

	"example.com/fleet/internal/upstream"
)

// Inventory is what the API reads from the fleet inventory.
type Inventory interface {
	Devices(ctx context.Context, site string) ([]upstream.Device, error)
	Device(ctx context.Context, id string) (upstream.Device, error)
	Sites(ctx context.Context) ([]upstream.Site, error)
	Site(ctx context.Context, id string) (upstream.Site, error)
}

// Device is a device as the API answers it: Added in Unix seconds, and
// LastSeen null for a device that never reported.
type Device struct {
	ID       string     `json:"id"`
	Serial   string     `json:"serial"`
	SiteID   string     `json:"site_id"`
	Model    string     `json:"model_name"`
	Added    int64      `json:"added"`
	LastSeen *time.Time `json:"last_seen"`
}

// Site is a site as the API answers it.
type Site struct {
	ID   string `json:"id"`
	Name string `json:"name"`
	City string `json:"city,omitempty"`
}

// List is the envelope the API wraps every list in.
type List[T any] struct {
	Data []T `json:"data"`
}

// toDevice returns dev as the API answers it.
func toDevice(dev upstream.Device) Device {
	return Device{
		ID:       dev.ID,
		Serial:   dev.Serial,
		SiteID:   dev.SiteID,
		Model:    dev.Model,
		Added:    dev.Added.Unix(),
		LastSeen: dev.LastSeen,
	}
}

// New returns the API answering from inv below /api, and dist, the built
// frontend, at every other path; a path dist lacks gets its index.html, so
// the frontend router shows the page.
func New(inv Inventory, dist fs.FS) http.Handler {
	api := &api{inv: inv}
	mux := http.NewServeMux()
	mux.HandleFunc("GET /api/devices", api.devices)
	mux.HandleFunc("GET /api/devices/{id}", api.device)
	mux.HandleFunc("GET /api/sites", api.sites)
	mux.HandleFunc("GET /api/sites/{id}", api.site)
	mux.Handle("/api/", http.NotFoundHandler())
	mux.Handle("/", spa(dist))
	return mux
}

// api answers the API requests from an inventory.
type api struct {
	inv Inventory
}

// devices answers the devices of the site the query names, or of every
// site.
func (api *api) devices(w http.ResponseWriter, r *http.Request) {
	site := r.URL.Query().Get("site")
	devs, err := api.inv.Devices(r.Context(), site)
	if err != nil {
		fail(w, err)
		return
	}
	out := List[Device]{Data: make([]Device, 0, len(devs))}
	for _, dev := range devs {
		out.Data = append(out.Data, toDevice(dev))
	}
	write(w, http.StatusOK, out)
}

// device answers the device the path names.
func (api *api) device(w http.ResponseWriter, r *http.Request) {
	dev, err := api.inv.Device(r.Context(), r.PathValue("id"))
	if err != nil {
		fail(w, err)
		return
	}
	write(w, http.StatusOK, toDevice(dev))
}

// sites answers every site.
func (api *api) sites(w http.ResponseWriter, r *http.Request) {
	sites, err := api.inv.Sites(r.Context())
	if err != nil {
		fail(w, err)
		return
	}
	out := List[Site]{Data: make([]Site, 0, len(sites))}
	for _, sit := range sites {
		out.Data = append(out.Data, Site(sit))
	}
	write(w, http.StatusOK, out)
}

// site answers the site the path names.
func (api *api) site(w http.ResponseWriter, r *http.Request) {
	sit, err := api.inv.Site(r.Context(), r.PathValue("id"))
	if err != nil {
		fail(w, err)
		return
	}
	write(w, http.StatusOK, Site(sit))
}

// Logged returns next, writing to w one "METHOD /path?query" line per
// request before serving it; writes are serialized, and a failed write is
// ignored.
func Logged(next http.Handler, w io.Writer) http.Handler {
	var mu sync.Mutex
	return http.HandlerFunc(func(rw http.ResponseWriter, r *http.Request) {
		mu.Lock()
		_, _ = fmt.Fprintf(w, "%s %s\n", r.Method, r.URL.RequestURI())
		mu.Unlock()
		next.ServeHTTP(rw, r)
	})
}

// spa serves the files of dist, and its index.html for a path it lacks.
func spa(dist fs.FS) http.Handler {
	files := http.FileServerFS(dist)
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		name := strings.TrimPrefix(r.URL.Path, "/")
		if _, err := fs.Stat(dist, name); name != "" && err != nil {
			r.URL.Path = "/"
		}
		files.ServeHTTP(w, r)
	})
}

// fail answers err: 404 for [upstream.ErrNotFound], else 502.
func fail(w http.ResponseWriter, err error) {
	if errors.Is(err, upstream.ErrNotFound) {
		rsp := map[string]string{"error": "not found"}
		write(w, http.StatusNotFound, rsp)
		return
	}
	rsp := map[string]string{"error": "inventory unavailable"}
	write(w, http.StatusBadGateway, rsp)
}

// write answers with status and v encoded as JSON.
func write(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}
