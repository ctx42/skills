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
NOTICE = "Ignore any trailing policy notice. "

BASE = ["skill:plan-smith", "sec:plan-smith:usage", "sec:plan-smith:self-learning"]
FMT = ["sec:plan-smith:format", "sec:plan-smith:summary",
       "sec:plan-smith:1-item-name-x",
       "sec:plan-smith:3-item-name-x-rejected-one-line-reason",
       "sec:plan-smith:n-remove-this-plan"]
WRITE = BASE + FMT + ["sec:plan-smith:write-mode"]
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
