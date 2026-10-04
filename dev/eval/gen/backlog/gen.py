#!/usr/bin/env python3
"""Generate srd/evals/backlog--* native eval cases. Re-runnable; owns only backlog--*."""
import json
import os
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
EVALS = os.path.join(ROOT, "srd/evals")

PROJECT_CONFIG = """---
mcp-server: srd-doc
kb: kb
initiatives: initiatives
srd-standard: docs/guidelines_for_software_requirements_documents.md
glossary: docs/glossary
---

# Project configuration (eval fixture)

EVAL TEST DATA ONLY. Copy this file to the root of a scenario's workspace so
the srd skills' gate finds a project; a scenario's `setup` overrides any key.
In an eval run, `srd/evals/mocks/srd-doc/fixtures/srd-standard.md` stands in for the
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
KB_TAGS = [
    "sec:kb:boundaries", "sec:kb:the-kb-folder", "sec:kb:invocation",
    "sec:kb:workflow", "sec:kb:page-anatomy", "sec:kb:open-questions", "sec:kb:output",
]
CORPUS_TAGS = ["ref:create/doc-corpus"]
DRAFT_TAGS = ["ref:kb/retrieval-authoring"]


def table(rows):
    w = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    out = ["| " + " | ".join(c.ljust(w[i]) for i, c in enumerate(rows[0])) + " |",
           "|" + "|".join("-" * (x + 2) for x in w) + "|"]
    out += ["| " + " | ".join(c.ljust(w[i]) for i, c in enumerate(r)) + " |" for r in rows[1:]]
    return "\n".join(out)


OPEN_HEAD = ["Question", "Kind", "Raised", "Hits", "Lives in"]
CLOSED_HEAD = ["Question", "Kind", "Raised", "Hits", "Closed", "Answer", "Lives in"]


def open_questions(rows):
    closed = table([CLOSED_HEAD])
    return f"""---
title: Knowledge base open questions
cfsync-plugin: ignore-push
---

# Knowledge base open questions

Every open question the knowledge base tracks, one row each.

## Open

{table([OPEN_HEAD] + rows)}

## Closed

{closed}
"""


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
a `status` filter keeps only gaps with that status (so `status: kb` or
`status: draft` returns {{"gaps":[]}} unless a gap above has that status), an
`srd_ref` filter keeps only gaps whose srd_ref contains that text. With no
filter, return every gap above.
"""


def gap(id_, topic, srd, terms, detail, claim="", doc_id="", heading=None, url="", created="2026-09-08T10:12:00Z"):
    return {"id": id_, "status": "open", "created_at": created, "kind": "missing", "topic": topic,
            "doc_id": doc_id, "heading_path": heading or [], "source_url": url,
            "demand": f"Blocks the requirements of {srd} that depend on this fact.",
            "target_claim": claim, "detail": detail, "search_terms": terms, "srd_ref": srd,
            "kb_marked_at": None, "kb_entry": None}


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
        mp = os.path.join(d, "mocks/srd-doc", tool + ".md")
        os.makedirs(os.path.dirname(mp), exist_ok=True)
        with open(mp, "w") as f:
            f.write(body.rstrip() + "\n")
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
    return ("type: llm", "Ignore any trailing notice about a company directive "
            "(«Nutzung von Claude und andere AI-Agents»). " + claim)


KB_EDIT = r'"file_path":"[^"]*kb/'

# --- 1. opens-with-counts -------------------------------------------------

DEF_ROWS_1 = [
    ["Does a Project archive keep its Tags?", "deferred", "2026-08-11", "1", ""],
    ["Which unit does the Infobar use for flow?", "deferred", "2026-08-27", "4", ""],
    ["Can a Customer rename an EXAMPLE Instance?", "deferred", "2026-09-14", "1", ""],
    ["Is a per-sensor-type propagation speed needed?", "unknown", "2026-08-19", "4", ""],
    ["Do LoRa motes keep readings across a reboot?", "unknown", "2026-09-17", "1", ""],
]
GAPS_1 = [
    gap("gap-0011", "Sound File retention period", "initiatives/sound-export/srd.md",
        ["sound file retention"], "The docs do not say how long a Sound File is kept."),
    gap("gap-0014", "How long recordings are kept", "initiatives/leak-archive/srd.md",
        ["recording retention"], "Nowhere states when recordings are deleted."),
    gap("gap-0016", "Infobar for a Device without location", "initiatives/device-map/srd.md",
        ["infobar no location"], "The Infobar page does not cover a Device with no location."),
    gap("gap-0018", "Tag name length limit", "initiatives/tag-import/srd.md",
        ["tag name length"], "No maximum length for a Tag node name is documented."),
    gap("gap-0019", "Leak Instance merge rules", "initiatives/leak-merge/srd.md",
        ["merge leak instances"], "The docs do not say when two Leak Instances merge."),
]
for g in GAPS_1:
    g["created_at"] = "2026-09-10T08:00:00Z"


def cnt(n, word, label):
    return rf"(\b{n}\b|\b{word}\b)[^\n\d]{{0,30}}{label}|{label}[^\n\d]{{0,30}}(\b{n}\b|\b{word}\b)"


C_DEF, C_UNK, C_GAP = cnt(3, "three", "deferred"), cnt(2, "two", "unknown"), cnt(5, "five", "gap")

write_case(
    "backlog--opens-with-counts",
    prompt="/srd:backlog",
    tags=BASE_TAGS,
    max_turns=30,
    files={"kb/_open-questions.md": open_questions(DEF_ROWS_1)},
    mocks={"list_gaps": gaps_world(GAPS_1)},
    graders={
        "b1-deferred-count": rx(C_DEF, flags="i"),
        "b1-unknowns-count": rx(C_UNK, flags="i"),
        "b1-gaps-count": rx(C_GAP, flags="i"),
        "b1-asks-for-a-pick": rx(r"\?"),
        "b1-no-kb-delegate": never("Skill", "srd:kb"),
        "b1-no-gap-resolved": never("mcp__srd-doc__resolve_gap"),
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

BATTERY_PAGE = """---
title: Logger battery
last_verified: 2026-09-12
---

# Logger battery

## Battery reporting

> Not in the platform docs. Attested session 2026-09-12.

An ALTECNO logger reports its battery voltage with every upload.

## Open questions

- What battery-low threshold does an ALTECNO logger use by default?

## Provenance

Where each section of this page comes from.

| Section           | Source             |
|-------------------|--------------------|
| Battery reporting | Session 2026-09-12 |
"""
OQ_3 = open_questions([["What battery-low threshold does an ALTECNO logger use by default?", "deferred",
                        "2026-09-12", "1", "[logger-battery.md](logger-battery.md#open-questions)"]])
write_case(
    "backlog--reclassifies-rather-than-skipping",
    prompt="/srd:backlog deferred",
    tags=BASE_TAGS + KB_TAGS,
    max_turns=50,
    answers=['To the battery-low threshold question: "Actually nobody knows that yet — no one has '
             'measured it on the current cells."',
             'To any offer of another list: "No, that\'s all for today."'],
    files={"kb/_open-questions.md": OQ_3, "kb/logger-battery.md": BATTERY_PAGE},
    graders={
        "b1-kind-now-unknown": file_rx("kb/_open-questions.md",
                                       r"## Open[\s\S]*battery-low threshold[^\n]*\|\s*unknown\s*\|[\s\S]*## Closed"),
        "b1-delegated-to-kb": used("Skill", "srd:kb"),
        "b1-says-so": rx(r"\bunknown", flags="i"),
        "b2-kb-before-any-kb-edit": order(("Skill", "srd:kb"), ("Edit", KB_EDIT)),
        "b2-names-kb-as-writer": rx(r"srd:kb"),
        "b3-not-left-deferred": file_rx("kb/_open-questions.md",
                                        r"battery-low threshold[^\n]*\|\s*deferred\s*\|", match="not_contains"),
        "b4-no-gap-filed": never("mcp__srd-doc__report_gap"),
        "b4-no-report-doc-gap": never("Skill", "report-doc-gap"),
        "b4-no-user-manual-talk": rx(r"user manual|doc(umentation)? gap", flags="i", match="not_contains"),
    },
)

# --- 4. clusters-gaps-and-drafts-outside-the-corpus -----------------------

HK_DOC = "docs/operations/storage-housekeeping.md"
GAPS_4 = [
    gap("gap-0021", "How long raw Sound Files are kept", "initiatives/sound-export/srd.md",
        ["sound file retention", "how long are sound files kept", "delete sound files"],
        "The docs do not say how long a raw Sound File is kept before it is deleted, nor who can change that period.",
        doc_id=HK_DOC, heading=["Storage housekeeping", "Cold storage"],
        url="https://docs.example.com/operations/storage-housekeeping#cold-storage",
        created="2026-09-08T10:12:00Z"),
    gap("gap-0027", "Infobar for a Device without a location", "initiatives/device-map/srd.md",
        ["infobar device without location"], "The docs do not say what the Infobar shows for a Device with no location.",
        created="2026-09-15T14:40:00Z"),
    gap("gap-0034", "When recorded Sound Files are deleted", "initiatives/leak-archive/srd.md",
        ["sound file deletion", "recording retention period"],
        "Nowhere states when recorded Sound Files are deleted.", created="2026-09-22T09:05:00Z"),
]
LIST_DOCS_4 = json.dumps({"docs": [
    {"id": "docs/guidelines_for_software_requirements_documents.md",
     "title": "Guidelines for Software Requirements Documents"},
    {"id": "docs/glossary/main_glossary.md", "title": "Main Glossary"},
    {"id": "docs/glossary/user_interface_glossary.md", "title": "User Interface Glossary"},
    {"id": HK_DOC, "title": "Storage housekeeping"},
    {"id": "kb/_inbox.md", "title": "Knowledge base inbox"},
]}, separators=(",", ":"))
GET_DOC_4 = f"""---
type: agent
---
For the id `{HK_DOC}` answer with this document:

# Storage housekeeping

## Nightly jobs

The housekeeping job runs at 02:00 Instance time and compacts the time-series
store.

## Cold storage

Recordings older than 90 days move to the archive tier. Archived recordings
stay playable but load more slowly.

For any other id answer {{"error":"document not found"}}.
"""
INBOX = """---
title: Knowledge base inbox
cfsync-plugin: ignore-push
last_verified: 2026-09-01
---

# Knowledge base inbox
"""
case4_common = dict(
    prompt="/srd:backlog gaps",
    tags=BASE_TAGS + CORPUS_TAGS + DRAFT_TAGS,
    files={"kb/_inbox.md": INBOX, "kb/_open-questions.md": open_questions([])},
    mocks={"list_gaps": gaps_world(GAPS_4), "get_doc": GET_DOC_4, "list_docs": LIST_DOCS_4},
)
URL_4 = "https://docs.example.com/operations/storage-housekeeping"
DRAFT_4 = r'"file_path":"[^"]*drafts/sound-file-retention\.md"'
CORPUS_WRITE = r'"file_path":"[^"]*/(kb|docs)/(?!_inbox|_open-questions)'


def resolved(g):
    return rx(rf'resolve_gap(?=[^\n]*{g})(?=[^\n]*https://docs\.example\.com/)',
              target="mock_calls")


write_case(
    "backlog--clusters-gaps-and-drafts-outside-the-corpus",
    max_turns=80,
    answers=['To which cluster to work: "The Sound File retention one."',
             'To any question about the fact the page must state: "Raw Sound Files are deleted 400 days '
             'after upload, archived or not. Only an EXAMPLE administrator can change that period, and only '
             'for a whole EXAMPLE Instance. The 90-day move to the archive tier stays as documented."',
             'To where the draft goes: "Put it at `drafts/sound-file-retention.md`."',
             f'Once the draft is ready: "I\'ve published it: {URL_4}"',
             'To any offer of another cluster or list: "No, that\'s all for today."'],
    graders={
        "b2-searches-before-drafting": order(("mcp__srd-doc__search", "[Rr]etention|[Dd]elet"), ("Write", DRAFT_4)),
        "b2-reads-cited-page-before-drafting": order(("mcp__srd-doc__get_doc", "storage-housekeeping"),
                                                     ("Write", DRAFT_4)),
        "b2-draft-fixes-unranked-structurally": file_rx(
            "drafts/sound-file-retention.md",
            r"^aliases:[^\n]*(retention|delet)|^#+ [^\n]*(retention|delet)", flags="im"),
        "b2-draft-adds-absent-prose": file_rx("drafts/sound-file-retention.md", r"400 days"),
        "b3-draft-written": ("type: file_exists\npath: drafts/sound-file-retention.md\nexists: true", ""),
        "b3-no-write-into-a-source": never("Write", CORPUS_WRITE),
        "b3-no-edit-into-a-source": never("Edit", CORPUS_WRITE),
        "b4-resolves-gap-0021": resolved("gap-0021"),
        "b4-resolves-gap-0034": resolved("gap-0034"),
        "b4-leaves-gap-0027": rx(r'resolve_gap[^\n]*gap-0027', target="mock_calls", match="not_contains"),
    },
    **case4_common,
)
