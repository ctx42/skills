// Command fleet serves the fleet frontend and its API.
//
// Configuration comes from environment variables:
//
//	FLEET_ADDR          listen address (default ":8080")
//	FLEET_UPSTREAM_URL  fleet inventory base URL
//	                    (default "http://localhost:8191")
//	FLEET_REQUEST_LOG   a file to append one "METHOD /path" line to per
//	                    request; no log without it
package main

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/ctx42/ring/pkg/ring"

	"example.com/fleet/internal/server"
	"example.com/fleet/internal/upstream"
	"example.com/fleet/web"
)

// Environment variables and their defaults.
const (
	envAddr     = "FLEET_ADDR"
	envUpstream = "FLEET_UPSTREAM_URL"
	envLog      = "FLEET_REQUEST_LOG"
	defAddr     = ":8080"
	defUpstream = "http://localhost:8191"
)

// shutdownTimeout bounds how long in-flight requests may finish on exit.
const shutdownTimeout = 5 * time.Second

// The inventory client is what the API reads from.
var _ server.Inventory = (*upstream.Client)(nil)

func main() {
	sig := []os.Signal{os.Interrupt, syscall.SIGTERM}
	ctx, stop := signal.NotifyContext(context.Background(), sig...)
	rng := ring.New()
	err := run(ctx, rng)
	stop()
	if err != nil {
		_, _ = fmt.Fprintf(rng.Stderr(), "fleet: %s\n", err)
		os.Exit(1)
	}
}

// run serves the application configured by the environment of rng until ctx
// is cancelled, then shuts down gracefully.
func run(ctx context.Context, rng *ring.Ring) error {
	dist, err := web.Dist()
	if err != nil {
		return err
	}
	inv := upstream.New(env(rng, envUpstream, defUpstream))
	hnd := server.New(inv, dist)
	if path := rng.EnvGet(envLog); path != "" {
		flag := os.O_APPEND | os.O_CREATE | os.O_WRONLY
		var log *os.File
		if log, err = os.OpenFile(path, flag, 0o644); err != nil {
			return fmt.Errorf("request log: %w", err)
		}
		defer func() { _ = log.Close() }()
		hnd = server.Logged(hnd, log)
	}
	hs := &http.Server{
		Addr:              env(rng, envAddr, defAddr),
		Handler:           hnd,
		ReadHeaderTimeout: 10 * time.Second,
	}
	done := make(chan error, 1)
	go func() { done <- hs.ListenAndServe() }()
	select {
	case err = <-done:
		return err

	case <-ctx.Done():
	}
	sctx, cancel := context.WithTimeout(context.Background(), shutdownTimeout)
	defer cancel()
	if err = hs.Shutdown(sctx); err != nil {
		return err
	}
	if err = <-done; !errors.Is(err, http.ErrServerClosed) {
		return err
	}
	return nil
}

// env returns the environment variable key of rng, or def when it is unset
// or empty.
func env(rng *ring.Ring, key, def string) string {
	if val := rng.EnvGet(key); val != "" {
		return val
	}
	return def
}
