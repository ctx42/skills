// Command fake-upstream serves the fake fleet inventory of package fake.
// FAKE_ADDR sets the listen address (default "localhost:8191"), and
// FAKE_DEVICES how many generated devices it holds beyond the fixed ones
// (default 0).
package main

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"

	"github.com/ctx42/ring/pkg/ring"

	"example.com/fleet/internal/fake"
)

// Environment variables and the address default.
const (
	envAddr    = "FAKE_ADDR"
	envDevices = "FAKE_DEVICES"
	defAddr    = "localhost:8191"
)

func main() {
	sig := []os.Signal{os.Interrupt, syscall.SIGTERM}
	ctx, stop := signal.NotifyContext(context.Background(), sig...)
	rng := ring.New()
	err := run(ctx, rng)
	stop()
	if err != nil {
		_, _ = fmt.Fprintf(rng.Stderr(), "fake-upstream: %s\n", err)
		os.Exit(1)
	}
}

// run serves the fake inventory at the address the environment of rng sets
// until ctx is cancelled.
func run(ctx context.Context, rng *ring.Ring) error {
	extra := 0
	if val := rng.EnvGet(envDevices); val != "" {
		var err error
		if extra, err = strconv.Atoi(val); err != nil || extra < 0 {
			return fmt.Errorf("%s: not a count: %q", envDevices, val)
		}
	}
	addr := rng.EnvGet(envAddr)
	if addr == "" {
		addr = defAddr
	}
	hs := &http.Server{
		Addr:              addr,
		Handler:           fake.Handler(extra),
		ReadHeaderTimeout: 10 * time.Second,
	}
	done := make(chan error, 1)
	go func() { done <- hs.ListenAndServe() }()
	select {
	case err := <-done:
		return err

	case <-ctx.Done():
	}
	if err := hs.Close(); err != nil {
		return err
	}
	if err := <-done; !errors.Is(err, http.ErrServerClosed) {
		return err
	}
	return nil
}
