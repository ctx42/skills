#!/usr/bin/env bash
set -euo pipefail
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
cat > go.mod <<'EOF_0'
module example.com/app

go 1.22
EOF_0
mkdir -p router
cat > router/router.go <<'EOF_1'
// Package router wires the HTTP routes of the service.
package router

import (
	"net/http"

	"example.com/app/handler"
)

// New returns the service's HTTP handler.
func New() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", handler.Health)
	return mux
}
EOF_1
mkdir -p handler
cat > handler/health.go <<'EOF_2'
// Package handler holds the HTTP handlers of the service.
package handler

import "net/http"

// Health reports that the service is up.
func Health(w http.ResponseWriter, _ *http.Request) {
	w.WriteHeader(http.StatusOK)
}
EOF_2
mkdir -p user
cat > user/user.go <<'EOF_3'
// Package user looks up and authenticates users.
package user

import (
	"context"
	"errors"
)

// ErrInvalid is returned for an unknown email or a wrong password.
var ErrInvalid = errors.New("invalid credentials")

// User is an authenticated account.
type User struct {
	ID    string
	Email string
}

// Authenticate returns the user with the email when the password matches.
func Authenticate(ctx context.Context, email, password string) (User, error) {
	_ = ctx
	if email == "" || password == "" {
		return User{}, ErrInvalid
	}
	return User{ID: "u-1", Email: email}, nil
}
EOF_3
git add -A
git commit -qm 'initial'
mkdir -p router
cat > router/router.go <<'EOF_0'
// Package router wires the HTTP routes of the service.
package router

import (
	"net/http"

	"example.com/app/handler"
)

// New returns the service's HTTP handler.
func New() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", handler.Health)
	mux.HandleFunc("POST /login", handler.Login)
	return mux
}
EOF_0
mkdir -p handler
cat > handler/login.go <<'EOF_1'
package handler

import (
	"encoding/json"
	"net/http"

	"example.com/app/token"
	"example.com/app/user"
)

type loginRequest struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

type loginResponse struct {
	Token string `json:"token"`
}

// Login checks the posted credentials and answers with a signed JWT.
func Login(w http.ResponseWriter, r *http.Request) {
	var req loginRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "bad request", http.StatusBadRequest)
		return
	}
	usr, err := user.Authenticate(r.Context(), req.Email, req.Password)
	if err != nil {
		http.Error(w, "invalid credentials", http.StatusUnauthorized)
		return
	}
	tok, err := token.Issue(usr.ID)
	if err != nil {
		http.Error(w, "internal error", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(loginResponse{Token: tok})
}
EOF_1
mkdir -p token
cat > token/token.go <<'EOF_2'
// Package token issues signed JSON Web Tokens.
package token

import (
	"os"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

// TTL is how long an issued token stays valid.
const TTL = 15 * time.Minute

// Issue returns an HS256-signed JWT for the user id, valid for TTL.
func Issue(userID string) (string, error) {
	now := time.Now()
	claims := jwt.RegisteredClaims{
		Subject:   userID,
		IssuedAt:  jwt.NewNumericDate(now),
		ExpiresAt: jwt.NewNumericDate(now.Add(TTL)),
	}
	tok := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return tok.SignedString([]byte(os.Getenv("JWT_SECRET")))
}
EOF_2
git add -A
