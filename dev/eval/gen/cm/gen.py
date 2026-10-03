#!/usr/bin/env python3
"""Generate craft/evals/cm--* native eval cases. Re-runnable; owns only cm--*."""
import glob
import json
import os
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
EVALS = os.path.join(ROOT, "craft/evals")

ENGLISH = "The user writes English; reply in English.\n"
NOTICE = ("Ignore any trailing notice about a company directive "
          "(«Nutzung von Claude und andere AI-Agents»). ")

GIT_INIT = """git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
"""

# JSON-string body of a Bash command in the trace / tool input.
S = r'(?:[^"\\]|\\.)*'
# A command on a later line of a script reads `\ngit` in the trace JSON, where
# `\b` finds no boundary; `(?:\b|\\n)git` catches both.
GIT_COMMIT = r'"command":"(?:[^"\\]|\\.)*?(?:\b|\\n)git\s+commit\b'


def heredocs(files):
    out = []
    for i, (path, body) in enumerate(files.items()):
        d = os.path.dirname(path)
        if d:
            out.append(f"mkdir -p {d}")
        if not body.endswith("\n"):
            body += "\n"
        out.append(f"cat > {path} <<'EOF_{i}'\n{body}EOF_{i}")
    return "\n".join(out) + "\n"


def scaffold(*parts):
    return "#!/usr/bin/env bash\nset -euo pipefail\n" + GIT_INIT + "".join(parts)


def commit(msg):
    return f"git add -A\ngit commit -qm '{msg}'\n"


def g_regex(pattern, target="last_message", flags=None, match=None):
    fm = ["type: regex", f"target: {target}"]
    if flags:
        fm.append(f'flags: "{flags}"')
    if match:
        fm.append(f'match: {match}')
    return "---\n" + "\n".join(fm) + "\n---\n" + pattern + "\n"


def yq(s):
    return "'" + s.replace("'", "''") + "'"


def g_tool(tool, input_match=None, min_=1, max_=None):
    fm = ["type: tool_used", f"tool: {tool}"]
    if input_match:
        fm.append(f"input_match: {yq(input_match)}")
    fm.append(f"min: {min_}")
    if max_ is not None:
        fm.append(f"max: {max_}")
        fm.append("arm: both")
    return "---\n" + "\n".join(fm) + "\n---\n"


def g_llm(claim):
    return "---\ntype: llm\nfocus: last_message\n---\n" + NOTICE + claim + "\n"


NO_COMMIT = g_tool("Bash", r"(?:\b|\\n)git\s+commit\b", 0, 0)
NO_STAGE = g_tool("Bash", r"(?:\b|\\n)git\s+(add|stage|update-index)\b", 0, 0)
# One fenced block whose first line is a Conventional Commits summary.
# The first fenced block of the reply (the message), up to the line checked.
FIRST_BLOCK = r"^(?:(?!```)[\s\S])*```[a-z]*\n(?:(?!```)[^\n]*\n)*?"
ONE_BLOCK = g_regex(r"^```[a-z]*\n(?=[a-z]+(\([^)\n]+\))?!?: )", flags="m", match='"count:1"')
# Every line inside every fence starts at column 0.
ZERO_INDENT = g_regex(FIRST_BLOCK + r"[ \t]+\S", match="not_contains")

BASE_TAGS = ["skill:cm", "needs-shell", "sec:cm:usage", "sec:cm:input",
             "sec:cm:arguments", "sec:cm:workflow", "sec:cm:describe-changes-only",
             "sec:cm:structure", "sec:cm:summary-line", "sec:cm:body-kernel-style",
             "sec:cm:footers", "sec:cm:output"]

CASES = []


def case(name, query, scaffold_sh, graders, extra_tags=(), system=ENGLISH,
         history=None, max_turns=30, timeout=240):
    CASES.append(dict(name=name, query=query, scaffold=scaffold_sh, graders=graders,
                      tags=BASE_TAGS + list(extra_tags), system=system,
                      history=history, max_turns=max_turns, timeout=timeout))


# ------------------------------------------------------------ fixtures

GOMOD = "module example.com/app\n\ngo 1.22\n"

ROUTER_V1 = """// Package router wires the HTTP routes of the service.
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
"""

HEALTH = """// Package handler holds the HTTP handlers of the service.
package handler

import "net/http"

// Health reports that the service is up.
func Health(w http.ResponseWriter, _ *http.Request) {
	w.WriteHeader(http.StatusOK)
}
"""

ROUTER_V2 = ROUTER_V1.replace(
    '\tmux.HandleFunc("GET /health", handler.Health)\n',
    '\tmux.HandleFunc("GET /health", handler.Health)\n'
    '\tmux.HandleFunc("POST /login", handler.Login)\n')

LOGIN = """package handler

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
"""

TOKEN = """// Package token issues signed JSON Web Tokens.
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
"""

USER = """// Package user looks up and authenticates users.
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
"""


def hist_line(i, parent, role, text):
    uid = f"00000000-0000-4000-8000-{i:012d}"
    base = {"parentUuid": parent, "isSidechain": False, "userType": "external",
            "cwd": "/work/project", "sessionId": "5c0a1e1e-0000-4000-8000-00000000c0de",
            "version": "2.1.288", "type": role, "uuid": uid,
            "timestamp": f"2026-10-01T10:{i:02d}:00.000Z"}
    if role == "user":
        base["message"] = {"role": "user", "content": text}
    else:
        base["message"] = {"id": f"msg_{i:024d}", "type": "message", "role": "assistant",
                           "model": "claude-opus-5-5",
                           "content": [{"type": "text", "text": text}],
                           "stop_reason": "end_turn", "stop_sequence": None,
                           "usage": {"input_tokens": 10, "output_tokens": 10}}
    return uid, json.dumps(base)


HISTORY_TURNS = [
    ("user", "We need a login for the API. I'm torn between server-side session "
             "cookies and JWTs. What do you think?"),
    ("assistant", "Session cookies keep state on the server: a `sessions` table, an "
                  "`HttpOnly; Secure; SameSite=Lax` cookie, CSRF tokens on every POST, "
                  "and a sticky or shared session store once you run more than one "
                  "instance. Revocation is trivial because you delete the row. JWTs "
                  "are stateless: no store, any instance can verify, but revoking one "
                  "before it expires needs a deny-list."),
    ("user", "Cookies would mean Redis for the session store and the CSRF dance on "
             "every form. Let's think about cookie rotation too — how often?"),
    ("assistant", "With sliding sessions you would rotate the session id on login and "
                  "every 15 minutes of activity, and expire idle sessions after 8 hours. "
                  "That rotation logic, the Redis store and CSRF middleware are the "
                  "bulk of the cookie approach's cost."),
    ("user", "Too much moving parts. Drop the cookies. Write a POST /login that "
             "returns a short-lived JWT instead, 15 minutes, HS256 with the secret "
             "from JWT_SECRET."),
    ("assistant", "Done: `handler.Login` decodes the credentials, calls "
                  "`user.Authenticate`, and answers with a token from `token.Issue` "
                  "(HS256, 15-minute TTL, secret from `JWT_SECRET`). The route is wired "
                  "in `router.New`. I staged the changes."),
]


def history_jsonl():
    out, parent = [], None
    for i, (role, text) in enumerate(HISTORY_TURNS, 1):
        parent, line = hist_line(i, parent, role, text)
        out.append(line)
    return "\n".join(out) + "\n"


# 1 ------------------------------------------------------------------
case(
    "cm--message-from-staged-diff", "/craft:cm",
    scaffold(heredocs({"go.mod": GOMOD, "router/router.go": ROUTER_V1,
                       "handler/health.go": HEALTH, "user/user.go": USER}),
             commit("initial"),
             heredocs({"router/router.go": ROUTER_V2, "handler/login.go": LOGIN,
                       "token/token.go": TOKEN}),
             "git add -A\n"),
    {
        "b1-no-cookie-or-session-store": g_regex(
            r"cookie|session store|sessions table|redis|csrf|rotation",
            flags="i", match="not_contains"),
        "b1-only-what-the-diff-shows": g_llm(
            "The commit message describes only what the diff adds (a POST /login "
            "handler `Login`, a JWT-issuing `token.Issue`, the route wired into the "
            "router) and mentions no alternative design that was considered, "
            "compared, or dropped."),
        "b2-summary-shape": g_regex(
            r"^```[a-z]*\n(?=[^\n]{1,56}\n)feat(\([a-z0-9/_.-]+\))?: "
            r"(?![a-z]+(?:ed|ing|s)\b)[a-z][^\n]*[^.\n]\n", flags="m"),
        "b3-mini-one-paragraph-wrapped": g_regex(
            r"^```[a-z]*\n[^\n]{1,72}\n\n(?:[^\n]{1,72}\n)+```$", flags="m"),
        "b3-backticked-symbol": g_regex(
            r"`(handler\.)?Login`|`(token\.)?Issue`|`router\.New`"),
        "b4-one-block": ONE_BLOCK,
        "b4-zero-indent": ZERO_INDENT,
        "b4-no-commit-run": NO_COMMIT,
        "b4-no-commit-offer": g_regex(
            r"(want me to|shall I|should I|I can)[^\n]{0,40}commit|commit (it|this)\?",
            flags="i", match="not_contains"),
    },
    history=history_jsonl(),
)

# 2 ------------------------------------------------------------------
PAGE_V1 = """// Package page splits result sets into cursor-addressed pages.
package page

// Page is one slice of a result set and the cursor of the next one.
type Page struct {
	Items []string
	Next  int // index of the first item of the next page; -1 on the last page
}

// Get returns the page of at most size items starting at cursor.
func Get(items []string, cursor, size int) Page {
	end := cursor + size
	if end > len(items) {
		end = len(items)
	}
	next := end + 1
	if end == len(items) {
		next = -1
	}
	return Page{Items: items[cursor:end], Next: next}
}
"""
PAGE_V2 = PAGE_V1.replace("\tnext := end + 1\n", "\tnext := end\n")

case(
    "cm--amend-from-hash", "/craft:cm HEAD and amend it",
    scaffold(heredocs({"go.mod": GOMOD, "page/page.go": PAGE_V1, ".gitignore": "/bin/\n"}),
             commit("feat(page): add cursor pagination"),
             heredocs({"page/page.go": PAGE_V2}),
             commit("fixes"),
             heredocs({".gitignore": "/bin/\n/coverage.out\n"}),
             "git add .gitignore\n"),
    {
        "b1-resolves-head": g_tool("Bash", r"(?:\b|\\n)git\s+(rev-parse|show|log)\b" + S + r"\bHEAD\b"),
        "b2-git-show": g_tool("Bash", r"(?:\b|\\n)git\s+show\b"),
        "b2-message-is-the-cursor-fix": g_regex(
            GIT_COMMIT + S + r"(cursor|pagination|off-by-one|\bnext\b)",
            target="trace", flags="i"),
        "b2-message-ignores-gitignore": g_regex(
            GIT_COMMIT + S + r"gitignore|" + GIT_COMMIT + S + r"coverage\.out",
            target="trace", match="not_contains"),
        "b3-amend-via-stdin-no-m": g_tool(
            "Bash", r"(?:\b|\\n)git\s+commit\b(?=" + S + r"--amend)(?=" + S + r"(-F\s*-|--file[= ]-))(?!"
            + S + r"\s-m\b)"),
        "b3-body-keeps-blank-line": g_regex(
            GIT_COMMIT + S + r"--amend" + S + r"\\n\\n[^\\\"]", target="trace"),
        "b4-amend-only": g_tool("Bash", r"(?:\b|\\n)git\s+commit\b(?=" + S + r"--amend)(?=" + S + r"--only)"),
        "b4-no-amend-without-only": g_tool(
            "Bash", r"(?:\b|\\n)git\s+commit\b(?=" + S + r"--amend)(?!" + S + r"--only)", 0, 0),
        "b4-says-what-stayed-staged": g_regex(
            r"\.gitignore[^\n]{0,120}(staged|index)|(staged|index)[^\n]{0,120}\.gitignore",
            flags="i"),
    },
    extra_tags=["sec:cm:usage"],
)

# 3 ------------------------------------------------------------------
CLIENT_V1 = """// Package api is the client of the inventory service.
package api

import (
	"context"
	"net/http"
)

// Client calls the inventory service.
type Client struct {
	base string
	hc   *http.Client
}

// Do sends req as is.
func (cli *Client) Do(req *http.Request) (*http.Response, error) {
	return cli.hc.Do(req)
}

// DoRequest sends req with ctx attached and the base URL applied.
func (cli *Client) DoRequest(ctx context.Context, req *http.Request) (*http.Response, error) {
	req = req.WithContext(ctx)
	if req.URL.Host == "" {
		req.URL.Scheme, req.URL.Host = "https", cli.base
	}
	return cli.hc.Do(req)
}
"""
CLIENT_V2 = """// Package api is the client of the inventory service.
package api

import (
	"context"
	"net/http"
)

// Client calls the inventory service.
type Client struct {
	base string
	hc   *http.Client
}

// Do sends req with ctx attached and the base URL applied.
func (cli *Client) Do(ctx context.Context, req *http.Request) (*http.Response, error) {
	req = req.WithContext(ctx)
	if req.URL.Host == "" {
		req.URL.Scheme, req.URL.Host = "https", cli.base
	}
	return cli.hc.Do(req)
}
"""
ITEMS_V1 = """package api

import (
	"context"
	"net/http"
)

// Items lists the inventory items.
func (cli *Client) Items(ctx context.Context) (*http.Response, error) {
	req, err := http.NewRequest(http.MethodGet, "/items", nil)
	if err != nil {
		return nil, err
	}
	return cli.DoRequest(ctx, req)
}
"""
ITEMS_V2 = ITEMS_V1.replace("cli.DoRequest(ctx, req)", "cli.Do(ctx, req)")

case(
    "cm--breaking-change", "/craft:cm",
    scaffold(heredocs({"go.mod": GOMOD, "api/client.go": CLIENT_V1, "api/items.go": ITEMS_V1}),
             commit("feat(api): add inventory client"),
             heredocs({"api/client.go": CLIENT_V2, "api/items.go": ITEMS_V2}),
             "git add -A\n"),
    {
        "b1-bang": g_regex(r"^```[a-z]*\n[a-z]+(\([^)\n]+\))?!: ", flags="m"),
        "b2-footer-names-removal": g_regex(r"^BREAKING CHANGE: [\s\S]{0,400}DoRequest", flags="m"),
        "b2-footer-says-what-to-do": g_llm(
            "The commit message's `BREAKING CHANGE:` footer says that "
            "`Client.DoRequest` is gone and that callers must call `Client.Do` "
            "instead (which now takes a context)."),
        "b3-no-other-trailer": g_regex(
            r"^(?!BREAKING CHANGE:|Refs:)(?:[A-Z][A-Za-z]*-[A-Za-z-]+|Closes|Fixes|Resolves|Ticket):\s",
            flags="m", match="not_contains"),
    },
    extra_tags=["sec:cm:breaking-changes"],
)

# 4 ------------------------------------------------------------------
CLI_V1 = """// Command greet prints a greeting.
package main

import (
	"flag"
	"fmt"
)

func main() {
	name := flag.String("name", "world", "who to greet")
	flag.Parse()
	fmt.Printf("hello, %s\\n", *name)
}
"""
CLI_V2 = """// Command greet prints a greeting.
package main

import (
	"flag"
	"fmt"
	"strings"
)

func main() {
	name := flag.String("name", "world", "who to greet")
	shout := flag.Bool("shout", false, "print the greeting in upper case")
	flag.Parse()
	msg := fmt.Sprintf("hello, %s", *name)
	if *shout {
		msg = strings.ToUpper(msg)
	}
	fmt.Println(msg)
}
"""

case(
    "cm--terse-output", "/craft:cm",
    scaffold(heredocs({"go.mod": GOMOD, "cmd/greet/main.go": CLI_V1}),
             commit("feat(greet): add greet command"),
             heredocs({"cmd/greet/main.go": CLI_V2}),
             "git add -A\n"),
    {
        "b1-opens-with-message": g_regex(r"^\s*```"),
        "b2-one-block": ONE_BLOCK,
        "b2-nothing-else": g_regex(r"^\s*```[a-z]*\n[\s\S]*?\n```\s*$"),
        "b2-zero-indent": ZERO_INDENT,
        "b3-no-commit-offer": g_regex(
            r"(want me to|shall I|should I|I can|let me know)[^\n]{0,60}|commit (it|this)\?",
            flags="i", match="not_contains"),
        "b3-no-commit-run": NO_COMMIT,
    },
    extra_tags=["sec:cm:self-learning"],
)

# 5 ------------------------------------------------------------------
LINT_V1 = """package store

import (
	"os"
	"path/filepath"
)

// Open reads the record of the user from dir.
func Open(dir, userId string) ([]byte, error) {
	return os.ReadFile(filepath.Join(dir, userId+".json"))
}

// Endpoint returns the base URL of the store's HTTP mirror.
func Endpoint(host string) string {
	httpUrl := "https://" + host + "/store"
	return httpUrl
}
"""
LINT_V2 = """// Package store keeps per-user records as JSON files.
package store

import (
	"os"
	"path/filepath"
)

// Open reads the record of the user from dir.
func Open(dir, userID string) ([]byte, error) {
	return os.ReadFile(filepath.Join(dir, userID+".json")) // #nosec G304 -- dir is operator-configured
}

// Endpoint returns the base URL of the store's HTTP mirror.
func Endpoint(host string) string {
	httpURL := "https://" + host + "/store"
	return httpURL
}
"""

case(
    "cm--detail-matched-to-impact", "/craft:cm",
    scaffold(heredocs({"go.mod": GOMOD, "store/store.go": LINT_V1}),
             commit("feat(store): add record store"),
             heredocs({"store/store.go": LINT_V2}),
             "git add -A\n"),
    {
        "b1-style-or-chore": g_regex(r"^```[a-z]*\n(style|chore)(\([^)\n]+\))?: ", flags="m"),
        "b2-no-per-edit-list": g_regex(
            r"^(?=[\s\S]*userI[Dd])(?=[\s\S]*httpU[Rr][Ll])(?=[\s\S]*nosec)",
            match="not_contains"),
        "b2-no-bullets-in-message": g_regex(FIRST_BLOCK + r"[-*]\s", match="not_contains"),
        "b3-no-footer": g_regex(r"^(Refs|BREAKING CHANGE):", flags="m", match="not_contains"),
    },
)

# 6 ------------------------------------------------------------------
HTTP_V1 = """// Package fetch downloads documents over HTTP.
package fetch

import (
	"io"
	"net/http"
)

// Get returns the body of the document at url.
func Get(url string) ([]byte, error) {
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	return io.ReadAll(resp.Body)
}
"""
HTTP_V2 = HTTP_V1 + """
// Head returns the response headers of the document at url without
// downloading its body, so callers can check the type and size first.
func Head(url string) (http.Header, error) {
	resp, err := http.Head(url)
	if err != nil {
		return nil, err
	}
	resp.Body.Close()
	return resp.Header, nil
}
"""

case(
    "cm--verbosity-arguments", "/craft:cm micro, then /craft:cm full",
    scaffold(heredocs({"go.mod": GOMOD, "fetch/fetch.go": HTTP_V1}),
             commit("feat(fetch): add document fetcher"),
             heredocs({"fetch/fetch.go": HTTP_V2}),
             "git add -A\n"),
    {
        "b1-micro-summary-only": g_regex(r"^[\s\S]*?```[a-z]*\n[a-z]+(\([^)\n]+\))?: [^\n]+\n```"),
        "b2-full-multi-paragraph": g_regex(
            r"```[a-z]*\n[a-z]+(\([^)\n]+\))?: [^\n]+\n\n(?:[^\n]+\n)+\n(?:[^\n]+\n)+"),
        "b3-same-summary": g_regex(r"```[a-z]*\n([^\n]+)\n```[\s\S]*```[a-z]*\n\1\n\n"),
    },
)

# 7 ------------------------------------------------------------------
ATTRIBUTION = ENGLISH + """
Attribution for git commits you create from here on:
- End git commit messages with:
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
"""

case(
    "cm--apply-commits-without-confirming", "/craft:cm micro apply",
    scaffold(heredocs({"go.mod": GOMOD, "fetch/fetch.go": HTTP_V1}),
             commit("feat(fetch): add document fetcher"),
             heredocs({"fetch/fetch.go": HTTP_V2}),
             "git add -A\n"),
    {
        "b1-commits-via-stdin-no-m": g_tool(
            "Bash", r"(?:\b|\\n)git\s+commit\b(?=" + S + r"(-F\s*-|--file[= ]-))(?!" + S + r"\s-m\b)"),
        "b1-no-m-or-bare-commit": g_tool(
            "Bash", r"(?:\b|\\n)git\s+commit\b(?!" + S + r"(-F\s*-|--file[= ]-))", 0, 0),
        "b2-one-line-message": g_regex(r"```[a-z]*\n[a-z]+(\([^)\n]+\))?: [^\n]+\n```"),
        "b2-no-body-committed": g_regex(
            GIT_COMMIT + S + r"<<\s*'?(\w+)'?\\n[^\\\"]+\\n(?!\1\b)", target="trace",
            match="not_contains"),
        "b3-no-coauthor-in-commit": g_regex(
            GIT_COMMIT + S + r"Co-Authored-By", target="trace", flags="i", match="not_contains"),
        "b3-no-coauthor-shown": g_regex(r"^Co-Authored-By:", flags="im", match="not_contains"),
    },
    system=ATTRIBUTION,
)

# 8, 10 --------------------------------------------------------------
RETRY_V1 = """// Package httpx wraps net/http with the service's defaults.
package httpx

import "net/http"

// Client sends requests to upstream services.
type Client struct {
	hc *http.Client
}

// Do sends req once.
func (cli *Client) Do(req *http.Request) (*http.Response, error) {
	return cli.hc.Do(req)
}
"""
RETRY_V2 = """// Package httpx wraps net/http with the service's defaults.
package httpx

import (
	"net/http"
	"time"
)

// maxAttempts is how many times Do tries a request before giving up.
const maxAttempts = 3

// Client sends requests to upstream services.
type Client struct {
	hc *http.Client
}

// Do sends req, retrying transport errors with exponential backoff.
func (cli *Client) Do(req *http.Request) (*http.Response, error) {
	var err error
	for attempt := 0; attempt < maxAttempts; attempt++ {
		var resp *http.Response
		resp, err = cli.hc.Do(req)
		if err == nil {
			return resp, nil
		}
		if attempt == maxAttempts-1 {
			break
		}
		time.Sleep(time.Duration(1<<attempt) * 100 * time.Millisecond)
	}
	return nil, err
}
"""
RETRY_SCAFFOLD = scaffold(heredocs({"go.mod": GOMOD, "httpx/client.go": RETRY_V1}),
                          commit("feat(httpx): add client"),
                          heredocs({"httpx/client.go": RETRY_V2}))
INVENTED = g_regex(r"\b(400|800)\s?ms\b|\b0?\.[48]\s?s\b|\b1\.6\s?s\b", flags="i", match="not_contains")

case(
    "cm--empty-index-falls-back-to-unstaged", "/craft:cm",
    RETRY_SCAFFOLD,
    {
        "b1-reads-unstaged-diff": g_tool("Bash", r"(?:\b|\\n)git\s+diff\b(?!" + S + r"--cached|" + S + r"--staged)"),
        "b1-describes-the-retry": g_regex(r"^```[a-z]*\n[^\n]*(retr|backoff)", flags="im"),
        "b2-says-unstaged": g_regex(r"unstaged|not staged|nothing (is )?staged|working[- ]tree", flags="i"),
        "b3-stages-nothing": NO_STAGE,
        "b3-no-commit": NO_COMMIT,
        "b4-no-invented-delay": INVENTED,
    },
)

case(
    "cm--apply-with-nothing-staged", "/craft:cm apply",
    RETRY_SCAFFOLD,
    {
        "b1-reads-unstaged-diff": g_tool("Bash", r"(?:\b|\\n)git\s+diff\b(?!" + S + r"--cached|" + S + r"--staged)"),
        "b1-describes-the-retry": g_regex(r"^```[a-z]*\n[^\n]*(retr|backoff)", flags="im"),
        "b2-no-commit": NO_COMMIT,
        "b3-stages-nothing": NO_STAGE,
        "b4-says-unstaged": g_regex(r"unstaged|not staged|nothing (is )?staged", flags="i"),
        "b4-says-apply-did-not-run": g_regex(
            # `n't` takes no leading \b: "didn't" has none before the n.
            r"(apply|commit)[^\n]{0,80}(\bnot|n't|\bskipped)\b|(\bnot|n't|\bno)\b[^\n]{0,60}\b(commit|apply)",
            flags="i"),
        "b4-presents-message": ONE_BLOCK,
        "b5-no-invented-delay": INVENTED,
    },
)

# 9 ------------------------------------------------------------------
DUR_V1 = """// Package conf parses configuration values.
package conf

import (
	"fmt"
	"time"
)

// ParseDuration parses s as a time.Duration. It rejects negative values:
// every duration in the configuration is a wait, and a wait cannot be
// negative.
func ParseDuration(s string) (time.Duration, error) {
	d, err := time.ParseDuration(s)
	if err != nil {
		return 0, fmt.Errorf("parse duration %q: %w", s, err)
	}
	return d, nil
}
"""
DUR_V2 = DUR_V1.replace(
    "\t\treturn 0, fmt.Errorf(\"parse duration %q: %w\", s, err)\n\t}\n",
    "\t\treturn 0, fmt.Errorf(\"parse duration %q: %w\", s, err)\n\t}\n"
    "\tif d < 0 {\n\t\treturn 0, fmt.Errorf(\"parse duration %q: negative\", s)\n\t}\n")
DUR_TEST = """package conf

import "testing"

func TestParseDuration_negative(t *testing.T) {
	_, err := ParseDuration("-5s")
	if err == nil {
		t.Fatal("expected an error for a negative duration")
	}
}
"""

case(
    "cm--fix-that-restores-promised-behavior-is-not-breaking", "/craft:cm",
    scaffold(heredocs({"go.mod": GOMOD, "conf/duration.go": DUR_V1}),
             commit("feat(conf): add ParseDuration"),
             heredocs({"conf/duration.go": DUR_V2, "conf/duration_test.go": DUR_TEST}),
             "git add -A\n"),
    {
        "b1-fix-type": g_regex(r"^```[a-z]*\nfix(\([^)\n]+\))?: ", flags="m"),
        "b1-no-bang": g_regex(r"^[a-z]+(\([^)\n]*\))?!:", flags="m", match="not_contains"),
        "b1-no-breaking-footer": g_regex(FIRST_BLOCK + r"BREAKING CHANGE", match="not_contains"),
        "b2-framed-as-matching-the-docs": g_llm(
            "The commit message presents the change as a bug fix that makes "
            "`ParseDuration` reject negative values as its documentation already "
            "said it does, not as a breaking change of the contract."),
        "b3-names-who-must-act": g_llm(
            "The commit message body says that code (or callers) relying on "
            "`ParseDuration` accepting negative values will now get an error."),
    },
    extra_tags=["sec:cm:breaking-changes"],
)

# 11 -----------------------------------------------------------------
RID_V1 = """// Package mw holds the service's HTTP middleware.
package mw

import "net/http"

// Chain applies the middleware in order.
func Chain(h http.Handler, mws ...func(http.Handler) http.Handler) http.Handler {
	for i := len(mws) - 1; i >= 0; i-- {
		h = mws[i](h)
	}
	return h
}
"""
RID = """package mw

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"net/http"
)

// Header carries the request id between services.
const Header = "X-Request-Id"

type ridKey struct{}

// RequestID reuses the caller's X-Request-Id or mints one, stores it in the
// request context, and echoes it in the response.
func RequestID(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		id := r.Header.Get(Header)
		if id == "" {
			var b [8]byte
			_, _ = rand.Read(b[:])
			id = hex.EncodeToString(b[:])
		}
		w.Header().Set(Header, id)
		next.ServeHTTP(w, r.WithContext(context.WithValue(r.Context(), ridKey{}, id)))
	})
}

// FromContext returns the request id stored by RequestID, or "".
func FromContext(ctx context.Context) string {
	id, _ := ctx.Value(ridKey{}).(string)
	return id
}
"""

case(
    "cm--hash-without-an-amend-ask", "/craft:cm HEAD",
    scaffold(heredocs({"go.mod": GOMOD, "mw/chain.go": RID_V1}),
             commit("feat(mw): add middleware chain"),
             heredocs({"mw/requestid.go": RID}),
             commit("wip")),
    {
        "b1-git-show": g_tool("Bash", r"(?:\b|\\n)git\s+show\b"),
        "b1-describes-request-id": g_regex(r"^```[a-z]*\n[^\n]*request[- ]?id", flags="im"),
        "b2-no-commit": NO_COMMIT,
        "b2-no-history-rewrite": g_tool("Bash", r"(?:\b|\\n)git\s+(reset|rebase|replace|filter-branch)\b", 0, 0),
        # An offer or a how-to, not a statement that nothing was amended.
        "b3-no-amend-offer": g_regex(
            r"\b(ask me to|want me to|shall I|should I|I can|I could|to)\s+(\w+\s+){0,2}amend|"
            r"/cm\b[^\n]*\bapply\b|--amend", flags="i", match="not_contains"),
    },
)

# ------------------------------------------------------------- write


def main():
    for d in glob.glob(os.path.join(EVALS, "cm--*")):
        shutil.rmtree(d)
    for c in CASES:
        d = os.path.join(EVALS, c["name"])
        os.makedirs(os.path.join(d, "graders"))
        tags = [f"case:{c['name']}"] + list(dict.fromkeys(c["tags"]))
        sysp = "".join("  " + l + "\n" if l else "\n" for l in c["system"].rstrip("\n").split("\n"))
        with open(os.path.join(d, "prompt.md"), "w") as f:
            f.write("---\n"
                    f"tags: [{', '.join(tags)}]\n"
                    "runs: 1\n"
                    f"max_turns: {c['max_turns']}\n"
                    f"timeout_seconds: {c['timeout']}\n"
                    "allowed_tools: [Read, Glob, Grep, Skill, Bash(git:*)]\n"
                    "append_system_prompt: |\n" + sysp +
                    "---\n\n" + c["query"] + "\n")
        yaml = (f'schema_version: "1.1"\nname: {c["name"]}\ncontext:\n'
                "  scaffold_script: scaffold.sh\n")
        if c["history"]:
            yaml += "  history_file: history.jsonl\n"
            with open(os.path.join(d, "history.jsonl"), "w") as f:
                f.write(c["history"])
        with open(os.path.join(d, "case.yaml"), "w") as f:
            f.write(yaml)
        p = os.path.join(d, "scaffold.sh")
        with open(p, "w") as f:
            f.write(c["scaffold"])
        os.chmod(p, 0o755)
        for gname, body in c["graders"].items():
            with open(os.path.join(d, "graders", gname + ".md"), "w") as f:
                f.write(body)
    print(f"wrote {len(CASES)} cases")


main()
