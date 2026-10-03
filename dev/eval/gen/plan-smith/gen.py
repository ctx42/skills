#!/usr/bin/env python3
"""Generate craft/evals/plan-smith--* native eval cases."""
import json
import os
import shutil
import uuid

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
EVALS = os.path.join(ROOT, "craft/evals")
ASSETS = os.path.join(ROOT, "craft/skills/plan-smith/assets")

ENGLISH = "The user writes English; reply in English."
WIRING = """Automated eval: the user is absent. Whenever the skill would stop and wait
for the user, take the next scripted answer below as the reply and continue
in this same run; never end the run to wait. If none fits, give the most
plausible answer and continue.
Before taking a scripted answer, write out in full, as your reply text, the
message you would send the user at that point."""
NOTICE = ("Ignore any trailing notice about a company directive "
          "(«Nutzung von Claude und andere AI-Agents»). ")

BASE = ["skill:plan-smith", "sec:plan-smith:usage", "sec:plan-smith:self-learning"]
FMT = ["sec:plan-smith:format", "sec:plan-smith:summary",
       "sec:plan-smith:1-item-name-x",
       "sec:plan-smith:3-item-name-x-rejected-one-line-reason",
       "sec:plan-smith:n-remove-this-plan"]
WRITE = BASE + FMT + ["sec:plan-smith:write-mode"]
UPDATE = BASE + FMT + ["sec:plan-smith:update-mode"]
TOOLS = ["Read", "Glob", "Grep", "Skill", "Write", "Edit"]


def asset(name):
    with open(os.path.join(ASSETS, name)) as f:
        return f.read()


def jsre(s):
    """Escape a literal for a JavaScript regex; newlines become \\n."""
    out = []
    for ch in s:
        if ch in r"\.*+?^${}()|[]/":
            out.append("\\" + ch)
        elif ch == "\n":
            out.append(r"\n")
        else:
            out.append(ch)
    return "".join(out)


def aligned_table():
    """Summary table aligned: '#' 4 wide, Item W wide, Status 8 wide."""
    def cell(w):
        return r"(?= [^ |])[^|\n]{%d}(?<= )" % w
    alts = []
    for w in range(6, 61):
        row = r"\|" + cell(4) + r"\|" + cell(w) + r"\|" + cell(8) + r"\|\n"
        sep = r"\|-{4}\|-{%d}\|-{8}\|\n" % w
        alts.append(row + sep + "(?:" + row + ")+")
    return r"^(?=\| #)(?:" + "|".join(alts) + r")(?!\|)"


ALIGNED = aligned_table()
SECTION_WITHOUT_CRITERIA = (
    r"^## \d+\.(?:(?!^## |done when|acceptance|verified by)[\s\S])*(?=^## |(?![\s\S]))")
COUNT_SEP = r"\s*(?:[/·,|]|,?\s+and\b)\s*"  # "0 Y / 5 N / 0 X" or "0 Y, 5 N and 0 X"


def counts(y, n, x):
    return f"{y}\\s*Y{COUNT_SEP}{n}\\s*N{COUNT_SEP}{x}\\s*X"


def fm(d):
    lines = []
    for k, v in d.items():
        if isinstance(v, list):
            lines.append(f"{k}: [{', '.join(v)}]")
        elif isinstance(v, str) and "\n" in v:
            lines.append(f"{k}: |")
            lines.extend(("  " + l) if l else "" for l in v.rstrip("\n").split("\n"))
        else:
            lines.append(f"{k}: {v}")
    return "---\n" + "\n".join(lines) + "\n---\n"


def regex(pattern, target="last_message", flags=None, match=None):
    d = {"type": "regex"}
    if isinstance(target, str) and target.startswith("file:"):
        d["target"] = "{source: file, path: %s}" % target[5:]
    else:
        d["target"] = target
    if match:
        d["match"] = f'"{match}"'
    if flags:
        d["flags"] = f'"{flags}"'
    return fm(d) + pattern + "\n"


def no_tool(tool):
    return fm({"type": "tool_used", "tool": tool, "min": 0, "max": 0, "arm": "both"})


def exists(path, yes=True):
    return fm({"type": "file_exists", "path": path, "exists": "true" if yes else "false"})


def llm(claim):
    return fm({"type": "llm", "focus": "last_message"}) + NOTICE + claim + "\n"


def case(name, tags, query, graders, *, answers=None, scaffold=None,
         history=None, max_turns=40, timeout=300, tools=TOOLS, extra_files=None):
    d = os.path.join(EVALS, f"plan-smith--{name}")
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, "graders"))
    asp = ENGLISH
    if answers:
        asp += "\n\n" + WIRING + "\n\n" + "\n".join(
            f"{i}. {a}" for i, a in enumerate(answers, 1))
    meta = {
        "tags": [f"case:plan-smith--{name}"] + tags,
        "runs": 1,
        "max_turns": max_turns,
        "timeout_seconds": timeout,
        "allowed_tools": tools,
        "append_system_prompt": asp + "\n",
    }
    with open(os.path.join(d, "prompt.md"), "w") as f:
        f.write(fm(meta) + "\n" + query + "\n")
    if scaffold or history:
        y = ['schema_version: "1.1"', f"name: plan-smith--{name}", "context:"]
        if scaffold:
            y.append("  scaffold_script: scaffold.sh")
        if history:
            y.append("  history_file: history.jsonl")
        with open(os.path.join(d, "case.yaml"), "w") as f:
            f.write("\n".join(y) + "\n")
    if scaffold:
        p = os.path.join(d, "scaffold.sh")
        with open(p, "w") as f:
            f.write(scaffold)
        os.chmod(p, 0o755)
    if history:
        with open(os.path.join(d, "history.jsonl"), "w") as f:
            f.write(history)
    for gname, body in graders.items():
        with open(os.path.join(d, "graders", gname + ".md"), "w") as f:
            f.write(body)


class Sh:
    """Build a scaffold script from inline files."""

    def __init__(self, git=False):
        self.parts = ["#!/usr/bin/env bash", "set -euo pipefail"]
        self.n = 0
        if git:
            self.parts += [
                "git init -q -b main",
                "git config user.email eval@example.com",
                "git config user.name Eval",
                "git config commit.gpgsign false",
            ]

    def file(self, path, content):
        tag = f"EOF_{self.n}"
        self.n += 1
        dn = os.path.dirname(path)
        if dn:
            self.parts.append(f"mkdir -p {dn}")
        if not content.endswith("\n"):
            content += "\n"
        self.parts.append(f"cat > {path} <<'{tag}'\n{content}{tag}")

    def run(self, cmd):
        self.parts.append(cmd)

    def text(self):
        return "\n".join(self.parts) + "\n"


# ---------------------------------------------------------------- fixtures

GO_SERVICE_MOD = "module example.com/svc\n\ngo 1.22\n"
GO_SERVICE_MAIN = '''// Command svc serves the operator API.
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
'''


def plan_write_graders(path, n_items, named_heads):
    g = {}
    g["b1-plan-file-exists"] = exists(path)
    g["b1-summary-and-legend"] = regex(
        r"^# [^\n]+\n\n## Summary\n\n\| #[\s\S]*^Legend:[^\n]*Y[^\n]*implemented[^\n]*N[^\n]*not yet[^\n]*X[^\n]*rejected",
        f"file:{path}", "m")
    g["b1-every-heading-has-checkbox"] = regex(
        r"^## \d+\.(?![^\n]*— \[[ x]\])[^\n]*$", f"file:{path}", "m", "not_contains")
    g["b2-item-count"] = regex(r"^## \d+\. ", f"file:{path}", "m", f"count:{n_items}")
    g["b2-closing-item-last"] = regex(
        rf"^## {n_items}\. Remove this plan — \[ \]$", f"file:{path}", "m")
    if named_heads:
        g["b2-named-items"] = regex(
            "^" + "".join(rf"(?=[\s\S]*^## \d+\.[^\n]*(?:{h}))" for h in named_heads),
            f"file:{path}", "im")
    g["b3-no-y-or-x-status"] = regex(
        r"^\|[^|\n]*\|[^|\n]*\| *[YX] *\|$", f"file:{path}", "m", "not_contains")
    g["b3-no-checked-box"] = regex(r"\[x\]", f"file:{path}", None, "not_contains")
    g["b4-every-item-has-criteria"] = regex(
        SECTION_WITHOUT_CRITERIA, f"file:{path}", "im", "not_contains")
    g["b6-table-aligned"] = regex(ALIGNED, f"file:{path}", "m")
    g["b7-no-plan-pasted"] = regex(
        r"^\s*\|\s*#\s*\||^#{1,3}\s*\d+\.\s", "last_message", "m", "not_contains")
    return g


# ------------------------------------------------------- 1 write-from-brief

sh = Sh()
sh.file("go.mod", GO_SERVICE_MOD)
sh.file("cmd/svc/main.go", GO_SERVICE_MAIN)
g = plan_write_graders("tmp/sso-plan.md", 5,
                       [r"(provider|config)", r"login", r"session", r"doc"])
g["b2-no-invented-items"] = regex(
    r"^## \d+\.[^\n]*\b(tests?|testing|CI|monitor\w*|rollout|roll-out|migrat\w*|metrics|alert\w*)\b",
    "file:tmp/sso-plan.md", "im", "not_contains")
g["b5-no-protocol-picked"] = regex(
    r"^(?![\s\S]*\b(OIDC|OpenID|SAML)\b)|^(?=[\s\S]*\b(OIDC|OpenID)\b)(?=[\s\S]*\bSAML\b)",
    "file:tmp/sso-plan.md")
g["b5-only-table-and-items"] = regex(
    r"^#{2,6} (?!Summary$|\d+\. )|^\**(assumptions?|open (questions?|choices|decisions)|risks?|decisions?)\**:?\s*$",
    "file:tmp/sso-plan.md", "im", "not_contains")
g["b7-path-and-counts-one-line"] = regex(
    r"sso-plan\.md[^\n]*" + counts(0, 5, 0) + "|" + counts(0, 5, 0) + r"[^\n]*sso-plan\.md",
    "last_message", "i")
g["b7-leave-outs-short"] = regex(r"^\s*[-*] [^\n]{111,}", "last_message", "m", "not_contains")
case("write-from-brief", WRITE,
     "/craft:plan-smith write plan the work to add SSO: provider config, login flow, "
     "session storage, and a page in the operator docs.",
     g, scaffold=sh.text(),
     answers=["Those choices are not made yet — leave them open and write the plan now."])

# --------------------------------------------------------- 2 bundled-brief

BUNDLED = ("/craft:plan-smith we need to get the nightly export working properly — right now "
           "it dumps everything to one CSV on the app server, which fills the disk, nobody "
           "is told when it fails, and finance says the numbers do not tie out with the "
           "dashboard. The figures can only be reconciled once the export is split per "
           "entity, since today there is nothing to compare line by line. Write that up as "
           "a plan.")
P2 = "tmp/export-plan.md"
g = {}
g["b1-plan-file-exists"] = exists(P2)
g["b1-split-into-outcomes"] = regex(
    r"^(?=[\s\S]*^## \d+\.[^\n]*(disk|stor|split|entit|location|off the app|destination|move))"
    r"(?=[\s\S]*^## \d+\.[^\n]*(notif|alert|fail))"
    r"(?=[\s\S]*^## \d+\.[^\n]*(reconcil|tie|dashboard|match|finance|figures|numbers))",
    f"file:{P2}", "im")
g["b1-at-least-three-work-items"] = regex(
    r"^## 4\. ", f"file:{P2}", "m")
g["b3-no-unraised-work"] = regex(
    r"^## \d+\.[^\n]*\b(rewrite|rewriting|scheduler|cron|airflow|language|port\b|tests?\b|monitoring|dashboards?\s+for)",
    f"file:{P2}", "im", "not_contains")
g["b4-every-item-has-criteria"] = regex(
    SECTION_WITHOUT_CRITERIA, f"file:{P2}", "im", "not_contains")
g["b5-dependency-stated"] = regex(
    r"(depend\w*|block\w*|requires?|needs?|after|once|until|first|cannot start|can only|using|uses|builds? on|from|with)[^\n]{0,120}(item\s*#?\d|#\d|\bsplit|per[- ]entity|own file)"
    r"|(item\s*#?\d|#\d)[^\n]{0,40}(depends?|is blocked|needs|requires)",
    f"file:{P2}", "i")
case("bundled-brief", WRITE, BUNDLED, g,
     answers=["'Not tying out' means the per-entity daily totals in the export differ "
              "from the dashboard's totals for the same day. The files should go to the "
              "shared object store (s3://finance-exports) instead of the app server's "
              "disk, and failure notices go to the #data-alerts channel. Save the plan "
              "as tmp/export-plan.md."])

g = {}
g["b2-no-write"] = no_tool("Write")
g["b2-no-edit"] = no_tool("Edit")
g["b2-asks-the-open-piece"] = regex(
    r"(tie|reconcil|dashboard|mismatch|differ|discrepan|where|destination|instead of the app server|store|entity)[^\n]*\?",
    "last_message", "i")
case("bundled-brief--gate", WRITE, BUNDLED, g, max_turns=30)

# ------------------------------------------------------ 3 grill-me-handoff

TURNS = [
    ("user", "/craft:grill-me CSV export for the reporting tool"),
    ("assistant", "6 branches open, 0 resolved: scope, size limit, format, delivery, "
     "permissions, audit.\n\nScope: does an export cover the filtered view or the whole dataset?"),
    ("user", "The currently filtered view only."),
    ("assistant", "Scope: the filtered view, not the whole dataset. 1 of 6 resolved, 5 open.\n\n"
     "Size limit: how many rows may one export hold?"),
    ("user", "Refuse anything over 100k rows and tell the user to narrow the filter."),
    ("assistant", "Size limit: over 100,000 rows is refused with a message to narrow the "
     "filter. 2 of 6 resolved, 4 open.\n\nFormat: which CSV dialect and encoding?"),
    ("user", "RFC 4180, UTF-8 with a BOM so Excel opens it correctly."),
    ("assistant", "Format: RFC 4180, UTF-8 with BOM. 3 of 6 resolved, 3 open.\n\n"
     "Delivery: a download in the request, or a background job?"),
    ("user", "Synchronous download. No email, no background job."),
    ("assistant", "Delivery: synchronous download only. 4 of 6 resolved, 2 open.\n\n"
     "Permissions: who may export a report?"),
    ("user", "Anyone who can see the report can export it."),
    ("assistant", "Permissions: export follows view access. 5 of 6 resolved, 1 open.\n\n"
     "Audit: should exports be recorded in the audit log?"),
    ("user", "Yes, log every export with the user, the timestamp, and the row count."),
    ("assistant", """All 6 branches resolved.

1. Scope — the export covers the currently filtered view, not the whole dataset. Verified by: exporting from a filtered report yields exactly the filtered rows.
2. Size limit — over 100k rows the export is refused with a message telling the user to narrow the filter. Verified by: a 100,001-row selection is refused and names the filter as the fix.
3. Format — RFC 4180, UTF-8 with a BOM so Excel opens it correctly. Verified by: the file opens in Excel with accented characters intact and round-trips through a CSV parser.
4. Delivery — synchronous download, no email and no background job. Verified by: the request returns the file itself, and no job row is created.
5. Permissions — anyone who can see the report can export it, no separate grant. Verified by: a viewer-role user can export, and a user who cannot open the report gets 403.
6. Audit — every export is logged with user, timestamp, and row count. Verified by: an export writes exactly one audit row carrying those three fields.

Persist this as a tracked plan at tmp/csv-export-plan.md?"""),
]


def history(turns, session):
    lines, parent = [], None
    for i, (role, text) in enumerate(turns):
        u = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{session}/{i}"))
        rec = {"parentUuid": parent, "isSidechain": False, "userType": "external",
               "cwd": "/work/project", "sessionId": session, "version": "2.1.288",
               "type": role, "uuid": u,
               "timestamp": f"2026-10-01T10:{i:02d}:00.000Z"}
        if role == "user":
            rec["message"] = {"role": "user", "content": text}
        else:
            rec["message"] = {"id": "msg_" + u.replace("-", "")[:24], "type": "message",
                              "role": "assistant", "model": "claude-opus-5-5",
                              "content": [{"type": "text", "text": text}],
                              "stop_reason": "end_turn", "stop_sequence": None,
                              "usage": {"input_tokens": 10, "output_tokens": 10}}
        lines.append(json.dumps(rec))
        parent = u
    return "\n".join(lines) + "\n"


P3 = "tmp/csv-export-plan.md"
g = plan_write_graders(P3, 7, [r"scope|filter", r"limit|size|row", r"format|csv|4180",
                               r"deliver|download", r"permission|access", r"audit"])
g["b1-no-reinterview"] = regex(
    # A settled branch's term in a new question ("exports blocked by the 100k
    # limit?") is context, not a re-ask: only questions that lead with it count.
    r"^[-*\s]*(?:\*\*[^*\n]*\*\*:?\s*)?(?:should|do|does|is|are|what|which|how|can|will)\b[^\n?]{0,40}"
    r"(filtered view|whole dataset|100k|100,000|row limit|BOM|4180|encoding|synchronous|background job|email|403|viewer|grant|audit row)[^\n?]*\?",
    "last_message", "im", "not_contains")
g["b2-verifications-carried"] = regex(
    r"^(?=[\s\S]*exactly the filtered rows)(?=[\s\S]*100,001)(?=[\s\S]*Excel[\s\S]*(round-trip|round trip|parser))"
    r"(?=[\s\S]*job row)(?=[\s\S]*\b403\b)(?=[\s\S]*(exactly )?one audit row)",
    f"file:{P3}", "i")
g["b5-path-and-counts"] = regex(
    r"csv-export-plan\.md[^\n]*" + counts(0, 7, 0) + "|" + counts(0, 7, 0) + r"[^\n]*csv-export-plan\.md",
    "last_message", "i")
g["b5-no-summary-replay"] = regex(
    r"RFC 4180|\bBOM\b|100,001|exactly the filtered rows", "last_message", "i", "not_contains")
case("grill-me-handoff", WRITE, "Yes, turn it into a plan.", g,
     history=history(TURNS, "7d1e2c4a-3b5f-4e8a-9c21-6a0f5e3d2b10"))

# ---------------------------------------------------------- 4 update-mixed

SSO = asset("sso-plan.md")
sh = Sh(git=True)
sh.file("go.mod", GO_SERVICE_MOD)
sh.file("cmd/svc/main.go", GO_SERVICE_MAIN)
sh.file("sso-plan.md", SSO)
sh.run("git add -A && git commit -q -m 'docs: add SSO plan'")
sh.run("git checkout -q -b feat/login-flow")
sh.file("auth/login.go", '''// Package auth implements the SSO login flow.
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
''')
sh.file("auth/login_test.go", '''package auth

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
''')
# The flow is wired, so login counts as built; provider config stays a
# hardcoded literal, so that item stays N.
sh.file("cmd/svc/main.go", '''// Command svc serves the operator API.
package main

import (
	"log"
	"net/http"

	"example.com/svc/auth"
)

func main() {
	flow := &auth.Flow{
		AuthURL:     "https://idp.staging.example/authorize",
		ClientID:    "svc",
		RedirectURI: "https://svc.staging.example/callback",
	}
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
	})
	mux.HandleFunc("GET /login", flow.Login)
	mux.HandleFunc("GET /callback", flow.Callback)
	log.Fatal(http.ListenAndServe(":8080", mux))
}
''')
sh.run("git add -A && git commit -q -m 'feat(auth): authorization-code login flow with PKCE'")
sh.run("git checkout -q main && git merge -q --no-ff feat/login-flow -m 'Merge pull request #41 from feat/login-flow'")
sh.run("git checkout -q -b feat/session-storage")
sh.file("session/store.go", '''// Package session keeps login sessions in Redis.
package session

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"time"
)

// TTL is how long a session lives without being renewed.
const TTL = 12 * time.Hour

// KV is the slice of a Redis client the store uses.
type KV interface {
	Set(ctx context.Context, key, val string, ttl time.Duration) error
	Get(ctx context.Context, key string) (string, error)
	Del(ctx context.Context, key string) error
}

// Store keeps sessions in Redis keyed by an opaque session ID; the cookie
// carries only that ID.
type Store struct{ kv KV }

// New returns a Store backed by kv.
func New(kv KV) *Store { return &Store{kv: kv} }

// Create stores a session for subject and returns its opaque ID.
func (sto *Store) Create(ctx context.Context, subject string) (string, error) {
	buf := make([]byte, 32)
	if _, err := rand.Read(buf); err != nil {
		return "", err
	}
	id := hex.EncodeToString(buf)
	return id, sto.kv.Set(ctx, key(id), subject, TTL)
}

// Get returns the subject of session id.
func (sto *Store) Get(ctx context.Context, id string) (string, error) {
	return sto.kv.Get(ctx, key(id))
}

// Logout deletes session id.
func (sto *Store) Logout(ctx context.Context, id string) error {
	return sto.kv.Del(ctx, key(id))
}

func key(id string) string { return "session:" + id }
''')
sh.file("session/store_test.go", '''package session

import (
	"context"
	"errors"
	"testing"
	"time"
)

// fakeRedis is an in-memory KV with a settable clock; it outlives any Store
// built on it, as a Redis server outlives the app.
type fakeRedis struct {
	now  time.Time
	vals map[string]string
	exp  map[string]time.Time
}

func newFakeRedis() *fakeRedis {
	return &fakeRedis{now: time.Unix(0, 0), vals: map[string]string{}, exp: map[string]time.Time{}}
}

func (fr *fakeRedis) Set(_ context.Context, key, val string, ttl time.Duration) error {
	fr.vals[key], fr.exp[key] = val, fr.now.Add(ttl)
	return nil
}

func (fr *fakeRedis) Get(_ context.Context, key string) (string, error) {
	val, ok := fr.vals[key]
	if !ok || !fr.now.Before(fr.exp[key]) {
		return "", errors.New("redis: nil")
	}
	return val, nil
}

func (fr *fakeRedis) Del(_ context.Context, key string) error {
	delete(fr.vals, key)
	return nil
}

func Test_Create_SetsTwelveHourTTL(t *testing.T) {
	fr := newFakeRedis()
	id, _ := New(fr).Create(context.Background(), "alice")
	if have := fr.exp["session:"+id].Sub(fr.now); have != 12*time.Hour {
		t.Fatalf("want 12h TTL, have %s", have)
	}
	fr.now = fr.now.Add(12*time.Hour + time.Second)
	if _, err := New(fr).Get(context.Background(), id); err == nil {
		t.Fatal("want the session expired after 12 hours")
	}
}

func Test_Session_SurvivesAppRestart(t *testing.T) {
	fr := newFakeRedis()
	id, _ := New(fr).Create(context.Background(), "alice")
	restarted := New(fr)
	if have, err := restarted.Get(context.Background(), id); err != nil || have != "alice" {
		t.Fatalf("want the session after a restart, have %q %v", have, err)
	}
}

func Test_Logout_DeletesKey(t *testing.T) {
	fr := newFakeRedis()
	sto := New(fr)
	id, _ := sto.Create(context.Background(), "alice")
	_ = sto.Logout(context.Background(), id)
	if _, ok := fr.vals["session:"+id]; ok {
		t.Fatal("want the key deleted on logout")
	}
}
''')
sh.run("git add -A && git commit -q -m 'feat(session): Redis session storage with 12h TTL'")
sh.run("git checkout -q main && git merge -q --no-ff feat/session-storage -m 'Merge pull request #44 from feat/session-storage'")
sh.file("ci/logs/staging-e2e-2026-09-30.log", '''2026-09-30T02:14:07Z job=staging-e2e commit=main provider=https://idp.staging.example
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
''')
sh.run("git add -A && git commit -q -m 'ci: keep the staging e2e log'")
P4 = "sso-plan.md"


def body(plan, n):
    """Section n's prose (between its heading and the next heading)."""
    part = plan.split(f"\n## {n}. ", 1)[1]
    part = part.split("\n", 1)[1]
    return part.split("\n## ", 1)[0].strip("\n")


g = {}
g["b1-table-statuses"] = regex(
    r"^(?=[\s\S]*^\| 1 +\| Provider config +\| N +\|$)(?=[\s\S]*^\| 2 +\| Login flow +\| Y +\|$)"
    r"(?=[\s\S]*^\| 3 +\| Session storage +\| [YN] +\|$)(?=[\s\S]*^\| 4 +\| Operator docs +\| X +\|$)",
    f"file:{P4}", "m")
g["b1-section-checkboxes"] = regex(
    r"^(?=[\s\S]*^## 1\. Provider config — \[ \]$)(?=[\s\S]*^## 2\. Login flow — \[x\]$)"
    r"(?=[\s\S]*^## 3\. Session storage — \[[x ]\]$)",
    f"file:{P4}", "m")
g["b1-docs-rejected-with-reason"] = regex(
    r"^## 4\. Operator docs — \[ \] *\(X: rejected — [^\n]*(platform|runbook)[^\n]*\)$",
    f"file:{P4}", "im")
g["b2-docs-prose-kept"] = regex(r"^## 4\. Operator docs[^\n]*\n\n" + jsre(body(SSO, 4)),
                                f"file:{P4}", "m")
g["b3-force-logout-item-5"] = regex(
    r"^(?=[\s\S]*^## 5\. [^\n]*(log ?out|sign[- ]?out)[^\n]* — \[ \]$)(?=[\s\S]*^\| 5 +\|[^|\n]*(log ?out|sign[- ]?out)[^|\n]*\| N +\|$)",
    f"file:{P4}", "im")
g["b3-closing-item-6"] = regex(
    r"^(?=[\s\S]*^## 6\. Remove this plan — \[ \]$)(?=[\s\S]*^\| 6 +\| Remove this plan +\| N +\|$)",
    f"file:{P4}", "m")
g["b3-nothing-after-closing"] = regex(r"^## 7\.|^\| 7 ", f"file:{P4}", "m", "not_contains")
g["b4-table-aligned"] = regex(ALIGNED, f"file:{P4}", "m")
for n, slug in [(1, "provider-config"), (2, "login-flow"), (3, "session-storage")]:
    g[f"b5-{slug}-prose-kept"] = regex(
        rf"^## {n}\.[^\n]*\n\n" + jsre(body(SSO, n)) + r"\n", f"file:{P4}", "m")
# Session storage may stay N: the fixture has no Redis client, only a fake KV.
g["b6-counts"] = regex(counts("[12]", "[2-4]", 1), "last_message", "i")
g["b6-reports-changes"] = regex(
    r"^(?=[\s\S]*login)(?=[\s\S]*session)(?=[\s\S]*(docs|operator))(?=[\s\S]*(force[- ]?logout|log ?out))",
    "last_message", "i")
g["b6-no-plan-pasted"] = regex(
    r"^\s*\|\s*#\s*\||^#{1,3}\s*\d+\.\s", "last_message", "m", "not_contains")
case("update-mixed", UPDATE,
     "/craft:plan-smith update sso-plan.md — login flow and session storage are both done "
     "and merged. We're dropping the operator docs item, the platform team is folding SSO "
     "into their own runbook instead. Provider config hasn't been started. Also, staging "
     "showed we need a way to force-logout a user across every session, that wasn't in the plan.",
     g, scaffold=sh.text(), max_turns=50)

# ------------------------------------------------- 5 update-unverified-claim

RL = asset("rate-limit-plan.md")
sh = Sh()
sh.file("go.mod", "module example.com/ratelimit\n\ngo 1.22\n")
sh.file("rate-limit-plan.md", RL)
sh.file("limiter.go", asset("limiter.go"))
P5 = "rate-limit-plan.md"
g = {}
# Read, or a shell read (runs have Bash).
g["b1-reads-the-code"] = regex(
    r'"name":"(?:Read|Bash)","input":\{"(?:file_path|command)":"(?:[^"\\]|\\.)*?limiter\.go',
    "trace")
g["b2-item-2-stays-n"] = regex(
    r"^(?=[\s\S]*^\| 2 +\| Redis counters +\| N +\|$)(?=[\s\S]*^## 2\. Redis counters — \[ \]$)",
    f"file:{P5}", "m")
g["b3-item-3-not-y"] = regex(
    r"^(?=[\s\S]*^\| 3 +\| 429 responses +\| N +\|$)(?=[\s\S]*^## 3\. 429 responses — \[ \]$)",
    f"file:{P5}", "m")
g["b4-names-map-not-redis"] = regex(
    r"(map|process[- ]local|in[- ]memory|in[- ]process|mutex|per[- ]process)", "last_message", "i")
g["b4-names-missing-retry-after"] = regex(r"Retry-After", "last_message", "i")
g["b4-claim-not-recorded"] = llm(
    "The reply tells the user that items 2 (Redis counters) and 3 (429 responses) "
    "were not marked done although the user said they were, because the code does "
    "not show them complete.")
g["b5-items-kept"] = regex(
    r"^(?=[\s\S]*^\| 1 +\| Token bucket +\| Y +\|$)(?=[\s\S]*^## 1\. Token bucket — \[x\]$)"
    r"(?=[\s\S]*^## 2\. Redis counters)(?=[\s\S]*^## 3\. 429 responses)",
    f"file:{P5}", "m")
case("update-unverified-claim", UPDATE,
     "/craft:plan-smith update rate-limit-plan.md — the Redis counters and the 429 responses "
     "both landed, mark them done.", g, scaffold=sh.text())

# ------------------------------------------------------ 6 ambiguous-request

g = {}
g["b1-one-question"] = regex(r"\?", "last_message", None, "count:1")
g["b1-write-or-update"] = regex(
    r"(write|new|draft|create)[\s\S]*(update|existing)|(update|existing)[\s\S]*(write|new|draft|create)",
    "last_message", "i")
g["b2-no-write"] = no_tool("Write")
g["b2-no-edit"] = no_tool("Edit")
g["b3-opens-on-question"] = regex(r"^[^\n]*\?", "last_message")
g["b3-no-preamble"] = regex(
    r"^\s*(I'll|I will|Let me|I've|I have|I'm|I (found|checked|looked|see|don't)|No plan|There (is|are) no|Sure|OK|Okay|Got it|To |Before )",
    "last_message", "i", "not_contains")
case("ambiguous-request", BASE, "/craft:plan-smith the SSO plan", g,
     max_turns=20, timeout=180)

# ---------------------------------------- 7 update-keeps-an-existing-table-s-widths

WIDE = asset("wide-column-plan.md")
sh = Sh()
sh.file("go.mod", "module example.com/tenancy\n\ngo 1.22\n")
sh.file("tmp/wide-column-plan.md", WIDE)
sh.file("store/query.go", '''// Package store is the repository layer; every query it runs is scoped to
// one tenant.
package store

import "strconv"

// TenantID identifies a tenant.
type TenantID string

// Cond is one extra WHERE condition with its argument.
type Cond struct {
	Expr string // e.g. "status = ?"
	Arg  any
}

// scoped renders a SELECT on table for tenant t. The tenant filter is always
// the first condition; repositories are the only callers, and each takes the
// tenant as a required parameter, so a query without a tenant id does not
// compile.
func scoped(table string, t TenantID, where []Cond) (string, []any) {
	sql := "SELECT * FROM " + table + " WHERE tenant_id = $1"
	args := []any{string(t)}
	for i, c := range where {
		sql += " AND " + c.Expr + " $" + strconv.Itoa(i+2)
		args = append(args, c.Arg)
	}
	return sql, args
}
''')
sh.file("store/users.go", '''package store

import (
	"context"
	"database/sql"
)

// Users is the repository for the users table.
type Users struct{ db *sql.DB }

// List returns tenant t's users matching where.
func (r Users) List(ctx context.Context, t TenantID, where ...Cond) (*sql.Rows, error) {
	q, args := scoped("users", t, where)
	return r.db.QueryContext(ctx, q, args...)
}
''')
sh.file("store/invoices.go", '''package store

import (
	"context"
	"database/sql"
)

// Invoices is the repository for the invoices table.
type Invoices struct{ db *sql.DB }

// List returns tenant t's invoices matching where.
func (r Invoices) List(ctx context.Context, t TenantID, where ...Cond) (*sql.Rows, error) {
	q, args := scoped("invoices", t, where)
	return r.db.QueryContext(ctx, q, args...)
}
''')
sh.file("store/users_integration_test.go", '''//go:build integration

package store

import (
	"context"
	"testing"
)

func Test_Users_List_ScopesToTenant(t *testing.T) {
	db := openTestDB(t)
	seed(t, db, "users", "acme", "globex")
	rows, err := Users{db: db}.List(context.Background(), "acme")
	if err != nil {
		t.Fatal(err)
	}
	assertOnlyTenant(t, rows, "acme")
}
''')
sh.file("store/invoices_integration_test.go", '''//go:build integration

package store

import (
	"context"
	"testing"
)

func Test_Invoices_List_ScopesToTenant(t *testing.T) {
	db := openTestDB(t)
	seed(t, db, "invoices", "acme", "globex")
	rows, err := Invoices{db: db}.List(context.Background(), "acme")
	if err != nil {
		t.Fatal(err)
	}
	assertOnlyTenant(t, rows, "acme")
}
''')
sh.file("store/helpers_integration_test.go", '''//go:build integration

package store

import (
	"database/sql"
	"os"
	"testing"

	_ "github.com/jackc/pgx/v5/stdlib"
)

func openTestDB(t *testing.T) *sql.DB {
	t.Helper()
	db, err := sql.Open("pgx", os.Getenv("TEST_DATABASE_URL"))
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { _ = db.Close() })
	return db
}

func seed(t *testing.T, db *sql.DB, table string, tenants ...string) {
	t.Helper()
	for _, tn := range tenants {
		if _, err := db.Exec("INSERT INTO "+table+" (tenant_id) VALUES ($1)", tn); err != nil {
			t.Fatal(err)
		}
	}
}

func assertOnlyTenant(t *testing.T, rows *sql.Rows, want string) {
	t.Helper()
	defer rows.Close()
	cols, _ := rows.Columns()
	for rows.Next() {
		vals := make([]any, len(cols))
		ptrs := make([]any, len(cols))
		for i := range vals {
			ptrs[i] = &vals[i]
		}
		_ = rows.Scan(ptrs...)
		for i, c := range cols {
			if c == "tenant_id" && vals[i] != want {
				t.Fatalf("want only tenant %s, have %v", want, vals[i])
			}
		}
	}
}
''')
sh.file("api/export.go", '''// Package api serves the tenant-facing HTTP API.
package api

import "net/http"

// TODO: per-tenant quotas — cap requests per tenant per minute so one
// tenant cannot starve the others.

// Export streams a tenant's data export.
func Export(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusNotImplemented)
}
''')
P7 = "tmp/wide-column-plan.md"
g = {}
g["b1-appended-row-padded-to-30"] = regex(
    r"^\| 4  \|(?= [^ |])[^|\n]{30}(?<= )\| N      \|$", f"file:{P7}", "m")
g["b1-closing-row-padded-to-30"] = regex(
    r"^\| 5  \| Remove this plan {13}\| N      \|$", f"file:{P7}", "m")
g["b1-header-kept"] = regex(
    r"^\| #  \| Item {25}\| Status \|\n\|----\|-{30}\|--------\|$", f"file:{P7}", "m")
g["b2-rows-2-3-identical"] = regex(
    r"^\| 2  \| Per-tenant keys {14}\| N      \|\n\| 3  \| Cross-tenant tests {11}\| N      \|$",
    f"file:{P7}", "m")
g["b2-row-1-only-status-changed"] = regex(
    r"^\| 1  \| Row-level filters {12}\| Y      \|$", f"file:{P7}", "m")
g["b3-item-1-checked"] = regex(r"^## 1\. Row-level filters — \[x\]$", f"file:{P7}", "m")
g["b3-todo-appended-as-item-4"] = regex(
    r"^(?=[\s\S]*^## 4\. [^\n]*quota[^\n]* — \[ \]$)(?=[\s\S]*^\| 4  \|[^|\n]*quota[^|\n]*\| N      \|$)",
    f"file:{P7}", "im")
case("update-keeps-an-existing-table-s-widths", UPDATE,
     "/craft:plan-smith update tmp/wide-column-plan.md", g, scaffold=sh.text())

# ------------------------------------------------- 8 update-completes-plan

DONE = asset("done-plan.md")
sh = Sh()
sh.file("go.mod", "module example.com/reports\n\ngo 1.22\n")
sh.file("tmp/done-plan.md", DONE)
sh.file("export/export.go", '''// Package export writes CSV exports of a report's filtered view.
package export

import (
	"context"
	"errors"
	"time"
)

// MaxRows is the largest export allowed.
const MaxRows = 100_000

// ErrTooMany is returned for a selection over MaxRows.
var ErrTooMany = errors.New("export refused: more than 100,000 rows — narrow the filter")

// Auditor records one audit row per export.
type Auditor interface {
	Record(ctx context.Context, user string, at time.Time, rows int) error
}

// Service exports filtered report views.
type Service struct {
	Audit Auditor
	Now   func() time.Time
}

// Export returns the CSV for the filtered rows and audits the export.
func (s Service) Export(ctx context.Context, user string, filtered [][]string) ([]byte, error) {
	if len(filtered) > MaxRows {
		return nil, ErrTooMany
	}
	out := render(filtered)
	if err := s.Audit.Record(ctx, user, s.Now(), len(filtered)); err != nil {
		return nil, err
	}
	return out, nil
}

func render(rows [][]string) []byte {
	var b []byte
	for _, r := range rows {
		for i, c := range r {
			if i > 0 {
				b = append(b, ',')
			}
			b = append(b, c...)
		}
		b = append(b, '\\n')
	}
	return b
}
''')
sh.file("export/export_test.go", '''package export

import (
	"context"
	"testing"
	"time"
)

type row struct {
	user string
	at   time.Time
	rows int
}

type fakeAudit struct{ rows []row }

func (f *fakeAudit) Record(_ context.Context, user string, at time.Time, n int) error {
	f.rows = append(f.rows, row{user, at, n})
	return nil
}

func Test_Export_WritesOneAuditRow(t *testing.T) {
	at := time.Date(2026, 9, 30, 12, 0, 0, 0, time.UTC)
	audit := &fakeAudit{}
	s := Service{Audit: audit, Now: func() time.Time { return at }}

	_, err := s.Export(context.Background(), "alice", [][]string{{"a"}, {"b"}, {"c"}})

	if err != nil {
		t.Fatal(err)
	}
	if len(audit.rows) != 1 {
		t.Fatalf("want exactly one audit row, have %d", len(audit.rows))
	}
	want := row{"alice", at, 3}
	if have := audit.rows[0]; have != want {
		t.Fatalf("want %+v, have %+v", want, have)
	}
}

func Test_Export_RefusesOverLimit(t *testing.T) {
	s := Service{Audit: &fakeAudit{}, Now: time.Now}
	_, err := s.Export(context.Background(), "alice", make([][]string, MaxRows+1))
	if err != ErrTooMany {
		t.Fatalf("want ErrTooMany, have %v", err)
	}
}
''')
SCAF8 = sh.text()
P8 = "tmp/done-plan.md"
ITEM3 = (r"^(?=[\s\S]*^## 3\. Audit log — \[x\]$)(?=[\s\S]*^\| 3  \| Audit log {9}\| Y      \|$)")
g = {}
g["b1-item-3-flipped"] = regex(ITEM3, f"file:{P8}", "m")
g["b4-numbering-kept"] = regex(
    r"^(?=[\s\S]*^## 1\. Filtered scope — \[x\]$)(?=[\s\S]*^## 2\. Row limit — \[x\]$)"
    r"(?=[\s\S]*^## 4\. Remove this plan)",
    f"file:{P8}", "m")
g["b4-no-fifth-item"] = regex(r"^## 5\.|^\| 5 ", f"file:{P8}", "m", "not_contains")
g["b5-file-kept"] = regex(r"^# CSV export plan$", f"file:{P8}", "m")
g["b5-closing-section-x"] = regex(
    r"^## 4\. Remove this plan — \[ \] *\(X: rejected — the user kept the plan\)$",
    f"file:{P8}", "m")
g["b5-closing-row-x"] = regex(r"^\| 4  \| Remove this plan  \| X      \|$", f"file:{P8}", "m")
case("update-completes-plan", UPDATE, "/craft:plan-smith update tmp/done-plan.md", g,
     scaffold=SCAF8, answers=["No, keep it."])

g = {}
g["b1-item-3-flipped"] = regex(ITEM3, f"file:{P8}", "m")
g["b2-asks-to-delete"] = regex(
    r"(delete|remove)[^\n]{0,80}(plan|file)|(plan|file)[^\n]{0,80}(delete|remov)",
    "last_message", "i")
g["b3-file-not-deleted"] = regex(r"^# CSV export plan$", f"file:{P8}", "m")
g["b3-closing-item-unmarked"] = regex(
    r"^(?=[\s\S]*^## 4\. Remove this plan — \[ \]$)(?=[\s\S]*^\| 4  \| Remove this plan  \| N      \|$)",
    f"file:{P8}", "m")
case("update-completes-plan--gate", UPDATE, "/craft:plan-smith update tmp/done-plan.md", g,
     scaffold=SCAF8)

print("ok")
