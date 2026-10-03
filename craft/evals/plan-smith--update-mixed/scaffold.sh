#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
cat > go.mod <<'EOF_0'
module example.com/svc

go 1.22
EOF_0
mkdir -p cmd/svc
cat > cmd/svc/main.go <<'EOF_1'
// Command svc serves the operator API.
package main

import (
	"log"
	"net/http"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
	})
	log.Fatal(http.ListenAndServe(":8080", mux))
}
EOF_1
cat > sso-plan.md <<'EOF_2'
# SSO plan

## Summary

| #  | Item              | Status |
|----|-------------------|--------|
| 1  | Provider config   | N      |
| 2  | Login flow        | N      |
| 3  | Session storage   | N      |
| 4  | Operator docs     | N      |

Legend: Y implemented · N not yet · X rejected

## 1. Provider config — [ ]

Read the OIDC issuer, client ID, and client secret from the environment and
validate them at startup. The secret never appears in logs or in the config
dump endpoint.

Done when: the server refuses to start with a missing or malformed issuer, and
`GET /debug/config` redacts the secret.

## 2. Login flow — [ ]

Authorization-code flow with PKCE. `/login` redirects to the provider,
`/callback` exchanges the code and establishes a session.

Done when: a full round trip against the staging provider lands an
authenticated user on the post-login page, and a replayed code is rejected.

## 3. Session storage — [ ]

Sessions live in Redis, keyed by an opaque session ID, with a 12-hour TTL. The
cookie carries only the ID.

Done when: a session survives an app restart, expires on its own after 12
hours, and logout deletes the key.

## 4. Operator docs — [ ]

A page in the operator manual covering the environment variables, the redirect
URI the provider must whitelist, and how to rotate the client secret.

Done when: someone who has not seen this work can configure SSO from the page
alone.
EOF_2
git add -A && git commit -q -m 'docs: add SSO plan'
git checkout -q -b feat/login-flow
mkdir -p auth
cat > auth/login.go <<'EOF_3'
// Package auth implements the SSO login flow.
package auth

import (
	"context"
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"net/http"
	"net/url"
	"sync"
)

// Exchanger trades an authorization code and its PKCE verifier for the
// authenticated subject.
type Exchanger interface {
	Exchange(ctx context.Context, code, verifier string) (subject string, err error)
}

// Sessions establishes a session for an authenticated subject.
type Sessions interface {
	Create(ctx context.Context, subject string) (id string, err error)
}

// Flow is the authorization-code flow with PKCE.
type Flow struct {
	AuthURL     string
	ClientID    string
	RedirectURI string
	Exchanger   Exchanger
	Sessions    Sessions

	mu        sync.Mutex
	verifiers map[string]string // state -> PKCE verifier
	used      map[string]bool   // codes already exchanged
}

// Login redirects the browser to the provider with a fresh state and a
// S256 code challenge.
func (f *Flow) Login(w http.ResponseWriter, r *http.Request) {
	state, verifier := random(), random()
	sum := sha256.Sum256([]byte(verifier))
	f.mu.Lock()
	if f.verifiers == nil {
		f.verifiers = map[string]string{}
	}
	f.verifiers[state] = verifier
	f.mu.Unlock()
	q := url.Values{
		"response_type":         {"code"},
		"client_id":             {f.ClientID},
		"redirect_uri":          {f.RedirectURI},
		"state":                 {state},
		"code_challenge":        {base64.RawURLEncoding.EncodeToString(sum[:])},
		"code_challenge_method": {"S256"},
	}
	http.Redirect(w, r, f.AuthURL+"?"+q.Encode(), http.StatusFound)
}

// Callback exchanges the code, rejects a replayed one, and sets the session
// cookie.
func (f *Flow) Callback(w http.ResponseWriter, r *http.Request) {
	code, state := r.URL.Query().Get("code"), r.URL.Query().Get("state")
	f.mu.Lock()
	verifier, ok := f.verifiers[state]
	replay := f.used[code]
	if ok && !replay {
		if f.used == nil {
			f.used = map[string]bool{}
		}
		f.used[code] = true
		delete(f.verifiers, state)
	}
	f.mu.Unlock()
	if !ok || replay {
		http.Error(w, "invalid or replayed code", http.StatusBadRequest)
		return
	}
	subject, err := f.Exchanger.Exchange(r.Context(), code, verifier)
	if err != nil {
		http.Error(w, "exchange failed", http.StatusBadGateway)
		return
	}
	id, err := f.Sessions.Create(r.Context(), subject)
	if err != nil {
		http.Error(w, "session failed", http.StatusInternalServerError)
		return
	}
	http.SetCookie(w, &http.Cookie{Name: "sid", Value: id, HttpOnly: true, Secure: true, Path: "/"})
	http.Redirect(w, r, "/home", http.StatusFound)
}

func random() string {
	b := make([]byte, 32)
	_, _ = rand.Read(b)
	return base64.RawURLEncoding.EncodeToString(b)
}
EOF_3
mkdir -p auth
cat > auth/login_test.go <<'EOF_4'
package auth

import (
	"context"
	"net/http"
	"net/http/httptest"
	"net/url"
	"testing"
)

type fakeExchanger struct{}

func (fakeExchanger) Exchange(context.Context, string, string) (string, error) { return "alice", nil }

type fakeSessions struct{}

func (fakeSessions) Create(context.Context, string) (string, error) { return "sid-1", nil }

func newFlow() *Flow {
	return &Flow{AuthURL: "https://idp.example/authorize", ClientID: "svc",
		RedirectURI: "https://svc.example/callback", Exchanger: fakeExchanger{}, Sessions: fakeSessions{}}
}

func login(t *testing.T, f *Flow) string {
	t.Helper()
	rec := httptest.NewRecorder()
	f.Login(rec, httptest.NewRequest(http.MethodGet, "/login", nil))
	loc, _ := url.Parse(rec.Header().Get("Location"))
	return loc.Query().Get("state")
}

func Test_Login_RedirectsWithPKCE(t *testing.T) {
	f := newFlow()
	rec := httptest.NewRecorder()
	f.Login(rec, httptest.NewRequest(http.MethodGet, "/login", nil))
	if rec.Code != http.StatusFound {
		t.Fatalf("want 302, have %d", rec.Code)
	}
	loc, _ := url.Parse(rec.Header().Get("Location"))
	if loc.Query().Get("code_challenge_method") != "S256" {
		t.Fatal("want S256 code challenge")
	}
}

func Test_Callback_ExchangesCodeAndSetsSession(t *testing.T) {
	f := newFlow()
	state := login(t, f)
	rec := httptest.NewRecorder()
	f.Callback(rec, httptest.NewRequest(http.MethodGet, "/callback?code=c1&state="+state, nil))
	if rec.Code != http.StatusFound || rec.Header().Get("Location") != "/home" {
		t.Fatalf("want redirect to /home, have %d %s", rec.Code, rec.Header().Get("Location"))
	}
}

func Test_Callback_RejectsReplayedCode(t *testing.T) {
	f := newFlow()
	state := login(t, f)
	f.Callback(httptest.NewRecorder(), httptest.NewRequest(http.MethodGet, "/callback?code=c1&state="+state, nil))
	state2 := login(t, f)
	rec := httptest.NewRecorder()
	f.Callback(rec, httptest.NewRequest(http.MethodGet, "/callback?code=c1&state="+state2, nil))
	if rec.Code != http.StatusBadRequest {
		t.Fatalf("want 400 for a replayed code, have %d", rec.Code)
	}
}
EOF_4
git add -A && git commit -q -m 'feat(auth): authorization-code login flow with PKCE'
git checkout -q main && git merge -q --no-ff feat/login-flow -m 'Merge pull request #41 from feat/login-flow'
git checkout -q -b feat/session-storage
mkdir -p session
cat > session/store.go <<'EOF_5'
// Package session keeps login sessions in Redis.
package session

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"time"

	"github.com/redis/go-redis/v9"
)

// TTL is how long a session lives without being renewed.
const TTL = 12 * time.Hour

// Store keeps sessions in Redis keyed by an opaque session ID; the cookie
// carries only that ID.
type Store struct{ rdb *redis.Client }

// New returns a Store backed by rdb.
func New(rdb *redis.Client) *Store { return &Store{rdb: rdb} }

// Create stores a session for subject and returns its opaque ID.
func (s *Store) Create(ctx context.Context, subject string) (string, error) {
	b := make([]byte, 32)
	if _, err := rand.Read(b); err != nil {
		return "", err
	}
	id := hex.EncodeToString(b)
	return id, s.rdb.Set(ctx, key(id), subject, TTL).Err()
}

// Get returns the subject of session id.
func (s *Store) Get(ctx context.Context, id string) (string, error) {
	return s.rdb.Get(ctx, key(id)).Result()
}

// Logout deletes session id.
func (s *Store) Logout(ctx context.Context, id string) error {
	return s.rdb.Del(ctx, key(id)).Err()
}

func key(id string) string { return "session:" + id }
EOF_5
mkdir -p session
cat > session/store_test.go <<'EOF_6'
package session

import (
	"context"
	"testing"
	"time"

	"github.com/alicebob/miniredis/v2"
	"github.com/redis/go-redis/v9"
)

func Test_Create_SetsTwelveHourTTL(t *testing.T) {
	mr := miniredis.RunT(t)
	s := New(redis.NewClient(&redis.Options{Addr: mr.Addr()}))
	id, _ := s.Create(context.Background(), "alice")
	if have := mr.TTL("session:" + id); have != 12*time.Hour {
		t.Fatalf("want 12h TTL, have %s", have)
	}
	mr.FastForward(12*time.Hour + time.Second)
	if _, err := s.Get(context.Background(), id); err == nil {
		t.Fatal("want the session expired after 12 hours")
	}
}

func Test_Session_SurvivesAppRestart(t *testing.T) {
	mr := miniredis.RunT(t)
	id, _ := New(redis.NewClient(&redis.Options{Addr: mr.Addr()})).Create(context.Background(), "alice")
	restarted := New(redis.NewClient(&redis.Options{Addr: mr.Addr()}))
	if have, err := restarted.Get(context.Background(), id); err != nil || have != "alice" {
		t.Fatalf("want the session after a restart, have %q %v", have, err)
	}
}

func Test_Logout_DeletesKey(t *testing.T) {
	mr := miniredis.RunT(t)
	s := New(redis.NewClient(&redis.Options{Addr: mr.Addr()}))
	id, _ := s.Create(context.Background(), "alice")
	_ = s.Logout(context.Background(), id)
	if mr.Exists("session:" + id) {
		t.Fatal("want the key deleted on logout")
	}
}
EOF_6
git add -A && git commit -q -m 'feat(session): Redis session storage with 12h TTL'
git checkout -q main && git merge -q --no-ff feat/session-storage -m 'Merge pull request #44 from feat/session-storage'
mkdir -p ci/logs
cat > ci/logs/staging-e2e-2026-09-30.log <<'EOF_7'
2026-09-30T02:14:07Z job=staging-e2e commit=main provider=https://idp.staging.example
2026-09-30T02:14:09Z RUN  sso/login_round_trip
2026-09-30T02:14:11Z      GET /login -> 302 https://idp.staging.example/authorize (code_challenge_method=S256)
2026-09-30T02:14:13Z      provider login as e2e-operator -> 302 /callback
2026-09-30T02:14:13Z      GET /callback -> 302 /home (cookie sid set)
2026-09-30T02:14:14Z      GET /home -> 200 authenticated as e2e-operator
2026-09-30T02:14:14Z PASS sso/login_round_trip (5.1s)
2026-09-30T02:14:15Z RUN  sso/replayed_code
2026-09-30T02:14:15Z      GET /callback (same code again) -> 400 invalid or replayed code
2026-09-30T02:14:15Z PASS sso/replayed_code (0.4s)
2026-09-30T02:14:15Z ok   staging-e2e 2 passed, 0 failed
EOF_7
git add -A && git commit -q -m 'ci: keep the staging e2e log'
