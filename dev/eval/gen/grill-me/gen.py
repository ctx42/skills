#!/usr/bin/env python3
"""Generate craft/evals/grill-me--* native eval cases. Rewrites only grill-me--*."""
import json, os, shutil, uuid, glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
EVALS = os.path.join(ROOT, "craft/evals")

ENGLISH = "The user writes English; reply in English."
SCRIPTED = """Automated eval: the user is absent. Whenever the skill would stop and wait
for the user, take the next scripted answer below as the reply and continue
in this same run; never end the run to wait. If none fits, give the most
plausible answer and continue.
Before taking a scripted answer, write out in full, as your reply text, the
message you would send the user at that point.
"""
BASE_TAGS = ["skill:grill-me", "sec:grill-me:usage", "sec:grill-me:how-it-works",
             "sec:grill-me:rules", "sec:grill-me:self-learning"]
SID = "5b0c7e8e-6f4e-4c1a-9a57-3f1d2b7c9e10"


def history(turns):
    """turns: list of ('user'|'assistant', text). Hand-built session JSONL."""
    lines, parent, minute = [], None, 0
    for role, text in turns:
        minute += 1
        u = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{SID}/{minute}/{text}"))
        rec = {"parentUuid": parent, "isSidechain": False, "userType": "external",
               "cwd": "/work/project", "sessionId": SID, "version": "2.1.288",
               "type": role, "uuid": u,
               "timestamp": f"2026-10-01T10:{minute:02d}:00.000Z"}
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


def grader(kind, body, **fm):
    out = ["---", f"type: {kind}"]
    for k, v in fm.items():
        out.append(f"{k}: {v}")
    out.append("---")
    out.append(body)
    return "\n".join(out) + "\n"


def last(body, match=None, flags=None):
    fm = {"target": "last_message"}
    if match:
        fm["match"] = json.dumps(match)
    if flags:
        fm["flags"] = json.dumps(flags)
    return grader("regex", body, **fm)


def infile(path, body, match=None, flags=None):
    fm = {"target": "{source: file, path: %s}" % path}
    if match:
        fm["match"] = json.dumps(match)
    if flags:
        fm["flags"] = json.dumps(flags)
    return grader("regex", body, **fm)


def llm(claim):
    return grader("llm", "Ignore any trailing policy notice. " + claim,
                  focus="last_message")


NO_WRITE = "---\ntype: tool_used\ntool: Write\nmin: 0\nmax: 0\narm: both\n---\n"


def case(name, query, graders, *, hist=None, answers=None, extra_tags=(),
         tools=("Read", "Glob", "Grep", "Skill"), max_turns=20, timeout=180):
    d = os.path.join(EVALS, name)
    os.makedirs(os.path.join(d, "graders"))
    tags = [f"case:{name}"] + BASE_TAGS + list(extra_tags)
    asp = ENGLISH + "\n"
    if answers:
        asp += "\n" + SCRIPTED + "\n" + "\n".join(
            f"{i}. {a}" for i, a in enumerate(answers, 1)) + "\n"
    fm = ["---", f"tags: [{', '.join(tags)}]", "runs: 1", f"max_turns: {max_turns}",
          f"timeout_seconds: {timeout}", f"allowed_tools: [{', '.join(tools)}]",
          "append_system_prompt: |"]
    fm += ["  " + l if l else "" for l in asp.rstrip("\n").split("\n")]
    fm.append("---")
    with open(os.path.join(d, "prompt.md"), "w") as f:
        f.write("\n".join(fm) + "\n\n" + query + "\n")
    if hist:
        with open(os.path.join(d, "history.jsonl"), "w") as f:
            f.write(history(hist))
        with open(os.path.join(d, "case.yaml"), "w") as f:
            f.write(f'schema_version: "1.1"\nname: {name}\ncontext:\n'
                    f'  history_file: history.jsonl\n')
    for gname, body in graders.items():
        with open(os.path.join(d, "graders", gname + ".md"), "w") as f:
            f.write(body)


for old in glob.glob(os.path.join(EVALS, "grill-me--*")):
    shutil.rmtree(old)

# 2. caller-supplied-subject: report-doc-gap drives; history about a Go rename.
GAP = "the docs don't say what happens to an in-flight order when a station goes offline"
H2 = [
    ("user", "Rename package `util` to `strutil` across the module and fix the imports."),
    ("assistant", "Renamed `util` to `strutil`: 4 files moved, 11 imports updated, "
                  "`go build ./...` passes."),
    ("user", "Good. Also drop the old `util` doc.go, strutil has its own."),
    ("assistant", "Removed `util/doc.go`; `strutil/doc.go` keeps the package godoc."),
    ("user", "/srd:report-doc-gap " + GAP),
    ("assistant", "This gap needs its facts drawn out before it can be filed. Handing it "
                  "to craft:grill-me; it returns its summary here and I file the gap "
                  "from that summary."),
]
case("grill-me--caller-supplied-subject", "/craft:grill-me " + GAP, {
    "b1-gap-is-the-subject": last(r"^(?=.*\border)(?=.*\bstation)", flags="is"),
    "b3-no-offer-to-persist": last(
        r"plan-smith|persist|save (it|this|the summary)|write (it|this) (up|to)|"
        r"plan file|as a plan|tracked plan", match="not_contains", flags="i"),
    "b3-hands-back": llm(
        "The reply ends on the structured summary of the documentation gap (or on "
        "handing that summary back to the report-doc-gap flow), not on a question "
        "asking the user whether to save or persist it."),
    "b4-no-write": NO_WRITE,
}, hist=H2, answers=[
    "The order is not cancelled. It stays queued on the server and is delivered "
    "when the station reconnects.",
    "If the station stays offline for more than 24 hours the order expires and the "
    "dispatcher gets a notification. Orders the station acknowledged before it "
    "dropped are not affected.",
    "The readers are dispatchers using the web console; while the station is "
    "offline the order shows the status \"Pending delivery\".",
    "The UI calls an offline station \"Disconnected\". \"In-flight\" means sent to "
    "the station but not yet acknowledged.",
    "That is everything I know; nothing else is open.",
], max_turns=40, timeout=300)

# 4. alignment-reached: summary + offer (gate), then the plan file (full).
H4 = [
    ("user", "/craft:grill-me CSV export for the reporting tool"),
    ("assistant", "6 branches open, 0 resolved: scope, size limit, format, delivery, "
                  "permissions, audit.\n\nScope: does an export cover the filtered "
                  "view or the whole dataset?"),
    ("user", "The currently filtered view only."),
    ("assistant", "Scope: the filtered view, not the whole dataset. 1 of 6 resolved, "
                  "5 open.\n\nSize limit: how many rows may one export hold?"),
    ("user", "Refuse anything over 100k rows and tell the user to narrow the filter."),
    ("assistant", "Size limit: over 100,000 rows is refused with a message to narrow "
                  "the filter. 2 of 6 resolved, 4 open.\n\nFormat: which CSV dialect "
                  "and encoding?"),
    ("user", "RFC 4180, UTF-8 with a BOM so Excel opens it correctly."),
    ("assistant", "Format: RFC 4180, UTF-8 with BOM. 3 of 6 resolved, 3 open.\n\n"
                  "Delivery: a download in the request, or a background job?"),
    ("user", "Synchronous download. No email, no background job."),
    ("assistant", "Delivery: synchronous download only. 4 of 6 resolved, 2 open.\n\n"
                  "Permissions: who may export a report?"),
    ("user", "Anyone who can see the report can export it."),
    ("assistant", "Permissions: export follows view access. 5 of 6 resolved, 1 open."
                  "\n\nAudit: should exports be recorded in the audit log?"),
]
Q4 = ("/craft:grill-me Yes, log every export with the user, the timestamp, and the "
      "row count.")
SIX = (r"^(?=.*filter)(?=.*100[,. ]?000|.*100k)(?=.*(4180|BOM))"
       r"(?=.*(synchronous|download))(?=.*(can see|view access|permission))"
       r"(?=.*audit)")
case("grill-me--alignment-reached", Q4, {
    "b4-plan-file-exists": grader("file_exists", "", path="plans/csv-export.md",
                                  exists="true"),
    "b4-every-branch-in-plan": infile("plans/csv-export.md", SIX, flags="is"),
    "b4-criteria-per-item": infile(
        "plans/csv-export.md", r"(done when|acceptance|pass(es)? when|verified when)"
        r"([\s\S]*?(done when|acceptance|pass(es)? when|verified when)){6}", flags="i"),
    "b5-no-code-files": grader("file_exists", "", path='"**/*.go"', exists="false"),
}, hist=H4, answers=["Yes, save it as a plan at plans/csv-export.md."],
    extra_tags=("skill:plan-smith",),
    tools=("Read", "Glob", "Grep", "Skill", "Write", "Edit"), max_turns=40, timeout=300)

# 7. branch-nobody-present-can-resolve: summary with an owned open branch.
H7 = [
    ("user", "/craft:grill-me the multi-tenant rollout"),
    ("assistant", "5 branches open, 0 resolved: tenant order, isolation, per-tenant "
                  "concurrency ceiling, rollback, monitoring.\n\nTenant order: which "
                  "tenants go first?"),
    ("user", "Internal tenants first, then the three pilot customers, then everyone "
             "else in batches of 20."),
    ("assistant", "Tenant order: internal, then 3 pilots, then batches of 20. 1 of 5 "
                  "resolved, 4 open.\n\nIsolation: what must one tenant never see or "
                  "affect of another?"),
    ("user", "No shared rows: every query is scoped by tenant_id, and each tenant "
             "has its own job queue."),
    ("assistant", "Isolation: tenant_id on every query, one job queue per tenant. "
                  "2 of 5 resolved, 3 open.\n\nRollback: what triggers a rollback, "
                  "and how far back does it go?"),
    ("user", "An error rate above 2% for 10 minutes rolls that batch back to the old "
             "version; earlier batches stay."),
    ("assistant", "Rollback: over 2% errors for 10 minutes rolls back that batch "
                  "only. 3 of 5 resolved, 2 open.\n\nMonitoring: what must the "
                  "rollout dashboard show?"),
    ("user", "Per-tenant error rate, p95 latency, and queue depth, refreshed every "
             "minute."),
    ("assistant", "Monitoring: per-tenant error rate, p95 latency, queue depth, "
                  "1-minute refresh. 4 of 5 resolved, 1 open.\n\nConcurrency "
                  "ceiling: how many concurrent jobs may one tenant run?"),
]
Q7 = ("/craft:grill-me I don't know, and I can't find out today — the platform team "
      "owns that number. Let's wrap up.")
case("grill-me--branch-nobody-present-can-resolve", Q7, {
    "b5-plan-file-exists": grader("file_exists", "", path="plans/rollout.md",
                                  exists="true"),
    "b5-open-item-owner-and-question": infile(
        "plans/rollout.md",
        r"^#{2,3} [^\n]*(platform team[^\n]*(concurrency|ceiling)|"
        r"(concurrency|ceiling)[^\n]*platform team)", flags="im"),
    "b5-what-it-blocks": infile("plans/rollout.md", r"\bblock(s|ed|ing)?\b",
                                flags="i"),
    "b2-no-ceiling-number": infile(
        "plans/rollout.md",
        r"(ceiling|concurrency|\bcap\b)[^\n.]{0,40}\b\d+\s*(concurrent|jobs?|workers?|"
        r"requests?|slots?|tasks?)\b",
        match="not_contains", flags="i"),
}, hist=H7, answers=["Yes, save it as a plan at plans/rollout.md."],
    extra_tags=("skill:plan-smith",),
    tools=("Read", "Glob", "Grep", "Skill", "Write", "Edit"), max_turns=40, timeout=300)

print("ok")
