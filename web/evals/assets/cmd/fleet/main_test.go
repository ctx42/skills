package main

import (
	"context"
	"net"
	"net/http"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/ctx42/ring/pkg/ring"
	"github.com/ctx42/testing/pkg/assert"
	"github.com/ctx42/testing/pkg/must"
	"github.com/ctx42/testkit/pkg/httpkit"
)

func Test_run(t *testing.T) {
	t.Run("serves until cancelled", func(t *testing.T) {
		// --- Given ---
		ctx, cancel := context.WithCancel(t.Context())
		lis := must.Value(net.Listen("tcp", "127.0.0.1:0"))
		addr := lis.Addr().String()
		must.Nil(lis.Close())

		inv := httpkit.NewServer(t).Rsp(http.StatusOK, []byte(`{"items":[]}`))
		env := []string{envAddr + "=" + addr, envUpstream + "=" + inv.URL()}
		rng := ring.New(ring.WithEnv(env))

		done := make(chan error, 1)
		go func() { done <- run(ctx, rng) }()
		var rsp *http.Response
		up := func() bool {
			var err error
			rsp, err = http.Get("http://" + addr + "/api/sites")
			return err == nil
		}
		assert.Wait(t, 5*time.Second, up)
		must.Nil(rsp.Body.Close())

		// --- When ---
		cancel()

		// --- Then ---
		assert.NoError(t, <-done)
		assert.Equal(t, http.StatusOK, rsp.StatusCode)
	})

	t.Run("logs requests", func(t *testing.T) {
		// --- Given ---
		ctx, cancel := context.WithCancel(t.Context())
		lis := must.Value(net.Listen("tcp", "127.0.0.1:0"))
		addr := lis.Addr().String()
		must.Nil(lis.Close())

		log := filepath.Join(t.TempDir(), "requests.log")
		inv := httpkit.NewServer(t).Rsp(http.StatusOK, []byte(`{"items":[]}`))
		env := []string{
			envAddr + "=" + addr,
			envUpstream + "=" + inv.URL(),
			envLog + "=" + log,
		}
		rng := ring.New(ring.WithEnv(env))

		done := make(chan error, 1)
		go func() { done <- run(ctx, rng) }()
		up := func() bool {
			rsp, err := http.Get("http://" + addr + "/api/sites")
			if err == nil {
				_ = rsp.Body.Close()
			}
			return err == nil
		}
		assert.Wait(t, 5*time.Second, up)

		// --- When ---
		cancel()

		// --- Then ---
		assert.NoError(t, <-done)
		have := string(must.Value(os.ReadFile(log)))
		assert.Equal(t, "GET /api/sites\n", have)
	})

	t.Run("error - request log not writable", func(t *testing.T) {
		// --- Given ---
		log := filepath.Join(t.TempDir(), "missing", "requests.log")
		rng := ring.New(ring.WithEnv([]string{envLog + "=" + log}))

		// --- When ---
		err := run(t.Context(), rng)

		// --- Then ---
		assert.ErrorContain(t, "request log: open", err)
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

func Test_env_tabular(t *testing.T) {
	tt := []struct {
		testN string

		env  []string
		want string
	}{
		{"set", []string{envAddr + "=:9000"}, ":9000"},
		{"empty", []string{envAddr + "="}, defAddr},
		{"unset", nil, defAddr},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- Given ---
			rng := ring.New(ring.WithEnv(tc.env))

			// --- When ---
			have := env(rng, envAddr, defAddr)

			// --- Then ---
			assert.Equal(t, tc.want, have)
		})
	}
}
