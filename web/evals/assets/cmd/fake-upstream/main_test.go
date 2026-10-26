package main

import (
	"context"
	"io"
	"net"
	"net/http"
	"testing"
	"time"

	"github.com/ctx42/ring/pkg/ring"
	"github.com/ctx42/testing/pkg/assert"
	"github.com/ctx42/testing/pkg/must"
)

func Test_run(t *testing.T) {
	t.Run("serves until cancelled", func(t *testing.T) {
		// --- Given ---
		ctx, cancel := context.WithCancel(t.Context())
		lis := must.Value(net.Listen("tcp", "127.0.0.1:0"))
		addr := lis.Addr().String()
		must.Nil(lis.Close())

		env := []string{envAddr + "=" + addr, envDevices + "=2"}
		rng := ring.New(ring.WithEnv(env))

		done := make(chan error, 1)
		go func() { done <- run(ctx, rng) }()
		var rsp *http.Response
		up := func() bool {
			var err error
			rsp, err = http.Get("http://" + addr + "/devices/g0002")
			return err == nil
		}
		assert.Wait(t, 5*time.Second, up)
		body := string(must.Value(io.ReadAll(rsp.Body)))
		must.Nil(rsp.Body.Close())

		// --- When ---
		cancel()

		// --- Then ---
		assert.NoError(t, <-done)
		assert.Contain(t, `"serial":"GN-0002"`, body)
	})

	t.Run("error - device count not a number", func(t *testing.T) {
		// --- Given ---
		env := []string{envDevices + "=many"}
		rng := ring.New(ring.WithEnv(env))

		// --- When ---
		err := run(t.Context(), rng)

		// --- Then ---
		assert.ErrorEqual(t, `FAKE_DEVICES: not a count: "many"`, err)
	})

	t.Run("error - address in use", func(t *testing.T) {
		// --- Given ---
		lis := must.Value(net.Listen("tcp", "127.0.0.1:0"))
		t.Cleanup(func() { _ = lis.Close() })
		env := []string{envAddr + "=" + lis.Addr().String()}
		rng := ring.New(ring.WithEnv(env))

		// --- When ---
		err := run(t.Context(), rng)

		// --- Then ---
		assert.ErrorContain(t, "address already in use", err)
	})
}
