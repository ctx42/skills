#!/usr/bin/env python3
"""Generate srd/evals/backlog--* native eval cases. Re-runnable; owns only backlog--*."""
import json
import os
import re
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
EVALS = os.path.join(ROOT, "srd/evals")

PROJECT_CONFIG = """---
mcp-server: srd
kb: kb
initiatives: initiatives
srd-standard: docs/srd-standard.md
glossary: docs/glossary
precedence:
  - kb
  - docs/concepts
  - docs/api
  - docs/operations
  - docs/glossary
---

# Project configuration (eval fixture)

EVAL TEST DATA ONLY. Copy this file to the root of a scenario's workspace so
the srd skills' gate finds a project; a scenario's `setup` overrides any key.
In an eval run, `srd/evals/mocks/srd/fixtures/srd-standard.md` stands in for the
`get_doc` result of `srd-standard` — see `dev/eval/blind-runner-prompt.md`.
"""

PERSONA = """Automated eval: the user is absent. Whenever the skill would stop and wait
for the user, take the next scripted answer below as the reply and continue
in this same run; never end the run to wait. If none fits, give the most
plausible answer and continue.
Before taking a scripted answer, write out in full, as your reply text, the
message you would send the user at that point.
"""

BASE_TAGS = [
    "skill:backlog", "sec:backlog:usage", "sec:backlog:boundaries",
    "sec:backlog:sources-of-truth", "sec:backlog:backends", "sec:backlog:workflow",
    "ref:create/project-config",
]
CORPUS_TAGS = ["ref:create/doc-corpus"]
DRAFT_TAGS = ["ref:kb/retrieval-authoring"]


def heredoc(path, body, tag):
    return f"cat > {path} <<'{tag}'\n{body.rstrip()}\n{tag}\n"


def scaffold(files, dirs=()):
    s = "#!/usr/bin/env bash\nset -euo pipefail\n"
    s += heredoc("project-config.md", PROJECT_CONFIG, "EOF_PC")
    s += "mkdir -p kb" + "".join(" " + d for d in dirs) + "\n"
    for i, (p, b) in enumerate(files.items()):
        s += heredoc(p, b, f"EOF_{i}")
    return s


def gaps_world(gaps):
    lines = "\n".join(json.dumps(g, separators=(",", ":")) for g in gaps)
    return f"""---
type: agent
---
The gap store holds exactly these gaps, one JSON record per line:

{lines}

Answer with {{"gaps":[...]}} holding every gap that matches the call's filters:
a `status` filter keeps only gaps with that status (so `status: filled` or
`status: draft` returns {{"gaps":[]}} unless a gap above has that status), an
`srd_ref` filter keeps only gaps whose srd_ref contains that text, a `stale:
true` filter keeps only gaps whose record has `stale: true` (none above
unless shown), a `query` keeps only gaps whose topic, detail, or search_terms
share a word with it, best match first, each with a `score` field. With no
filter, return every gap above.
"""


def gap(id_, topic, srd, terms, detail, claim="", doc_id="", heading=None, created="2026-09-08T10:12:00Z",
        answer="", hits=1, ask=(), asked=""):
    slug = "-".join("".join(c if c.isalnum() else " " for c in topic.lower()).split())[:60]
    return {"id": id_, "status": "open", "kind": "missing", "answer": answer, "ask": list(ask),
            "asked": asked, "srd_ref": srd,
            "doc_id": doc_id, "heading_path": heading or [], "search_terms": terms, "hits": hits,
            "created": created, "filled_by": [], "topic": topic,
            "demand": f"Blocks the requirements of {srd} that depend on this fact.",
            "detail": detail, "target_claim": claim, "file": f"{id_}-{slug}.md"}


ENGLISH = "The user writes English; reply in English."


def write_case(name, *, prompt, tags, max_turns, answers=None, files=None, dirs=(),
               mocks=None, graders=None, allowed="[Read, Glob, Grep, Skill, Write, Edit]"):
    d = os.path.join(EVALS, name)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, "graders"))
    fm = [f"tags: [{', '.join(['case:' + name] + tags)}]", "runs: 1",
          f"max_turns: {max_turns}", "timeout_seconds: 300", f"allowed_tools: {allowed}"]
    body = ENGLISH
    if answers:
        body += "\n" + PERSONA + "\n" + "\n".join(f"{i}. {a}" for i, a in enumerate(answers, 1))
    if body:
        fm.append("append_system_prompt: |\n" + "\n".join("  " + l if l else "" for l in body.split("\n")))
    with open(os.path.join(d, "prompt.md"), "w") as f:
        f.write("---\n" + "\n".join(fm) + "\n---\n\n" + prompt + "\n")
    with open(os.path.join(d, "case.yaml"), "w") as f:
        f.write(f'schema_version: "1.1"\nname: {name}\ncontext:\n  scaffold_script: scaffold.sh\n')
    p = os.path.join(d, "scaffold.sh")
    with open(p, "w") as f:
        f.write(scaffold(files or {}, dirs))
    os.chmod(p, 0o755)
    for tool, body in (mocks or {}).items():
        mp = os.path.join(d, "mocks/srd", tool + ".md")
        os.makedirs(os.path.dirname(mp), exist_ok=True)
        with open(mp, "w") as f:
            f.write(body.rstrip() + "\n")
    for body in (mocks or {}).values():
        # A {{file:fixtures/X}} include resolves against the case's own copy.
        for fx in sorted(set(re.findall(r"\{\{file:fixtures/([^}]+)\}\}", body))):
            dst = os.path.join(d, "mocks/srd/fixtures", fx)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(os.path.join(EVALS, "mocks/srd/fixtures", fx), dst)
    for gname, (front, body) in (graders or {}).items():
        with open(os.path.join(d, "graders", gname + ".md"), "w") as f:
            f.write("---\n" + front.strip() + "\n---\n" + (body.strip() + "\n" if body else ""))


# --- grader helpers -------------------------------------------------------

def rx(pattern, target="last_message", flags=None, match=None):
    front = "type: regex\n"
    front += f"target: {target}\n"
    if match:
        front += f'match: "{match}"\n' if ":" in match else f"match: {match}\n"
    if flags:
        front += f'flags: "{flags}"\n'
    return (front, pattern)


def file_rx(path, pattern, flags=None, match=None):
    return rx(pattern, "{source: file, path: %s}" % path, flags, match)


def never(tool, input_match=None):
    front = f"type: tool_used\ntool: {tool}\n"
    if input_match:
        front += f"input_match: '{input_match}'\n"
    return (front + "min: 0\nmax: 0\narm: both", "")


def used(tool, input_match=None, lo=1, hi=None):
    front = f"type: tool_used\ntool: {tool}\n"
    if input_match:
        front += f"input_match: '{input_match}'\n"
    front += f"min: {lo}"
    if hi is not None:
        front += f"\nmax: {hi}"
    return (front, "")


def order(before, after):
    def side(x):
        return x if isinstance(x, str) else "{tool: %s, input_match: '%s'}" % x
    return (f"type: tool_order\nbefore: {side(before)}\nafter: {side(after)}", "")


def llm(claim):
    return ("type: llm", "Ignore any trailing policy notice. " + claim)


KB_EDIT = r'"file_path":"[^"]*kb/'

# --- 1. opens-with-counts -------------------------------------------------

QUESTIONS_1 = [
    ("gap-0003", "Withdrawn build order and its part kits",
     "Does withdrawing a Build Order release its picked Part Kits?", "deferred", "2026-08-11", 1),
    ("gap-0006", "Launch Calendar slot fee currency",
     "Which currency does the Launch Calendar show slot fees in?", "deferred", "2026-08-27", 4),
    ("gap-0009", "Renaming a Customer Mission", "Can a customer rename a Customer Mission after booking?",
     "deferred", "2026-09-14", 1),
    ("gap-0004", "Per-payload insurance fee", "Is a per-payload insurance fee needed?",
     "unknown", "2026-08-19", 4),
    ("gap-0010", "Hot-fire data across a test-stand reset",
     "Does the test stand keep hot-fire channel data across a power reset?", "unknown", "2026-09-17", 1),
]
GAPS_1 = [
    gap("gap-0011", "Hot-fire recording retention period", "hot-fire-scheduler",
        ["hot-fire recording retention"], "The docs do not say how long a hot-fire recording is kept."),
    gap("gap-0014", "How long hot-fire recordings are kept", "telemetry-replay",
        ["hot-fire recording retention"], "Nowhere states when hot-fire recordings are deleted."),
    gap("gap-0016", "Bay Map for a stage without a bay", "bay-calendar",
        ["bay map unassigned stage"], "The Bay Map page does not cover a stage not yet assigned to a bay."),
    gap("gap-0018", "Part kit label length limit", "part-kit-tracking",
        ["part kit label length"], "No maximum length for a Part Kit label is documented."),
    gap("gap-0019", "Launch slot merge rules", "slot-swap",
        ["merge launch slots"], "The docs do not say when two adjacent Launch Slots can be merged."),
]
for g in GAPS_1:
    g["created"] = "2026-09-10T08:00:00Z"
GAPS_1 += [gap(i, t, "payload-booking", [], q, answer=a, hits=h, created=c + "T09:00:00Z")
           for i, t, q, a, c, h in QUESTIONS_1]


def cnt(n, word, label):
    return rf"(\b{n}\b|\b{word}\b)[^\n\d]{{0,30}}{label}|{label}[^\n\d]{{0,30}}(\b{n}\b|\b{word}\b)"


C_DEF, C_UNK, C_GAP = cnt(3, "three", "deferred"), cnt(2, "two", "unknown"), cnt(5, "five", "gap")

write_case(
    "backlog--opens-with-counts",
    prompt="/srd:backlog",
    tags=BASE_TAGS,
    max_turns=30,
    mocks={"list_gaps": gaps_world(GAPS_1)},
    graders={
        "b1-deferred-count": rx(C_DEF, flags="i"),
        "b1-unknowns-count": rx(C_UNK, flags="i"),
        "b1-gaps-count": rx(C_GAP, flags="i"),
        "b1-asks-for-a-pick": rx(r"\?"),
        "b1-no-kb-delegate": never("Skill", "srd:kb"),
        "b1-no-gap-filled": never("mcp__srd__fill_gap"),
        "b2-deferred-first": rx(r"^(?:(?!unknown|\bgaps?\b)[\s\S])*deferred", flags="i"),
        "b3-no-grill": never("Skill", "grill"),
        "b3-no-write": never("Write"),
        "b3-no-edit": never("Edit"),
        "b4-no-preamble": llm("The reply's first sentence gives backlog counts; it is not a "
                              "preamble announcing what the agent will do or narrating checks it ran."),
        "b4-deferred-count-once": rx(C_DEF, flags="i", match="count:1"),
        "b4-unknowns-count-once": rx(C_UNK, flags="i", match="count:1"),
        "b4-gaps-count-once": rx(C_GAP, flags="i", match="count:1"),
    },
)

# --- 3. reclassifies-rather-than-skipping ---------------------------------

ANVIL_PAGE = """---
title: Anvil engine
last_verified: 2026-09-12
---

# Anvil engine

## Chamber temperature reporting

> Not in the platform docs. Attested session 2026-09-12.

> Open: gap-0042.

An Anvil engine reports its chamber temperature on its own telemetry channel
in every downlink frame of a hot-fire.

## Provenance

Where each section of this page comes from.

| Section                       | Source             |
|-------------------------------|--------------------|
| Chamber temperature reporting | Session 2026-09-12 |
"""
GAPS_3 = [gap("gap-0042", "Anvil engine default overheat warning temperature", "session 2026-09-12",
              ["anvil overheat warning temperature"],
              "At what chamber temperature does an Anvil engine raise its default overheat warning?",
              doc_id="kb/anvil-engine.md", heading=["Anvil engine", "Chamber temperature reporting"],
              answer="deferred", created="2026-09-12T15:30:00Z")]
write_case(
    "backlog--reclassifies-rather-than-skipping",
    prompt="/srd:backlog deferred",
    tags=BASE_TAGS + ["ref:backlog/ask"],
    max_turns=50,
    answers=['To the overheat warning temperature question: "Actually nobody knows that yet — no one has '
             'measured it on the new injector."',
             'To any offer of another list: "No, that\'s all for today."'],
    files={"kb/anvil-engine.md": ANVIL_PAGE},
    mocks={"list_gaps": gaps_world(GAPS_3)},
    graders={
        "b1-answer-now-unknown": used("mcp__srd__update_gap", '"answer":"unknown"'),
        "b1-says-so": rx(r"\bunknown", flags="i"),
        "b2-no-kb-delegate": never("Skill", "srd:kb"),
        "b2-no-kb-write": never("Write", KB_EDIT),
        "b2-no-kb-edit": never("Edit", KB_EDIT),
        "b3-not-cleared": never("mcp__srd__update_gap", '"answer":"(deferred)?"'),
        "b3-not-closed": never("mcp__srd__wontfix_gap"),
        "b4-no-fill": never("mcp__srd__fill_gap"),
        "b4-no-gap-filed": never("mcp__srd__report_gap"),
        "b4-no-report-doc-gap": never("Skill", "report-doc-gap"),
        "b4-no-doc-gap-talk": rx(r"doc(umentation)? gap", flags="i", match="not_contains"),
    },
)

# --- 4. clusters-gaps-and-drafts-outside-the-corpus -----------------------

HF_DOC = "docs/engines/hot-fire-campaigns.md"
HF_ID = "1000000110"  # synced page: its front-matter id, not its path, is the identity
GAPS_4 = [
    gap("gap-0021", "How long hot-fire recordings are kept", "hot-fire-scheduler",
        ["hot-fire recording retention", "how long are hot-fire recordings kept", "delete hot-fire recordings"],
        "The docs do not say how long a hot-fire recording is kept before it is deleted, nor who can change "
        "that period.",
        doc_id=HF_ID, heading=["Hot-Fire Campaigns", "Recordings"],
        created="2026-09-08T10:12:00Z"),
    gap("gap-0027", "Bay Map for a stage without a bay", "bay-calendar",
        ["bay map stage without bay"], "The docs do not say what the Bay Map shows for a stage not yet "
        "assigned to a bay.",
        created="2026-09-15T14:40:00Z"),
    gap("gap-0034", "When hot-fire recordings are deleted", "telemetry-replay",
        ["hot-fire recording deletion", "hot-fire recording retention period"],
        "Nowhere states when hot-fire recordings are deleted.", created="2026-09-22T09:05:00Z"),
]
LIST_DOCS_4 = json.dumps({"docs": [
    {"id": i, "path": p, "rank": r, "title": t} for i, p, r, t in [
        ("docs/srd-standard.md",
         "docs/srd-standard.md", 6,
         "Requirements Specification Standard"),
        ("docs/glossary/terms.md", "docs/glossary/terms.md", 5, "Starforge Terms"),
        ("docs/glossary/ui-terms.md", "docs/glossary/ui-terms.md", 5, "UI Terms"),
        (HF_ID, HF_DOC, 4, "Hot-Fire Campaigns"),
        ("kb/_inbox.md", "kb/_inbox.md", 1, "Knowledge base inbox"),
    ]]}, separators=(",", ":"))
# The project's SRD standard, served from the suite fixture: the skill reads it
# through get_doc, and an unanswered get_doc stops the sitting.
STANDARD = ("docs/srd-standard.md", "{{file:fixtures/srd-standard.md}}")
GET_DOC_4 = f"""---
type: agent
---
For the id `{HF_ID}` or the path `{HF_DOC}` answer with this document:

# Hot-Fire Campaigns

## Campaign plan

An Anvil engine is cleared to fly after three hot-fires of at least 30
seconds each; a stage is cleared after one full-duration stage hot-fire.

## Recordings

Hot-fire recordings older than 30 days move to the cold archive. Archived
recordings stay downloadable but load more slowly.

""" + f"For `{STANDARD[0]}`:\n\n````markdown\n{STANDARD[1]}\n````\n\n" + \
    'For any other id answer {"error":"document not found"}.\n'
INBOX = """---
title: Knowledge base inbox
last_verified: 2026-09-01
---

# Knowledge base inbox
"""
case4_common = dict(
    prompt="/srd:backlog gaps",
    tags=BASE_TAGS + CORPUS_TAGS + DRAFT_TAGS + ["ref:backlog/gaps"],
    files={"kb/_inbox.md": INBOX},
    mocks={"list_gaps": gaps_world(GAPS_4), "get_doc": GET_DOC_4, "list_docs": LIST_DOCS_4},
)
URL_4 = "https://wiki.example.com/pages/1000000110"
DRAFT_4 = r'"file_path":"[^"]*drafts/hot-fire-recording-retention\.md"'
CORPUS_WRITE = r'"file_path":"[^"]*/(kb|docs)/(?!_inbox)'


write_case(
    "backlog--clusters-gaps-and-drafts-outside-the-corpus",
    max_turns=80,
    answers=['To which cluster to work: "The hot-fire recording retention one."',
             'To any question about the fact the page must state: "Hot-fire recordings are deleted 400 days '
             'after the hot-fire, archived or not. Only the test-site director can change that period, and '
             'only for a whole engine model. The 30-day move to the cold archive stays as documented."',
             'To where the draft goes: "Put it at `drafts/hot-fire-recording-retention.md`."',
             f'Once the draft is ready: "I\'ve published it: {URL_4} — the docs pull runs tonight."',
             'To any offer of another cluster or list: "No, that\'s all for today."'],
    graders={
        "b2-searches-before-drafting": order(("mcp__srd__search", "[Rr]etention|[Dd]elet"), ("Write", DRAFT_4)),
        "b2-reads-cited-page-before-drafting": order(("mcp__srd__get_doc", "hot-fire-campaigns|" + HF_ID),
                                                     ("Write", DRAFT_4)),
        "b2-draft-fixes-unranked-structurally": file_rx(
            "drafts/hot-fire-recording-retention.md",
            r"^aliases:[^\n]*(retention|delet)|^#+ [^\n]*(retention|delet)", flags="im"),
        "b2-draft-adds-absent-prose": file_rx("drafts/hot-fire-recording-retention.md", r"400 days"),
        "b3-draft-written": ("type: file_exists\npath: drafts/hot-fire-recording-retention.md\nexists: true", ""),
        "b3-no-write-into-a-source": never("Write", CORPUS_WRITE),
        "b3-no-edit-into-a-source": never("Edit", CORPUS_WRITE),
        "b4-no-fill": never("mcp__srd__fill_gap"),
        "b4-no-wontfix": never("mcp__srd__wontfix_gap"),
        "b4-says-open-until-pulled": llm("After the user gives the published URL, the agent's own reply text tells "
                                         "the user the cluster's gaps stay open until the page is pulled into the corpus."),
    },
    **case4_common,
)

# --- 5. sweeps-an-abandoned-srd ------------------------------------------

REJ, CO = "crew-seats", "payload-booking"


def table(head, rows):
    w = [max(len(r[i]) for r in [head, *rows]) for i in range(len(head))]
    line = lambda r: "| " + " | ".join(c.ljust(n) for c, n in zip(r, w)) + " |"
    return "\n".join([line(head), "|" + "|".join("-" * (n + 2) for n in w) + "|", *map(line, rows)]) + "\n"


PROV_5 = table(["Section", "Source"], [["Crew seat booking", f"{REJ} interview"],
                                       ["Mission visibility", f"{REJ}, {CO} interviews"],
                                       ["Crew seat limit", f"{REJ} interview"],
                                       ["Launch countdown", f"{CO} interview"]])
MP_PAGE = f"""---
title: Mission Portal
attested: 2026-09-02
srd_ref: {REJ}, {CO}
last_verified: 2026-09-20
---

# Mission Portal

## Crew seat booking

> Not in the platform docs. Attested {REJ} interview 2026-09-02.

A customer books a crew seat on an Ember mission from the Mission Portal. A
seat booking holds until its build order freezes.

## Mission visibility

> Not in the platform docs. Attested {REJ} interview 2026-09-02; {CO}
> interview 2026-09-20.

A Customer Mission is visible on the Mission Portal only to the accounts of
the customer who booked it.

## Crew seat limit

> Not in the platform docs. Attested {REJ} interview 2026-09-02.

An Ember mission carries at most 4 crew seats.

## Launch countdown

> Not in the platform docs. Attested {CO} interview 2026-09-20.

The Mission Dashboard counts down to the launch slot in the customer's time
zone.

## Provenance

Where each section of this page comes from.

{PROV_5}"""


def srd_doc(title, summary, lifecycle, ticket, code, included, req):
    head = table(["Field", "Value"], [
        ["Summary", summary],
        ["Maintainer", "Dana K"],
        ["Reviewers", "John K"],
        ["Tracking", f"[SF-{ticket}](https://tracker.example.com/browse/SF-{ticket})"],
        ["Lifecycle", lifecycle],
        ["Mockups", "none"],
    ])
    return f"""# {title}

{head}
## Introduction

Purpose: {summary[0].lower() + summary[1:]}

This document covers only that change; the Boundaries section lists what it
leaves out.

## Conventions

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to
be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they
appear in all capitals.

## Boundaries

### Included

- {included}

### Excluded

- Changes to launch slot pricing.

## Requirements

- `{code}-1` {req}
"""


SRDS_5 = {
    f"initiatives/{REJ}/srd.md": srd_doc(
        "Crew seats", "Let a customer book a crew seat on an Ember mission.", "WITHDRAWN", 131, "CS",
        "Booking a crew seat on an Ember mission.",
        "The Mission Portal MUST let a customer book a crew seat on an Ember mission."),
    f"initiatives/{CO}/srd.md": srd_doc(
        "Payload booking", "Let a customer book one payload onto one launch slot.", "APPROVED",
        112, "PB", "Booking a payload onto a launch slot and showing the booked mission.",
        "The Mission Portal MUST show each booked Customer Mission with its launch slot and a countdown."),
}
LIST_DOCS_5 = json.dumps({"docs": [
    {"id": i, "path": i, "rank": r, "title": t} for i, r, t in [
        ("docs/srd-standard.md", 6,
         "Requirements Specification Standard"),
        ("docs/glossary/terms.md", 5, "Starforge Terms"),
        ("kb/mission-portal.md", 1, "Mission Portal"),
        ("kb/_inbox.md", 1, "Knowledge base inbox"),
        (f"initiatives/{REJ}/srd.md", None, "Crew seats"),
        (f"initiatives/{CO}/srd.md", None, "Payload booking"),
    ]]}, separators=(",", ":")).replace(',"rank":null', "")
# An inbox that ends on a bare heading leaked into the next mocked gap-store
# answer (3 of 3 runs on 2026-10-30); a body line closes the page.
INBOX_5 = INBOX + "\nNo facts are waiting to be filed.\n"
GET_DOC_5 = "---\ntype: agent\n---\nAnswer each id or path with its document below, verbatim.\n\n" + "".join(
    f"For `{i}`:\n\n````markdown\n{b.rstrip()}\n````\n\n" for i, b in
    [*SRDS_5.items(), ("kb/mission-portal.md", MP_PAGE), ("kb/_inbox.md", INBOX_5), STANDARD]
) + 'For any other id answer {"error":"document not found"}.\n'


def store_world(gaps):
    held = "\n\n".join(json.dumps(g, separators=(",", ":"), ensure_ascii=False) for g in gaps)
    return f"""---
type: agent
---
The documentation-gap store of the srd server. At the start of this run
the store holds exactly these gaps:

{held}

Every earlier gap call this run changes the store; always answer from the
store as those calls left it.

- report_gap records a new gap: status `draft` when `draft` is true, else
  `open`. It takes the next unused id in the series gap-0901, gap-0902,
  gap-0903 (never one already issued) and answers {{"gap_id":"<new id>"}}.
- update_gap changes only the fields given on the draft or open gap named by
  `gap_id` (a field left out keeps its value; `add_hit` true adds 1 to
  `hits`) and answers {{"ok":true}}.
- submit_gap moves the draft named by `gap_id` to status `open` and answers
  {{"ok":true}}; a gap_id that is not a draft answers
  `ERROR: gap <gap_id> is not a draft`.
- reopen_gap moves the filled gap named by `gap_id` to status `open` and
  answers {{"ok":true}}; a gap_id that is not filled answers
  `ERROR: gap <gap_id> is not filled`.
- list_gaps answers {{"gaps":[...]}} with the full current record of every
  gap that matches the call's filters: `status` keeps only gaps in exactly
  that status, `srd_ref` keeps only gaps whose srd_ref contains that text,
  `stale: true` keeps only gaps whose record has `stale: true`; an empty or
  missing filter keeps every gap. A `query` keeps only gaps whose
  topic, detail, or search_terms share a word with it, best match first,
  each with a `score` field. No match answers {{"gaps":[]}}.
"""


REVERT_5 = gap("gap-0040", f"Crew seat limit rests on abandoned SRD {REJ}", REJ, ["crew seat limit"],
               f"Abandoned SRD {REJ} (Lifecycle WITHDRAWN) attested this section; no other SRD attests it.",
               doc_id="kb/mission-portal.md", heading=["Mission Portal", "Crew seat limit"],
               created="2026-09-28T09:00:00Z")
REVERT_5["kind"] = "wrong"
GAPS_5 = [
    gap("gap-0031", "Countdown after a scrub", CO, [],
        "What does the Mission Dashboard countdown show after a scrub?", answer="deferred",
        created="2026-09-20T11:00:00Z"),
    gap("gap-0035", "Mission Portal session length", CO, ["mission portal session length"],
        "The docs do not say how long a Mission Portal session lasts before sign-in is asked again.",
        created="2026-09-21T10:00:00Z"),
    REVERT_5,
]
WORLD_5 = store_world(GAPS_5)
RG = "mcp__srd__report_gap"

write_case(
    "backlog--sweeps-an-abandoned-srd",
    prompt="/srd:backlog",
    tags=BASE_TAGS + CORPUS_TAGS + ["skill:report-doc-gap", "sec:report-doc-gap:the-gap-tools",
                                    "sec:report-doc-gap:the-gap-record", "sec:report-doc-gap:workflow"],
    max_turns=60,
    files={"kb/mission-portal.md": MP_PAGE, "kb/_inbox.md": INBOX_5,
           **{p: b for p, b in SRDS_5.items()}},
    dirs=(f"initiatives/{REJ}", f"initiatives/{CO}"),
    mocks={"list_docs": LIST_DOCS_5, "get_doc": GET_DOC_5,
           **{t: WORLD_5 for t in ("list_gaps", "report_gap", "update_gap", "submit_gap", "reopen_gap")}},
    graders={
        "b1-two-gaps": used(RG, lo=2, hi=2),
        "b1-both-wrong": used(RG, '"kind":"wrong"', 2, 2),
        "b1-booking-section": used(RG, "[Cc]rew [Ss]eat [Bb]ooking", 1, 1),
        "b1-visibility-section": used(RG, "[Mm]ission [Vv]isibility", 1, 1),
        "b1-both-submitted": used("mcp__srd__submit_gap", lo=2, hi=2),
        "b2-detail-names-co-attester": used(RG, r'"detail":"(?:[^"\\]|\\.)*' + CO, 1, 1),
        "b3-none-for-covered-section": never(RG, "[Ss]eat [Ll]imit"),
        "b3-no-hit-on-covered-gap": never("mcp__srd__update_gap", "gap-0040"),
        "b4-sweep-in-opening": rx(rf"{REJ}[^\n]*(abandon|withdrawn|\b2\b|two)|(abandon|withdrawn)[^\n]*{REJ}", flags="i"),
        "b4-no-kb-write": never("Write", KB_EDIT),
        "b4-no-kb-edit": never("Edit", KB_EDIT),
    },
)

# --- 6. rechecks-stale-gaps -----------------------------------------------

SR_PAGE = """---
title: Scrub refunds
attested: 2026-09-20
srd_ref: scrub-refunds, payload-booking
last_verified: 2026-09-30
---

# Scrub refunds

## Customer scrub refund

> Not in the platform docs. Attested scrub-refunds interview 2026-09-20.

When the customer causes a scrub, Starforge pays back 80% of the slot fee;
the other 20% covers the pad crew's costs for the day.

## Refund claim deadline

> Not in the platform docs. Attested scrub-refunds interview 2026-09-20;
> payload-booking interview 2026-09-29.

A customer must claim a scrub refund within 60 days of the scrub; later
claims are refused.

## Provenance

Where each section of this page comes from.

""" + table(["Section", "Source"], [["Customer scrub refund", "scrub-refunds interview"],
                                     ["Refund claim deadline", "scrub-refunds, payload-booking interviews"]])
HF_PAGE_6 = """# Hot-Fire Campaigns

## Campaign plan

An Anvil engine is cleared to fly after three hot-fires of at least 30
seconds each; a stage is cleared after one full-duration stage hot-fire.

## Cold archive

Hot-fire recordings older than 30 days move to the cold archive. Archived
recordings stay downloadable but load more slowly.
"""
H_OLD = ["9f2c4e1a7b3d5f60812a4c6e8b0d2f4a6c8e0a2b4d6f8a0c2e4a6b8d0f2a4c6e",
         "1b3d5f7092a4c6e8f0b2d4a6c8e0f2b4d6a8c0e2f4b6d8a0c2e4f6b8d0a2c4e6",
         "c4e6a8b0d2f4a6c8e0b2d4f6a8c0e2b4d6f8a0c2e4b6d8f0a2c4e6b8d0f2a4c6"]


def filled(g, refs, stale_refs):
    g.update(status="filled", filled_by=refs, stale=True,
             stale_refs=[{"ref": r, "reason": why} for r, why in stale_refs])
    return g


SR = "kb/scrub-refunds.md"
GAPS_6 = [
    filled(gap("gap-0050", "Customer-caused scrub refund", "scrub-refunds", ["customer scrub refund"],
               "The docs do not say how much of the slot fee a customer-caused scrub refunds.",
               claim="A customer-caused scrub refunds 80% of the slot fee.",
               doc_id=SR, heading=["Scrub refunds", "Customer scrub refund"], created="2026-09-20T11:00:00Z"),
           [{"ref": f"{SR}#customer-scrub-refund", "hash": H_OLD[0]}],
           [(f"{SR}#customer-scrub-refund", "changed")]),
    filled(gap("gap-0051", "Scrub refund claim deadline", "scrub-refunds", ["scrub refund claim deadline"],
               "The docs do not say whether a scrub refund must be claimed by a deadline.",
               claim="A scrub refund can be claimed at any time; there is no deadline.", doc_id=SR,
               heading=["Scrub refunds", "Refund claim deadline"], created="2026-09-20T11:05:00Z"),
           [{"ref": f"{SR}#refund-claim-deadline", "hash": H_OLD[1]}],
           [(f"{SR}#refund-claim-deadline", "changed")]),
    filled(gap("gap-0052", "When hot-fire recordings move to the cold archive", "telemetry-replay",
               ["hot-fire recording cold archive", "hot-fire recordings older than 30 days"],
               "Nowhere states when hot-fire recordings leave fast storage.",
               claim="Hot-fire recordings older than 30 days move to the cold archive.", doc_id=HF_ID,
               heading=["Hot-Fire Campaigns", "Recordings"], created="2026-09-08T10:12:00Z"),
           [{"ref": f"{HF_ID}#recordings", "hash": H_OLD[2]}], [(f"{HF_ID}#recordings", "vanished")]),
    gap("gap-0055", "Part kit label length limit", "part-kit-tracking", ["part kit label length"],
        "No maximum length for a Part Kit label is documented.", created="2026-09-25T09:00:00Z"),
]
SECTIONS_6 = [f"{SR}#customer-scrub-refund", f"{SR}#refund-claim-deadline", f"{SR}#provenance",
              f"{HF_ID}#campaign-plan", f"{HF_ID}#cold-archive"]
WORLD_6 = f"""---
type: agent
---
The documentation-gap store of the srd server. At the start of this run
the store holds exactly these gaps:

{chr(10).join(json.dumps(g, separators=(",", ":")) for g in GAPS_6)}

Every earlier gap call this run changes the store; always answer from the
store as those calls left it. The corpus sections that resolve right now are
exactly: {", ".join(f"`{x}`" for x in SECTIONS_6)} (`{HF_DOC}` is accepted for
`{HF_ID}` and stored as `{HF_ID}`).

- list_gaps answers {{"gaps":[...],"invalid":[]}} with the full current record
  of every gap that matches the call's filters: `status` keeps only gaps in
  exactly that status, `srd_ref` keeps only gaps whose srd_ref contains that
  text, `stale: true` keeps only gaps whose record has `stale: true`; an empty
  or missing filter keeps every gap. A `query` keeps only gaps whose topic,
  detail, or search_terms share a word with it, best match first, each with a
  `score` field.
- fill_gap: when any `filled_by` entry is not one of the resolving sections,
  answer `ERROR: invalid: filled_by entry <entry> does not resolve` and change
  nothing. A `filled` gap given `complete` false or missing answers
  `ERROR: invalid: gap <gap_id> is filled; only complete true is accepted`.
  Otherwise replace the gap's filled_by with the entries, each with a fresh
  64-hex `hash`, drop its `stale` and `stale_refs`, set status `filled` when
  `complete` is true (an open gap without it stays open), replace `detail`
  with `remaining` when given, and answer {{"ok":true}}.
- reopen_gap moves the filled gap named by `gap_id` to status `open`, keeps
  its filled_by, stale, and stale_refs, appends the reason to `detail`, and
  answers {{"ok":true}}; a gap that is not filled answers
  `ERROR: invalid: gap <gap_id> is not filled`.
- update_gap changes only the fields given on the draft or open gap named by
  `gap_id` and answers {{"ok":true}}; wontfix_gap moves an open gap to
  `wontfix` and answers {{"ok":true}}.
"""
LIST_DOCS_6 = json.dumps({"docs": [
    {"id": i, "path": p, "rank": r, "title": t} for i, p, r, t in [
        ("docs/srd-standard.md",
         "docs/srd-standard.md", 6,
         "Requirements Specification Standard"),
        ("docs/glossary/terms.md", "docs/glossary/terms.md", 5, "Starforge Terms"),
        (HF_ID, HF_DOC, 4, "Hot-Fire Campaigns"),
        (SR, SR, 1, "Scrub refunds"),
        ("kb/_inbox.md", "kb/_inbox.md", 1, "Knowledge base inbox"),
    ]]}, separators=(",", ":"))
GET_DOC_6 = "---\ntype: agent\n---\nAnswer each id or path with its document below, verbatim.\n\n" + "".join(
    f"For `{i}`:\n\n````markdown\n{b.rstrip()}\n````\n\n" for i, b in
    [(f"{HF_ID}` or `{HF_DOC}", HF_PAGE_6), (SR, SR_PAGE), ("kb/_inbox.md", INBOX), STANDARD]
) + 'For any other id answer {"error":"document not found"}.\n'
SEARCH_6 = f"""---
type: agent
---
Answer {{"results":[...]}} with these corpus sections, each a result
{{"title","id","path","rank","heading_path","text","score"}}, keeping only the
ones whose text or heading shares a word (ignoring case and plurals) with the
query, best match first; none matching answers {{"results":[]}}:

- id `{HF_ID}`, path `{HF_DOC}`, rank 4, title "Hot-Fire Campaigns",
  heading_path ["Hot-Fire Campaigns", "Cold archive"], text "Hot-fire
  recordings older than 30 days move to the cold archive. Archived
  recordings stay downloadable but load more slowly."
- id `{HF_ID}`, path `{HF_DOC}`, rank 4, title "Hot-Fire Campaigns",
  heading_path ["Hot-Fire Campaigns", "Campaign plan"], text "An Anvil
  engine is cleared to fly after three hot-fires of at least 30 seconds
  each; a stage is cleared after one full-duration stage hot-fire."
- id `{SR}`, path `{SR}`, rank 1, title "Scrub refunds", heading_path
  ["Scrub refunds", "Customer scrub refund"], text "When the customer causes
  a scrub, Starforge pays back 80% of the slot fee; the other 20% covers the
  pad crew's costs for the day."
- id `{SR}`, path `{SR}`, rank 1, title "Scrub refunds", heading_path
  ["Scrub refunds", "Refund claim deadline"], text "A customer must claim a
  scrub refund within 60 days of the scrub; later claims are refused."
"""
FG = "mcp__srd__fill_gap"


def call(*parts):
    return "^" + "".join(f"(?=.*{x})" for x in parts)


write_case(
    "backlog--rechecks-stale-gaps",
    prompt="/srd:backlog",
    tags=BASE_TAGS + CORPUS_TAGS,
    max_turns=50,
    files={SR: SR_PAGE, "kb/_inbox.md": INBOX},
    mocks={"list_docs": LIST_DOCS_6, "get_doc": GET_DOC_6, "search": SEARCH_6,
           **{t: WORLD_6 for t in ("list_gaps", "fill_gap", "reopen_gap", "update_gap", "wontfix_gap")}},
    graders={
        "b1-refreshes-gap-0050": used(FG, call('"gap_id":"gap-0050"',
                                               r'"filled_by":\["kb/scrub-refunds\.md#customer-scrub-refund"\]',
                                               '"complete":true'), 1, 1),
        "b1-no-reopen-0050": never("mcp__srd__reopen_gap", "gap-0050"),
        "b2-reopens-gap-0051": used("mcp__srd__reopen_gap", call('"gap_id":"gap-0051"', '"reason":"[^"]'),
                                    1, 1),
        "b2-no-fill-0051": never(FG, "gap-0051"),
        "b3-repoints-gap-0052": used(FG, call('"gap_id":"gap-0052"',
                                              rf'"filled_by":\["{HF_ID}#cold-archive"\]',
                                              '"complete":true'), 1, 1),
        "b3-never-the-vanished-ref": never(FG, "#recordings"),
        "b4-lists-stale-before-filling": order(("mcp__srd__list_gaps", '"stale":true'), FG),
        "b4-clause-in-counts": rx(r"stale[^\n]{0,80}(reopen|refresh)|(reopen|refresh)[^\n]{0,80}stale",
                                  flags="i"),
    },
)

# --- 7. ask-writes-one-message-per-person ----------------------------------

GAPS_7 = [
    gap("gap-0061", "Picked part kit expiry", "part-kit-tracking", ["part kit expiry"],
        "Does a picked part kit expire when its stage integration slips, and after how long?",
        answer="deferred", created="2026-09-20T10:00:00Z", ask=["Maya R", "John K"]),
    gap("gap-0062", "Scrub refund payout time", "scrub-refunds", ["scrub refund payout"],
        "How many days after a scrub is the refund paid out?", answer="deferred",
        created="2026-09-21T10:00:00Z", ask=["Maya R"], asked="2026-09-28"),
    gap("gap-0063", "Bay D Ember capacity", "bay-calendar", ["bay d ember capacity"],
        "How many Ember boosters can Bay D hold at once?", answer="deferred", created="2026-09-22T10:00:00Z"),
]
WORLD_7 = f"""---
type: agent
---
The documentation-gap store of the srd server. At the start of this run
the store holds exactly these gaps:

{chr(10).join(json.dumps(g, separators=(",", ":")) for g in GAPS_7)}

Every earlier gap call this run changes the store; always answer from the
store as those calls left it.

- list_gaps answers {{"gaps":[...],"invalid":[]}} with the full current record
  of every gap that matches all of the call's filters: `status` keeps only
  gaps in exactly that status (no gap above is a `draft`), `srd_ref` keeps
  only gaps whose srd_ref contains that text, `stale: true` keeps only gaps
  whose record has `stale: true` (none above), `ask` keeps only gaps with a
  name in `ask` containing that text ignoring case, `asked: true` keeps only
  gaps whose `asked` is non-empty and `asked: false` only those whose `asked`
  is empty; an empty or missing filter keeps every gap. A `query` keeps only
  gaps whose topic, detail, or search_terms share a word with it, best match
  first, each with a `score` field.
- update_gap changes only the fields given on the draft or open gap named by
  `gap_id` (`ask` replaces the list; `asked` must be a YYYY-MM-DD date or
  empty, else answer `ERROR: invalid: asked must be YYYY-MM-DD`) and answers
  {{"ok":true}}.
"""
UG = "mcp__srd__update_gap"


def in_block(pat):
    """Some fenced block of the reply contains pat (fence pairs skipped from the start)."""
    skip = r"(?:[^`]|`(?!``))*"
    return rf"^{skip}(?:```[a-z]*\n(?:(?!```)[\s\S])*```{skip})*?```[a-z]*\n(?:(?!```)[\s\S])*?{pat}"


case7_common = dict(
    prompt="/srd:backlog ask",
    tags=BASE_TAGS + CORPUS_TAGS + ["ref:backlog/ask"],
    max_turns=30,
    mocks={"list_gaps": WORLD_7, "update_gap": WORLD_7},
)
write_case(
    "backlog--ask-writes-one-message-per-person--gate",
    graders={
        "b1-maya-block": rx(in_block(r"Maya R(?:(?!```)[\s\S])*?expir")),
        "b1-john-block": rx(in_block(r"John K(?:(?!```)[\s\S])*?expir")),
        "b1-two-blocks": rx("```", match="count:4"),
        "b2-no-refund-question": rx(in_block("refund"), flags="i", match="not_contains"),
        "b2-no-capacity-question": rx(in_block(r"Bay D|how many Ember"), flags="i", match="not_contains"),
        "b2-counts-asked": rx(r"already (been )?(asked|sent)|(\b1\b|\bone\b)[^\n]{0,60}\b(asked|sent)\b|\b(asked|sent)\b[^\n]{0,60}(\b1\b|\bone\b)",
                              flags="i"),
        "b2-offers-reminders": rx(r"ask reminders", flags="i"),
        "b3-no-gap-id-in-block": rx(in_block(r"gap-\d"), match="not_contains"),
        "b3-no-mention-in-block": rx(in_block(r"@\w"), match="not_contains"),
        "b4-no-asked-before-confirmation": never(UG),
    },
    **case7_common,
)
write_case(
    "backlog--ask-writes-one-message-per-person",
    answers=['To which messages were sent: "Sent both of them."',
             'To any offer of another list or more work: "No, that\'s all for today."'],
    graders={
        "b4-asked-on-gap-0061": used(UG, r'^(?=.*"gap_id":"gap-0061")(?=.*"asked":"\d{4}-\d{2}-\d{2}")', 1, 1),
        "b4-no-update-on-asked-gap": never(UG, "gap-0062"),
        "b4-no-update-on-unnamed-gap": never(UG, "gap-0063"),
    },
    **case7_common,
)
