#!/usr/bin/env python3
"""Generate srd/evals/report-doc-gap--* native eval cases."""
import json
import os
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
EV = os.path.join(ROOT, "srd/evals")

PC = """---
mcp-server: srd-doc
kb: kb
initiatives: initiatives
srd-standard: confluence/infraport/guidelines_for_software_requirements_documents.md
glossary: confluence/infraport/glossary
---

# Project configuration (eval fixture)

EVAL TEST DATA ONLY. Copy this file to the root of a scenario's workspace so
the srd skills' gate finds a project; a scenario's `setup` overrides any key.
In an eval run, `srd/evals/mocks/srd-doc/fixtures/srd-standard.md` stands in for the
`get_doc` result of `srd-standard` — see `dev/eval/blind-runner-prompt.md`.
"""

SRD = """# Gateway Failure Reporting

|                |                                                                     |
|----------------|---------------------------------------------------------------------|
| **Objective**  | Define how the system reports failed upstream calls to API clients. |
| **Initiative** | [INT-530](https://jira.example.com/browse/INT-530)                  |
| **Owners**     | @dana, @erik                                                        |
| **Status**     | IN PROGRESS                                                         |
| **Designs**    | N/A                                                                 |

> [!INFO]
> The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
> "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
> document are to be interpreted as described in
> [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
> [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
> appear in all capitals, as shown here.

## Introduction

This document specifies how the system answers an API client when the
upstream service behind the API Gateway fails or does not answer.

## Glossary

### Correlation ID

The identifier the API Gateway assigns to one client request.

## Scope

### In Scope

**SC-1:** Answering an API client when its upstream call fails.

**SC-2:** Logging failed upstream calls.

### Out of Scope

**OSC-1:** Changing the API Gateway's retry policy.

## Requirements

### Gateway (GW)

**GW-1:** The system MUST answer HTTP 502 when an upstream call fails after
the API Gateway's retries.

**GW-2:** The system MUST log each of the API Gateway's 3× retries of a
failed upstream call.

**GW-3:** The system MUST log each failed upstream call with the host name
of the upstream service.

**GW-4:** The system MUST put the request's Correlation ID in the body of
each HTTP 502 answer.
"""

SRD_FULL = SRD + """
### Retention Sweep (RS)

**RS-1:** The system MUST delete gateway failure log entries older than the
platform's 90-day retention window.

### Login Guard (GR)

**GR-7:** The system MUST lock a user account after 5 failed sign-in
attempts.

**GR-9:** The system MUST lock a user account after 3 failed sign-in
attempts.
"""

PERSONA = """Automated eval: the user is absent. Whenever the skill would stop and wait
for the user, take the next scripted answer below as the reply and continue
in this same run; never end the run to wait. If none fits, give the most
plausible answer and continue.
Before taking a scripted answer, write out in full, as your reply text, the
message you would send the user at that point. That message must appear
as visible reply text in this run before you continue; never answer
silently.

Scripted answers (pick the one that fits the question):
"""

BASE_TAGS = [
    "skill:report-doc-gap",
    "sec:report-doc-gap:usage",
    "sec:report-doc-gap:boundaries",
    "sec:report-doc-gap:support-files",
    "sec:report-doc-gap:invocation",
    "sec:report-doc-gap:workflow",
    "sec:report-doc-gap:the-gap-tools",
    "sec:report-doc-gap:the-gap-record",
    "ref:create/project-config",
]
REVIEW_TAGS = [
    "skill:review", "sec:review:usage", "sec:review:boundaries",
    "sec:review:sources-of-truth", "sec:review:documentation-corpus",
    "sec:review:modes", "sec:review:review-file-format",
    "sec:review:review-default", "ref:review/review-file",
    "ref:create/doc-corpus", "ref:create/authoring-guide", "ref:create/errata",
    "ref:create/srd-procedures",
]
GAP_TOOLS = ["list_gaps", "report_gap", "update_gap", "submit_gap", "discard_gap"]


def gap(gid, topic, detail, demand, terms, kind="missing", doc_id="",
        heading=None, url="", claim="", srd="specs/gateway.md"):
    return {"id": gid, "status": "draft", "kind": kind, "topic": topic,
            "doc_id": doc_id, "heading_path": heading, "source_url": url,
            "demand": demand, "target_claim": claim, "detail": detail,
            "search_terms": terms, "srd_ref": srd}


G_RETRY = gap("gap-0311", "API Gateway retry count for failed upstream calls",
              "No corpus document states how many times the API Gateway "
              "retries a failed upstream call.",
              "GW-2 needs the retry count", ["gateway retry count"])
G_BODY = gap("gap-0312", "API Gateway error body format",
             "No corpus page describes the JSON body of a gateway error answer.",
             "GW-4 needs the error body layout", ["gateway error body"])
G_SIG = gap("gap-0313", "Webhook signature header name",
            "No corpus page names the header that carries the webhook "
            "signature.",
            "GW-3 needs the signature header", ["webhook signature header"])
G_RETRY_PTR = gap(
    "gap-0311", "API Gateway retry count for failed upstream calls",
    "The API Gateway overview page describes how the gateway forwards "
    "upstream calls and answers HTTP 502, but never states how many times "
    "it retries a failed upstream call or how long it waits between tries.",
    "GW-2 needs the retry count",
    ["gateway retry count", "upstream retries"],
    doc_id="confluence/infraport/api-gateway/overview.md",
    heading=["API Gateway", "Upstream calls"],
    url="https://confluence.example.com/infraport/api-gateway/overview#upstream-calls")
G_RATE = gap("gap-0331", "API Gateway rate-limit response headers",
             "No corpus page names the headers the gateway sends with an "
             "HTTP 429 answer.",
             "GW-4 needs the rate-limit header names", ["rate limit headers"])
G_TIMEOUT = gap("gap-0341", "API Gateway upstream timeout value",
                "No corpus page states how long the API Gateway waits for an "
                "upstream service before giving up.",
                "GW-1 needs the upstream timeout", ["gateway upstream timeout"])


def fixed_list(gaps):
    return json.dumps({"gaps": gaps}, separators=(",", ":"), ensure_ascii=False) + "\n"


def world(gaps):
    if gaps:
        held = "At the start of this run the store holds exactly these gaps:\n\n" + \
            "\n\n".join(json.dumps(g, separators=(",", ":"), ensure_ascii=False)
                        for g in gaps)
    else:
        held = "At the start of this run the store holds no gaps at all."
    return f"""---
type: agent
---
The documentation-gap store of the srd-doc server. {held}

Every earlier gap call this run changes the store; always answer from the
store as those calls left it.

- report_gap records a new gap: status `draft` when `draft` is true, else
  `open`. It takes the next unused id in the series gap-0901, gap-0902,
  gap-0903 (never one already issued) and answers
  {{"id":"<new id>","status":"<status>"}}.
- update_gap replaces the descriptive fields of the draft named by
  `gap_id` with the ones given (a field left out becomes empty) and answers
  {{"ok":true,"id":"<gap_id>"}}. A gap_id the store does not hold, or one not
  in status `draft`, answers `ERROR: gap <gap_id> is not an editable draft`.
- submit_gap moves the draft named by `gap_id` to status `open` and answers
  {{"ok":true,"id":"<gap_id>","status":"open"}}; same error rule as update_gap.
- discard_gap deletes the draft named by `gap_id` and answers
  {{"ok":true,"id":"<gap_id>"}}; same error rule as update_gap.
- list_gaps answers {{"gaps":[...]}} with the full current record of every
  gap that matches the call's filters: `status` keeps only gaps in exactly
  that status, `srd_ref` keeps only gaps whose srd_ref contains that text; an
  empty or missing filter keeps every gap. No match answers {{"gaps":[]}}.
"""


def scaffold(config=True, srd=SRD, extra=""):
    s = "#!/usr/bin/env bash\nset -euo pipefail\n"
    if config:
        s += "cat > project-config.md <<'EOF_PC'\n" + PC + "EOF_PC\n"
    if srd:
        s += "mkdir -p specs\ncat > specs/gateway.md <<'EOF_SRD'\n" + srd + "EOF_SRD\n"
    s += extra
    return s


def write(path, text, mode=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)
    if mode:
        os.chmod(path, mode)


def yq(s):
    return "'" + s.replace("'", "''") + "'"


def grader(spec):
    """spec: dict with name, type, and fields; 'body' becomes the body."""
    fm = []
    body = spec.get("body")
    for k, v in spec.items():
        if k in ("name", "body"):
            continue
        if isinstance(v, dict):
            inner = ", ".join(f"{ik}: {yq(iv) if ik == 'input_match' else iv}"
                              for ik, iv in v.items())
            fm.append(f"{k}: {{{inner}}}")
        elif k in ("input_match",):
            fm.append(f"{k}: {yq(v)}")
        elif k in ("flags", "path"):
            fm.append(f'{k}: "{v}"')
        else:
            fm.append(f"{k}: {v}")
    out = "---\n" + "\n".join(fm) + "\n---\n"
    if body is not None:
        out += body + "\n"
    return out


ENGLISH = "The user writes English; reply in English."


def case(name, prompt, graders, tags=(), persona=None, mocks=None,
         scaffold_sh=None, max_turns=40, timeout=300, extra_yaml="",
         allowed="[Read, Glob, Grep, Skill, Write, Edit]"):
    d = os.path.join(EV, f"report-doc-gap--{name}")
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    all_tags = [f"case:report-doc-gap--{name}"] + BASE_TAGS + list(tags)
    seen, t2 = set(), []
    for t in all_tags:
        if t not in seen:
            seen.add(t)
            t2.append(t)
    fm = [f"tags: [{', '.join(t2)}]", "runs: 1", f"max_turns: {max_turns}",
          f"timeout_seconds: {timeout}", f"allowed_tools: {allowed}"]
    fm.append("append_system_prompt: |")
    for line in (ENGLISH + "\n" + (PERSONA + persona if persona else "")).rstrip("\n").split("\n"):
        fm.append(("  " + line) if line else "")
    write(os.path.join(d, "prompt.md"), "---\n" + "\n".join(fm) + "\n---\n\n" + prompt.strip() + "\n")
    if scaffold_sh is not None:
        write(os.path.join(d, "case.yaml"),
              f'schema_version: "1.1"\nname: report-doc-gap--{name}\n'
              f"{extra_yaml}context:\n  scaffold_script: scaffold.sh\n")
        write(os.path.join(d, "scaffold.sh"), scaffold_sh, 0o755)
    for fname, body in (mocks or {}).items():
        write(os.path.join(d, "mocks/srd-doc", fname), body)
    for g in graders:
        write(os.path.join(d, "graders", g["name"] + ".md"), grader(g))


def none_of(tool, name, input_match=None):
    g = {"name": name, "type": "tool_used", "tool": tool}
    if input_match:
        g["input_match"] = input_match
    g.update({"min": 0, "max": 0, "arm": "both"})
    return g


def agent_mocks(gaps):
    w = world(gaps)
    return {f"{t}.md": w for t in GAP_TOOLS}


# assistant-text helpers over the trace (one JSON event per line)
STR = r'(?:[^"\\]|\\.)*'
ATEXT = r'"type":"text","text":"' + STR

SRD_ARG = "/srd:report-doc-gap specs/gateway.md"

# 1. capture-does-not-interrupt -------------------------------------------
case(
    "capture-does-not-interrupt",
    "/srd:review specs/gateway.md",
    tags=REVIEW_TAGS + ["sec:report-doc-gap:the-doc-gap-vs-srd-gap-boundary"],
    scaffold_sh=scaffold(),
    mocks=agent_mocks([]),
    max_turns=60,
    graders=[
        {"name": "b1-light-draft-captured", "type": "regex", "target": "mock_calls",
         "flags": "m",
         "body": r'^(?=[^\n]*"tool":"[^"]*report_gap")(?=[^\n]*"draft":true)'
                 r'(?=[^\n]*"srd_ref":"specs/gateway\.md")(?=[^\n]*"search_terms":\["[^"]+")'
                 r'(?=[^\n]*"detail":"[^"]+")[^\n]*[Rr]etr'},
        none_of("mcp__srd-doc__submit_gap", "b2-no-submit"),
        none_of("mcp__srd-doc__update_gap", "b2-no-grill-update"),
        none_of("Skill", "b2-no-grill-me", "grill"),
        {"name": "b3-pass-reaches-review-file", "type": "file_exists",
         "path": "specs/gateway.review.md", "exists": "true"},
        {"name": "b3-capture-before-review-file", "type": "tool_order",
         "before": {"tool": "mcp__srd-doc__report_gap"},
         "after": {"tool": "Write", "input_match": r"gateway\.review\.md"}},
        {"name": "b3-end-of-pass-offer", "type": "regex", "target": "last_message",
         # An offer: a question, or a choice that names filing (a menu has no "?").
         "flags": "is", "body": r"^(?=.*retr)(?=.*\b(draft|gap-\d{4})\b)(?=.*(\?|\bfile\b))"},
    ])

# 2. drain-grill-confirm-file ---------------------------------------------
drain_mocks = {"list_gaps.md": fixed_list([G_RETRY, G_BODY])}
case(
    "drain-grill-confirm-file--gate", SRD_ARG,
    scaffold_sh=scaffold(), mocks=drain_mocks, max_turns=30,
    graders=[
        {"name": "b1-count-topics-offer", "type": "regex", "target": "last_message",
         "flags": "is",
         "body": r"^(?=.*\b(2|two)\b)(?=.*retr)(?=.*error body)(?=.*\bnow\b)"},
        {"name": "b2-depth-asked", "type": "regex", "target": "last_message",
         "flags": "is", "body": r"^(?=.*\blight\b)(?=.*\bheavy\b)"},
        none_of("mcp__srd-doc__submit_gap", "b1-nothing-filed-before-yes"),
        none_of("mcp__srd-doc__update_gap", "b1-nothing-grilled-before-yes"),
    ])
case(
    "drain-grill-confirm-file--gate-record",
    SRD_ARG + "\n\nWork them now, light; their one-line details are fine as they are.",
    scaffold_sh=scaffold(), mocks=drain_mocks, max_turns=30,
    graders=[
        {"name": "b2-record-shown", "type": "regex", "target": "last_message",
         "flags": "is",
         "body": r"^(?=.*(retr|error body))(?=.*\b(file|submit)\b)(?=.*\b(change|correct|edit|amend|adjust)\b)"},
        none_of("mcp__srd-doc__submit_gap", "b3-nothing-filed-before-yes"),
    ])
case(
    "drain-grill-confirm-file", SRD_ARG,
    scaffold_sh=scaffold(), mocks=drain_mocks, max_turns=50,
    persona="""1. Offered the unreported draft doc gaps: "Work them now."
2. Asked how deep to go on a gap: "Light."
3. Asked to confirm or sharpen a gap's one-line detail: "It's fine as it is."
4. Shown an assembled record and asked whether to file it: "Yes, file it."
""",
    graders=[
        {"name": "b3-retry-gap-filed", "type": "tool_used",
         "tool": "mcp__srd-doc__submit_gap", "input_match": "gap-0311", "min": 1},
        {"name": "b3-body-gap-filed", "type": "tool_used",
         "tool": "mcp__srd-doc__submit_gap", "input_match": "gap-0312", "min": 1},
        {"name": "b3-ids-named", "type": "regex", "target": "last_message",
         "flags": "s", "body": r"^(?=.*gap-0311)(?=.*gap-0312)"},
    ])

# 3. an-srd-gap-is-refused --------------------------------------------------
case(
    "an-srd-gap-is-refused",
    SRD_ARG + """

Hand-over from an srd:review pass on specs/gateway.md; capture these:

1. The Retention Sweep section (RS-1) cites a 90-day retention window the
   platform docs never state. Searches tried: "retention sweep window",
   "gateway log retention days"; no hit.
2. GR-7 and GR-9 both specify the login lockout threshold and disagree
   (5 failed attempts versus 3).
""",
    tags=["sec:report-doc-gap:the-doc-gap-vs-srd-gap-boundary", "ref:create/doc-corpus"],
    scaffold_sh=scaffold(srd=SRD_FULL), max_turns=30,
    graders=[
        {"name": "b1-retention-captured-as-draft", "type": "tool_used",
         "tool": "mcp__srd-doc__report_gap",
         "input_match": r'^(?=.*"draft":true)(?=.*([Rr]etention|90))', "min": 1},
        none_of("mcp__srd-doc__report_gap", "b2-lockout-not-captured",
                r"GR-7|GR-9|[Ll]ockout|[Ss]ign-in attempts"),
        none_of("mcp__srd-doc__submit_gap", "b2-nothing-filed"),
        {"name": "b3-caller-keeps-srd-defect", "type": "regex",
         "target": "last_message", "flags": "is",
         "body": r"^(?=.*(GR-7|GR-9|lockout))(?=.*(own findings|its findings|your findings|caller|SRD (gap|defect)|in the SRD))"},
    ])

# 4. opt-out-and-duplicate-merge ----------------------------------------------
merge_prompt = SRD_ARG + """

Hand-over from an srd:system-check pass on specs/gateway.md: no corpus
document states how many times the API Gateway retries a failed upstream
call. kind: missing. demand: GW-2 logs each of the gateway's 3× retries, and
the retry count cannot be confirmed. Searches tried: "API gateway resend
attempts", "retry policy upstream"; no relevant hit.

Once it is captured, work this SRD's drafts with me now. Skip the questions.
"""
merge_mocks = agent_mocks([G_RETRY_PTR])
UPD = r'(?=[^\n]*"tool":"[^"]*update_gap")'
case(
    "opt-out-and-duplicate-merge--gate", merge_prompt,
    scaffold_sh=scaffold(), mocks=merge_mocks, max_turns=30,
    graders=[
        {"name": "b3-record-shown-for-confirmation", "type": "regex",
         "target": "last_message", "flags": "is",
         "body": r"^(?=.*retr)(?=.*\b(file|submit)\b)(?=.*\b(change|correct|edit|amend|adjust)\b)"},
        none_of("mcp__srd-doc__submit_gap", "b3-nothing-filed-before-yes"),
    ])
case(
    "opt-out-and-duplicate-merge", merge_prompt,
    scaffold_sh=scaffold(), mocks=merge_mocks, max_turns=40,
    persona="""1. Shown the assembled record and asked whether to file it: "File it."
2. Asked how deep to go on a gap: "Skip the questions."
""",
    graders=[
        {"name": "b1-terms-unioned", "type": "regex", "target": "mock_calls",
         "flags": "m",
         "body": "^" + UPD + r'(?=[^\n]*"gap_id":"gap-0311")(?=[^\n]*gateway retry count)(?=[^\n]*resend attempts)'},
        none_of("mcp__srd-doc__report_gap", "b1-no-twin-captured"),
        {"name": "b1-pointers-survive", "type": "regex", "target": "mock_calls",
         "flags": "m", "match": "not_contains",
         "body": "^" + UPD + r'(?![^\n]*"doc_id":"confluence/infraport/api-gateway/overview\.md"[^\n]*)|^'
                 + UPD + r'(?![^\n]*"source_url":"https://confluence\.example\.com/infraport/api-gateway/overview#upstream-calls")|^'
                 + UPD + r'(?![^\n]*"heading_path":\["API Gateway","Upstream calls"\])'},
        {"name": "b1-detail-and-kind-survive", "type": "regex", "target": "mock_calls",
         "flags": "m", "match": "not_contains",
         "body": "^" + UPD + r'(?![^\n]*never states how many times)|^' + UPD + r'(?![^\n]*"kind":"missing")'},
        {"name": "b2-target-claim-empty", "type": "regex", "target": "mock_calls",
         "flags": "m", "match": "not_contains",
         "body": "^" + UPD + r'(?=[^\n]*"target_claim":"[^"\\])'},
        none_of("Skill", "b2-no-grill-me", "grill"),
        {"name": "b3-filed-after-yes", "type": "tool_used",
         "tool": "mcp__srd-doc__submit_gap", "input_match": "gap-0311", "min": 1},
    ])

# 5. gate-stops-without-the-server ---------------------------------------------
# The suite mocks always serve srd-doc and a case cannot remove a suite tool, so
# the config names a server no mock serves: its tools are absent from the
# session, which is the branch the scenario tests.
PC_NOSRV = PC.replace("mcp-server: srd-doc", "mcp-server: doc-corpus")
case(
    "gate-stops-without-the-server", SRD_ARG,
    scaffold_sh=scaffold(config=False, extra="cat > project-config.md <<'EOF_PC'\n" + PC_NOSRV + "EOF_PC\n"),
    mocks={"list_gaps.md": fixed_list([G_RETRY])}, max_turns=20,
    allowed="[Read, Glob, Grep, Skill, Write, Edit, WebFetch]",
    graders=[
        {"name": "b1-names-missing-tools", "type": "regex", "target": "last_message",
         "flags": "i", "body": r"no `?mcp__doc-corpus__\*?`? tools"},
        none_of("Read", "b1-srd-not-read", r"specs/gateway\.md"),
        none_of("Bash", "b1-srd-not-shell-read", r'"command":"(?:[^"\\]|\\.)*specs/gateway\.md'),
        {"name": "b2-start-server-mcp-rerun", "type": "regex", "target": "last_message",
         "flags": "is", "body": r"^(?=.*start[^\n]*doc-corpus)(?=.*/mcp)(?=.*(re-?run|run[^\n]{0,80}again))"},
        none_of("WebFetch", "b3-no-rest-call"),
        none_of("Bash", "b3-no-shell-fallback", r"curl|wget|https?://|git (clone|pull|fetch)"),
        none_of("mcp__srd-doc__list_gaps", "b3-no-other-server-gaps"),
        none_of("mcp__srd-doc__search", "b3-no-other-server-search"),
        {"name": "b3-nothing-kept-locally", "type": "file_exists", "path": "**",
         "exists": "false"},
        {"name": "b4-no-preamble", "type": "regex", "target": "last_message",
         "flags": "i", "match": "not_contains",
         "body": r"^\s*(I'll|I will|Let me|Running|Checking|First|Starting|Sure)"},
        {"name": "b4-mcp-advice-once", "type": "regex", "target": "last_message",
         "flags": "s", "match": "not_contains", "body": r"/mcp.*/mcp"},
    ])

# 6. declined-at-the-confirm-gate ---------------------------------------------
decl_mocks = {"list_gaps.md": fixed_list([G_RATE])}
case(
    "declined-at-the-confirm-gate--gate",
    SRD_ARG + "\n\nWork the draft now, light; its one-line detail is fine as it is.",
    scaffold_sh=scaffold(), mocks=decl_mocks, max_turns=30,
    graders=[
        {"name": "b3-amend-path-offered", "type": "regex", "target": "last_message",
         "flags": "is",
         "body": r"^(?=.*\b(file|submit)\b)(?=.*\b(change|correct|edit|amend|adjust)\b)(?=.*\b(drop|discard)\b)"},
        none_of("mcp__srd-doc__submit_gap", "b3-nothing-filed-before-answer"),
        none_of("mcp__srd-doc__discard_gap", "b3-nothing-discarded-before-answer"),
    ])
case(
    "declined-at-the-confirm-gate", SRD_ARG,
    scaffold_sh=scaffold(), mocks=decl_mocks, max_turns=40,
    persona="""1. Offered the unreported draft doc gap: "Work it now."
2. Asked how deep to go: "Light."
3. Asked to confirm or sharpen the one-line detail: "That's fine."
4. Shown the assembled record and asked whether to file it: "No. The record
   is wrong; don't file it, drop it."
""",
    graders=[
        none_of("mcp__srd-doc__submit_gap", "b1-files-nothing"),
        {"name": "b2-discard-called", "type": "tool_used",
         "tool": "mcp__srd-doc__discard_gap", "input_match": "gap-0331", "min": 1},
        {"name": "b2-says-discarded", "type": "regex", "target": "last_message",
         "flags": "i", "body": r"discard|dropped|deleted"},
        {"name": "b4-names-dropped-topic", "type": "regex", "target": "last_message",
         "flags": "i", "body": r"rate[- ]limit"},
    ])

# 7. missing-config-stops-the-run ---------------------------------------------
case(
    "missing-config-stops-the-run", SRD_ARG,
    scaffold_sh=scaffold(config=False), max_turns=20,
    graders=[
        {"name": "b1-names-file-and-start-dir", "type": "regex",
         "target": "last_message", "flags": "is",
         "body": r"^(?=.*project-config\.md)(?=.*specs)"},
    ] + [none_of(f"mcp__srd-doc__{t}", f"b2-no-{t.replace('_', '-')}") for t in GAP_TOOLS] + [
        none_of("Skill", "b2-no-grill-me", "grill"),
        none_of("mcp__srd-doc__search", "b3-no-server-probe"),
        none_of("mcp__srd-doc__list_docs", "b3-no-server-listing"),
        {"name": "b3-no-guessed-server", "type": "regex", "target": "last_message",
         "flags": "i", "match": "not_contains",
         "body": r"(us(e|ing)|assum\w*|fall(ing)? back to|carry(ing)? on with)[^.\n]{0,40}srd-doc"},
    ])

# 8. heavy-grill-and-session-opt-out -----------------------------------------
case(
    "heavy-grill-and-session-opt-out", SRD_ARG,
    scaffold_sh=scaffold(), mocks={"list_gaps.md": fixed_list([G_RETRY, G_BODY, G_SIG])},
    max_turns=80,
    persona="""1. Offered the unreported draft doc gaps: "Work them now."
2. Asked how deep to go on the first gap (the retry count): "Heavy."
3. Any interview question about the retry count: "The gateway retries a
   failed upstream call 3 times, 2 seconds apart, then answers 502. Ops
   calls it a resend. That is all I know."
4. Shown an assembled record and asked whether to file it: "File it."
5. Asked how deep to go on any later gap: "Just take the one-liners for the
   rest of these."
""",
    graders=[
        {"name": "b1-grill-me-invoked", "type": "tool_used", "tool": "Skill",
         "input_match": "grill-me", "min": 1},
        {"name": "b3-all-three-filed", "type": "tool_used",
         "tool": "mcp__srd-doc__submit_gap", "min": 3},
        {"name": "b4-opted-out-target-claim-empty", "type": "regex",
         "target": "mock_calls", "flags": "m", "match": "not_contains",
         "body": "^" + UPD + r'(?=[^\n]*"gap_id":"gap-031[23]")(?=[^\n]*"target_claim":"[^"\\])'},
    ])

case(
    "heavy-grill-and-session-opt-out--gate",
    SRD_ARG + "\n\nWork them now. Just take the one-liners for all of these; no questions.",
    scaffold_sh=scaffold(), mocks={"list_gaps.md": fixed_list([G_RETRY, G_BODY, G_SIG])},
    max_turns=30,
    graders=[
        {"name": "b2-no-depth-question", "type": "regex", "target": "last_message",
         "flags": "is", "match": "not_contains",
         "body": r"\blight\b.*\bheavy\b|\bheavy\b.*\blight\b|how deep"},
        {"name": "b3-record-shown-for-confirmation", "type": "regex",
         "target": "last_message", "flags": "is",
         "body": r"^(?=.*\b(file|submit)\b)(?=.*\b(change|correct|edit|amend|adjust)\b)"},
        none_of("mcp__srd-doc__submit_gap", "b3-nothing-filed-before-yes"),
        none_of("Skill", "b4-no-grill-me", "grill"),
    ])

# Bullet 2 sits at gap 3's pause, which a scripted run answers silently. Depth
# is scripted only for gaps 1 and 2: re-asked for gap 3, the run ends on that
# question; honored, gap 3 is filed like the others.
case(
    "heavy-grill-and-session-opt-out--stop", SRD_ARG,
    scaffold_sh=scaffold(), mocks={"list_gaps.md": fixed_list([G_RETRY, G_BODY, G_SIG])},
    max_turns=80,
    persona="""When the skill waits and none of the answers below fits, end the run there
instead of guessing an answer.
1. Offered the unreported draft doc gaps: "Work them now."
2. Asked how deep to go on the first gap (the retry count): "Heavy."
3. Any interview question about the retry count: "The gateway retries a
   failed upstream call 3 times, 2 seconds apart, then answers 502. Ops
   calls it a resend. That is all I know."
4. Shown any assembled record and asked whether to file it: "File it."
5. Asked how deep to go on the second gap (the error body format): "Just take
   the one-liners for the rest of these."
""",
    graders=[
        {"name": "b2-no-depth-reasked", "type": "regex", "target": "last_message",
         "flags": "is", "match": "not_contains",
         "body": r"\blight\b.*\bheavy\b|\bheavy\b.*\blight\b|how deep"},
        {"name": "b2-third-gap-filed", "type": "tool_used",
         "tool": "mcp__srd-doc__submit_gap", "min": 3},
    ])

# 9. drafts-survive-a-new-session ---------------------------------------------
case(
    "drafts-survive-a-new-session", SRD_ARG,
    scaffold_sh=scaffold(), mocks={"list_gaps.md": fixed_list([G_TIMEOUT])},
    max_turns=30,
    graders=[
        {"name": "b1-list-gaps-draft-for-srd", "type": "tool_used",
         "tool": "mcp__srd-doc__list_gaps",
         "input_match": r'^(?=.*"status":"draft")(?=.*"srd_ref":"[^"]*specs/gateway\.md")', "min": 1},
        none_of("Read", "b1-no-local-gap-read",
                r'"file_path":"(?![^"]*/(skills|lessons)/)[^"]*(gap|draft)'),
        # A shell path token naming gap/draft, outside skill and lesson dirs.
        none_of("Bash", "b1-no-local-gap-shell-read",
                r'"command":"(?:[^"\\]|\\.)*?(?<=[\s=]|\\n)(?![^\s"\\]*/(?:skills|lessons)/)'
                r'[^\s"\\]*(?:gap|draft)'),
        none_of("Glob", "b1-no-local-gap-glob", r'"pattern":"[^"]*(gap|draft)'),
        {"name": "b2-offers-to-work-it", "type": "regex", "target": "last_message",
         "flags": "is", "body": r"^(?=.*timeout)(?=.*\bwork\b)(?=.*\?)"},
        none_of("mcp__srd-doc__report_gap", "b2-not-captured-again"),
        none_of("Write", "b3-no-write"),
        none_of("Edit", "b3-no-edit"),
        {"name": "b3-no-file-created", "type": "file_exists", "path": "**",
         "exists": "false"},
    ])

print("ok")
