#!/usr/bin/env python3
"""Generate craft/evals/fix-all--* native eval cases. Re-runnable; owns only fix-all--*."""
import glob
import json
import os
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
EVALS = os.path.join(ROOT, "craft/evals")

ENGLISH = "The user writes English; reply in English.\n"

GIT_INIT = """git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
"""

# JSON-string body of a Bash command in the trace / tool input.
S = r'(?:[^"\\]|\\.)*'
GIT_COMMIT = r"(?:\b|\\n)git\s+commit\b"
# Every command, in the trace JSON, that runs `git commit`.
CMD_COMMIT = r'"command":"' + S + r'?' + GIT_COMMIT


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


def scaffold(files):
    return ("#!/usr/bin/env bash\nset -euo pipefail\n" + GIT_INIT + heredocs(files)
            + "go vet ./... && go test ./... >/dev/null\n"
            + "git add -A\ngit commit -qm 'initial'\n")


def yq(s):
    return "'" + s.replace("'", "''") + "'"


def g_regex(pattern, target="last_message", flags=None, match=None):
    fm = ["type: regex"]
    if isinstance(target, dict):
        fm += ["target:", "  source: file", f"  path: {target['path']}"]
    else:
        fm.append(f"target: {target}")
    if flags:
        fm.append(f'flags: "{flags}"')
    if match:
        fm.append(f"match: {match}")
    return "---\n" + "\n".join(fm) + "\n---\n" + pattern + "\n"


def g_tool(tool, input_match=None, min_=1, max_=None):
    fm = ["type: tool_used", f"tool: {tool}"]
    if input_match:
        fm.append(f"input_match: {yq(input_match)}")
    fm.append(f"min: {min_}")
    if max_ is not None:
        fm.append(f"max: {max_}")
        fm.append("arm: both")
    return "---\n" + "\n".join(fm) + "\n---\n"


def file_has(path, pattern, absent=False):
    return g_regex(pattern, target={"path": path}, match="not_contains" if absent else None)


NO_COMMIT = g_tool("Bash", GIT_COMMIT, 0, 0)
NO_EDIT = g_tool("Edit", None, 0, 0)
NO_WRITE = g_tool("Write", None, 0, 0)
NO_ADD_ALL = g_tool("Bash", r"(?:\b|\\n)git\s+add\s+(?:-A\b|--all\b|\.(?:\s|\\n|$|&|;|\"))", 0, 0)
NO_COAUTHOR = g_regex(CMD_COMMIT + S + r"Co-Authored-By", target="trace", flags="i",
                      match="not_contains")

ATTRIBUTION = ENGLISH + """
Attribution for git commits you create from here on:
- End git commit messages with:
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
"""

SCRIPTED = """
Automated eval: the user is absent. Whenever the skill would stop and wait
for the user, take the next scripted answer below as the reply and continue
in this same run; never end the run to wait. If none fits, give the most
plausible answer and continue.

1. Leave #2 as it is; do not fix it.
"""

TAGS = ["skill:fix-all", "needs-shell", "sec:fix-all:usage",
        "sec:fix-all:1-triage-before-any-edit", "sec:fix-all:2-fix-one-commit-per-fix",
        "sec:fix-all:3-report"]

CASES = []


def case(name, history, files, graders, system=ENGLISH, tags=TAGS):
    CASES.append(dict(name=name, history=history, scaffold=scaffold(files),
                      graders=graders, system=system, tags=tags))


def hist_line(i, parent, role, text):
    uid = f"00000000-0000-4000-8000-{i:012d}"
    base = {"parentUuid": parent, "isSidechain": False, "userType": "external",
            "cwd": "/work/project", "sessionId": "f1a11000-0000-4000-8000-00000000f1a1",
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


def history(ask, findings):
    out, parent = [], None
    for i, (role, text) in enumerate([("user", ask), ("assistant", findings)], 1):
        parent, line = hist_line(i, parent, role, text)
        out.append(line)
    return "\n".join(out) + "\n"


# 1 ------------------------------------------------------------------
FETCH = """// Package fetch downloads documents over HTTP.
package fetch

import (
	"fmt"
	"io"
	"net/http"
)

// Fetch returns the body of the document at url. Callers recieve an error
// for any status other than 200.
func Fetch(c *http.Client, url string) ([]byte, error) {
	resp, err := c.Get(url)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("fetch %s: %s", url, resp.Status)
	}
	defer resp.Body.Close()
	return io.ReadAll(resp.Body)
}
"""

UTIL = """package fetch

import "strings"

// trimAll trims the space around every string in ss.
func trimAll(ss []string) []string {
	out := make([]string, len(ss))
	for i, s := range ss {
		out[i] = strings.TrimSpace(s)
	}
	return out
}
"""

FETCH_TEST = """package fetch

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func Test_Fetch(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/missing" {
			http.NotFound(w, r)
			return
		}
		_, _ = w.Write([]byte("ok"))
	}))
	defer srv.Close()

	have, err := Fetch(srv.Client(), srv.URL+"/doc")
	if err != nil || string(have) != "ok" {
		t.Fatalf("Fetch() = %q, %v", have, err)
	}
	if _, err := Fetch(srv.Client(), srv.URL+"/missing"); err == nil {
		t.Fatal("Fetch(/missing) error = nil")
	}
}
"""

case(
    "fix-all--all-auto-commits-separately",
    history("Review the fetch package for problems.",
            "Three findings:\n\n"
            "1. `fetch.go` `Fetch` returns on a non-200 status before it defers "
            "`resp.Body.Close()`, so that path leaks the response body.\n"
            "2. The `Fetch` doc comment misspells \"receive\" as \"recieve\".\n"
            "3. `util.go` `trimAll` is unexported and never called: dead code."),
    {"go.mod": "module example.com/fetch\n\ngo 1.22\n", "fetch.go": FETCH,
     "util.go": UTIL, "fetch_test.go": FETCH_TEST},
    {
        "b1-no-question-commits": g_tool("Bash", GIT_COMMIT),
        "b2-three-commits": g_regex(CMD_COMMIT, target="trace", match='"count:3"'),
        "b2-no-add-all": NO_ADD_ALL,
        "b3-checks-gate-commit": g_regex(
            r'"command":"' + S + r"?(?:\b|\\n)go\s+(?:test|vet)\b" + S + GIT_COMMIT,
            target="trace"),
        "b4-conventional": g_regex(
            CMD_COMMIT + S + r"<<\s*'?\w+'?\\n(?:fix|docs|chore|refactor|style)(?:\([^)\\]+\))?!?: ",
            target="trace"),
        "b4-no-coauthor": NO_COAUTHOR,
        "b5-defer-before-status": file_has(
            "fetch.go", r"defer resp\.Body\.Close\(\)[\s\S]*StatusCode != http\.StatusOK"),
        "b5-typo-gone": file_has("fetch.go", "recieve", absent=True),
        "b5-trimall-gone": g_regex(
            r'"command":"' + S + r"(?:\b|\\n)(?:git\s+)?rm\b" + S + r"util\.go"
            + r'|"name":"Edit","input":\{"file_path":"[^"]*util\.go","old_string":"'
            + S + r"trimAll",
            target="trace"),
        "b6-fixed-3-of-3": g_regex(r"fixed 3 of 3", flags="i"),
        "b6-no-deferred": g_regex(r"^#*\s*\**Deferred", flags="im", match="not_contains"),
    },
    system=ATTRIBUTION,
)

# 2 ------------------------------------------------------------------
CLIENT = """// Package client sends HTTP requests with retries.
package client

import "net/http"

// Client retries a failed request up to MaxRetries times.
type Client struct {
	HTTP       *http.Client
	MaxRetries int
}

// Do sends req, retrying on a 5xx status.
func (c *Client) Do(req *http.Request) (*http.Response, error) {
	var resp *http.Response
	var err error
	for i := 0; i <= c.MaxRetries; i++ {
		resp, err = c.HTTP.Do(req)
		if err != nil {
			return nil, err
		}
		if resp.StatusCode < 500 {
			return resp, nil
		}
	}
	return resp, nil
}
"""

CLIENT_TEST = """package client

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func Test_Client_Do(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))
	defer srv.Close()

	c := &Client{HTTP: srv.Client()}
	req, _ := http.NewRequest(http.MethodGet, srv.URL, nil)
	have, err := c.Do(req)
	if err != nil || have.StatusCode != http.StatusOK {
		t.Fatalf("Do() = %v, %v", have, err)
	}
	have.Body.Close()
}
"""

README = """# client

HTTP client with retries. `MaxRetries` defaults to 0: a request is sent once.
"""

case(
    "fix-all--contract-asked-up-front",
    history("Review the client library.",
            "Three findings:\n\n"
            "1. The exported `Client.Do(req)` should take a `context.Context` as "
            "its first parameter.\n"
            "2. `Do` leaks the response body of every 5xx response it retries.\n"
            "3. The `MaxRetries` default of 0 should be 3; the README documents 0."),
    {"go.mod": "module example.com/client\n\ngo 1.22\n", "client.go": CLIENT,
     "client_test.go": CLIENT_TEST, "README.md": README},
    {
        "b1-asks-do-signature": g_regex(r"context|\bDo\b", flags="i"),
        "b1-asks-maxretries": g_regex(r"MaxRetries"),
        "b3-no-edit": NO_EDIT,
        "b3-no-write": NO_WRITE,
        "b3-no-commit": NO_COMMIT,
        "b3-client-unchanged": file_has("client.go", r"func \(c \*Client\) Do\(req \*http\.Request\)"),
    },
)

# 3 ------------------------------------------------------------------
CONFIG = """package app

import "time"

// config holds the resolved runtime settings.
type config struct {
	tmo time.Duration
}

func newConfig(o Options) config {
	return config{tmo: o.Timeout}
}
"""

OPTIONS = """// Package app runs the service.
package app

import "time"

// Options configures the service.
type Options struct {
	Timeout time.Duration
	// Legacy is no longer read.
	Legacy bool
}

// Timeout returns the timeout the service runs with.
func Timeout(o Options) time.Duration {
	return newConfig(o).tmo
}
"""

APP_TEST = """package app

import (
	"testing"
	"time"
)

func Test_Timeout(t *testing.T) {
	if have := Timeout(Options{Timeout: time.Second}); have != time.Second {
		t.Fatalf("Timeout() = %v", have)
	}
}
"""

EXAMPLE = """package main

import (
	"fmt"
	"time"

	"example.com/app"
)

func main() {
	fmt.Println(app.Timeout(app.Options{Timeout: time.Second, Legacy: true}))
}
"""

case(
    "fix-all--answered-round-then-unattended",
    history("Review the app package.",
            "Two findings:\n\n"
            "1. `config.go`: the unexported field `config.tmo` should be named "
            "`timeout`.\n"
            "2. `options.go`: drop the unused exported field `Options.Legacy`; "
            "`examples/main.go` still sets it."),
    {"go.mod": "module example.com/app\n\ngo 1.22\n", "config.go": CONFIG,
     "options.go": OPTIONS, "app_test.go": APP_TEST, "examples/main.go": EXAMPLE},
    {
        "b1-one-commit": g_regex(CMD_COMMIT, target="trace", match='"count:1"'),
        "b1-renamed": file_has("config.go", r"\btimeout\s+time\.Duration"),
        "b2-legacy-kept": file_has("options.go", r"\bLegacy\s+bool"),
        "b3-reports-2": g_regex(r"#?2\b[^\n]{0,160}(?:skip|left|leave|not fixed|deferred|decid|asked)",
                                flags="i"),
    },
    system=ENGLISH + SCRIPTED,
)


# ------------------------------------------------------------- write


def main():
    for d in glob.glob(os.path.join(EVALS, "fix-all--*")):
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
                    "max_turns: 60\n"
                    "timeout_seconds: 300\n"
                    "allowed_tools: [Read, Glob, Grep, Skill, Edit, Write, Bash(git:*), Bash(go:*)]\n"
                    "append_system_prompt: |\n" + sysp +
                    "---\n\n/craft:fix-all\n")
        with open(os.path.join(d, "case.yaml"), "w") as f:
            f.write(f'schema_version: "1.1"\nname: {c["name"]}\ncontext:\n'
                    "  scaffold_script: scaffold.sh\n  history_file: history.jsonl\n")
        with open(os.path.join(d, "history.jsonl"), "w") as f:
            f.write(c["history"])
        p = os.path.join(d, "scaffold.sh")
        with open(p, "w") as f:
            f.write(c["scaffold"])
        os.chmod(p, 0o755)
        for gname, body in c["graders"].items():
            with open(os.path.join(d, "graders", gname + ".md"), "w") as f:
                f.write(body)
    print(f"wrote {len(CASES)} cases")


main()
