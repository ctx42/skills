#!/usr/bin/env python3
"""Generate srd/evals/report-doc-gap--* native eval cases."""
import json
import os
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
EV = os.path.join(ROOT, "srd/evals")

PC = """---
mcp-server: srd
kb: kb
initiatives: initiatives
srd-standard: docs/guidelines_for_software_requirements_documents.md
glossary: docs/glossary
precedence:
  - kb
  - docs/concepts
  - docs/api-gateway
  - docs/operations
  - docs/glossary
---

# Project configuration (eval fixture)

EVAL TEST DATA ONLY. Copy this file to the root of a scenario's workspace so
the srd skills' gate finds a project; a scenario's `setup` overrides any key.
In an eval run, `srd/evals/mocks/srd/fixtures/srd-standard.md` stands in for the
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
GAP_TOOLS = ["list_gaps", "report_gap", "update_gap", "submit_gap", "discard_gap", "reopen_gap"]


def gap(gid, topic, detail, demand, terms, kind="missing", doc_id="",
        heading=None, claim="", srd="specs/gateway.md"):
    slug = "-".join("".join(c if c.isalnum() else " " for c in topic.lower()).split())[:60]
    return {"id": gid, "status": "draft", "kind": kind, "answer": "",
            "srd_ref": srd, "doc_id": doc_id, "heading_path": heading,
            "search_terms": terms, "hits": 1, "created": "2026-09-20T09:00:00Z",
            "filled_by": [], "topic": topic, "demand": demand, "detail": detail,
            "target_claim": claim, "file": f"{gid}-{slug}.md"}


G_RETRY = gap("gap-0311", "API Gateway retry count for failed upstream calls",
              "No corpus document states how many times the API Gateway "
              "retries a failed upstream call.",
              "GW-2 needs the retry count", ["gateway retry count"])
G_BODY = gap("gap-0312", "API Gateway error body format",
             "No corpus page describes the JSON body of a gateway error answer.",
             "GW-4 needs the error body layout", ["gateway error body"])
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
The documentation-gap store of the srd server. {held}

Every earlier gap call this run changes the store; always answer from the
store as those calls left it.

- report_gap records a new gap: status `draft` when `draft` is true, else
  `open`. It takes the next unused id in the series gap-0901, gap-0902,
  gap-0903 (never one already issued) and answers {{"gap_id":"<new id>"}}.
- update_gap changes only the fields given on the draft or open gap named by
  `gap_id` (a field left out keeps its value; `add_hit` true adds 1 to
  `hits`) and answers {{"ok":true}}. A gap_id the store does not hold, or one
  in status `filled` or `wontfix`, answers
  `ERROR: gap <gap_id> is not an editable draft or open gap`.
- submit_gap moves the draft named by `gap_id` to status `open` and answers
  {{"ok":true}}; a gap_id that is not a draft answers
  `ERROR: gap <gap_id> is not a draft`.
- discard_gap deletes the draft named by `gap_id` and answers
  {{"ok":true}}; same error rule as submit_gap.
- reopen_gap moves the filled gap named by `gap_id` to status `open`,
  appending `reason` to its detail, and answers {{"ok":true}}; a gap_id that
  is not filled answers `ERROR: gap <gap_id> is not filled`.
- list_gaps answers {{"gaps":[...]}} with the full current record of every
  gap that matches the call's filters: `status` keeps only gaps in exactly
  that status, `srd_ref` keeps only gaps whose srd_ref contains that text; an
  empty or missing filter keeps every gap. A `query` keeps only gaps whose
  topic, detail, or search_terms share a word with it, best match first,
  each with a `score` field. No match answers {{"gaps":[]}}.
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
        write(os.path.join(d, "mocks/srd", fname), body)
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
        {"name": "b1-dedup-query-first", "type": "tool_order",
         "before": {"tool": "mcp__srd__list_gaps", "input_match": r'"query":"[^"]+'},
         "after": {"tool": "mcp__srd__report_gap"}},
        {"name": "b1-light-draft-captured", "type": "regex", "target": "mock_calls",
         "flags": "m",
         "body": r'^(?=[^\n]*"tool":"[^"]*report_gap")(?=[^\n]*"draft":true)'
                 r'(?=[^\n]*"srd_ref":"specs/gateway\.md")(?=[^\n]*"search_terms":\["[^"]+")'
                 r'(?=[^\n]*"detail":"[^"]+")[^\n]*[Rr]etr'},
        none_of("mcp__srd__submit_gap", "b2-no-submit"),
        none_of("mcp__srd__update_gap", "b2-no-grill-update"),
        none_of("Skill", "b2-no-grill-me", "grill"),
        {"name": "b3-pass-reaches-review-file", "type": "file_exists",
         "path": "specs/gateway.review.md", "exists": "true"},
        {"name": "b3-capture-before-review-file", "type": "tool_order",
         "before": {"tool": "mcp__srd__report_gap"},
         "after": {"tool": "Write", "input_match": r"gateway\.review\.md"}},
        {"name": "b3-end-of-pass-offer", "type": "regex", "target": "last_message",
         # An offer: a question, or a choice that names filing (a menu has no "?").
         "flags": "is", "body": r"^(?=.*retr)(?=.*\b(draft|gap-\d{4})\b)(?=.*(\?|\bfile\b))"},
    ])

# 2. drain-grill-confirm-file ---------------------------------------------
drain_mocks = {"list_gaps.md": fixed_list([G_RETRY, G_BODY])}
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
         "tool": "mcp__srd__submit_gap", "input_match": "gap-0311", "min": 1},
        {"name": "b3-body-gap-filed", "type": "tool_used",
         "tool": "mcp__srd__submit_gap", "input_match": "gap-0312", "min": 1},
        {"name": "b3-ids-named", "type": "regex", "target": "last_message",
         "flags": "s", "body": r"^(?=.*gap-0311)(?=.*gap-0312)"},
    ])

# 9. drafts-survive-a-new-session ---------------------------------------------
case(
    "drafts-survive-a-new-session", SRD_ARG,
    scaffold_sh=scaffold(), mocks={"list_gaps.md": fixed_list([G_TIMEOUT])},
    max_turns=30,
    graders=[
        {"name": "b1-list-gaps-draft-for-srd", "type": "tool_used",
         "tool": "mcp__srd__list_gaps",
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
        none_of("mcp__srd__report_gap", "b2-not-captured-again"),
        none_of("Write", "b3-no-write"),
        none_of("Edit", "b3-no-edit"),
        {"name": "b3-no-file-created", "type": "file_exists", "path": "**",
         "exists": "false"},
    ])

print("ok")
