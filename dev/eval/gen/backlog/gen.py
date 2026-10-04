#!/usr/bin/env python3
"""Generate srd/evals/backlog--* native eval cases. Re-runnable; owns only backlog--*."""
import json
import os
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
EVALS = os.path.join(ROOT, "srd/evals")

PROJECT_CONFIG = """---
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
        answer="", hits=1):
    slug = "-".join("".join(c if c.isalnum() else " " for c in topic.lower()).split())[:60]
    return {"id": id_, "status": "open", "kind": "missing", "answer": answer, "srd_ref": srd,
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
    ("gap-0003", "Project archive and Tags", "Does a Project archive keep its Tags?", "deferred",
     "2026-08-11", 1),
    ("gap-0006", "Infobar flow unit", "Which unit does the Infobar use for flow?", "deferred",
     "2026-08-27", 4),
    ("gap-0009", "Renaming an EXAMPLE Instance", "Can a Customer rename an EXAMPLE Instance?", "deferred",
     "2026-09-14", 1),
    ("gap-0004", "Per-sensor-type propagation speed", "Is a per-sensor-type propagation speed needed?",
     "unknown", "2026-08-19", 4),
    ("gap-0010", "LoRa mote readings across a reboot", "Do LoRa motes keep readings across a reboot?",
     "unknown", "2026-09-17", 1),
]
GAPS_1 = [
    gap("gap-0011", "Sound File retention period", "sound-export",
        ["sound file retention"], "The docs do not say how long a Sound File is kept."),
    gap("gap-0014", "How long recordings are kept", "leak-archive",
        ["recording retention"], "Nowhere states when recordings are deleted."),
    gap("gap-0016", "Infobar for a Device without location", "device-map",
        ["infobar no location"], "The Infobar page does not cover a Device with no location."),
    gap("gap-0018", "Tag name length limit", "tag-import",
        ["tag name length"], "No maximum length for a Tag node name is documented."),
    gap("gap-0019", "Leak Instance merge rules", "leak-merge",
        ["merge leak instances"], "The docs do not say when two Leak Instances merge."),
]
for g in GAPS_1:
    g["created"] = "2026-09-10T08:00:00Z"
GAPS_1 += [gap(i, t, "sound-export", [], q, answer=a, hits=h, created=c + "T09:00:00Z")
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

BATTERY_PAGE = """---
title: Logger battery
last_verified: 2026-09-12
---

# Logger battery

## Battery reporting

> Not in the platform docs. Attested session 2026-09-12.

> Open: gap-0042.

An ALTECNO logger reports its battery voltage with every upload.

## Provenance

Where each section of this page comes from.

| Section           | Source             |
|-------------------|--------------------|
| Battery reporting | Session 2026-09-12 |
"""
GAPS_3 = [gap("gap-0042", "ALTECNO logger default battery-low threshold", "session 2026-09-12",
              ["altecno battery low threshold"],
              "What battery-low threshold does an ALTECNO logger use by default?",
              doc_id="kb/logger-battery.md", heading=["Logger battery", "Battery reporting"],
              answer="deferred", created="2026-09-12T15:30:00Z")]
write_case(
    "backlog--reclassifies-rather-than-skipping",
    prompt="/srd:backlog deferred",
    tags=BASE_TAGS,
    max_turns=50,
    answers=['To the battery-low threshold question: "Actually nobody knows that yet — no one has '
             'measured it on the current cells."',
             'To any offer of another list: "No, that\'s all for today."'],
    files={"kb/logger-battery.md": BATTERY_PAGE},
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

HK_DOC = "docs/operations/storage-housekeeping.md"
HK_ID = "1882030917"  # synced page: its front-matter id, not its path, is the identity
GAPS_4 = [
    gap("gap-0021", "How long raw Sound Files are kept", "sound-export",
        ["sound file retention", "how long are sound files kept", "delete sound files"],
        "The docs do not say how long a raw Sound File is kept before it is deleted, nor who can change that period.",
        doc_id=HK_ID, heading=["Storage housekeeping", "Cold storage"],
        created="2026-09-08T10:12:00Z"),
    gap("gap-0027", "Infobar for a Device without a location", "device-map",
        ["infobar device without location"], "The docs do not say what the Infobar shows for a Device with no location.",
        created="2026-09-15T14:40:00Z"),
    gap("gap-0034", "When recorded Sound Files are deleted", "leak-archive",
        ["sound file deletion", "recording retention period"],
        "Nowhere states when recorded Sound Files are deleted.", created="2026-09-22T09:05:00Z"),
]
LIST_DOCS_4 = json.dumps({"docs": [
    {"id": i, "path": p, "rank": r, "title": t} for i, p, r, t in [
        ("docs/guidelines_for_software_requirements_documents.md",
         "docs/guidelines_for_software_requirements_documents.md", 6,
         "Guidelines for Software Requirements Documents"),
        ("docs/glossary/main_glossary.md", "docs/glossary/main_glossary.md", 5, "Main Glossary"),
        ("docs/glossary/user_interface_glossary.md", "docs/glossary/user_interface_glossary.md", 5,
         "User Interface Glossary"),
        (HK_ID, HK_DOC, 4, "Storage housekeeping"),
        ("kb/_inbox.md", "kb/_inbox.md", 1, "Knowledge base inbox"),
    ]]}, separators=(",", ":"))
GET_DOC_4 = f"""---
type: agent
---
For the id `{HK_ID}` or the path `{HK_DOC}` answer with this document:

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
last_verified: 2026-09-01
---

# Knowledge base inbox
"""
case4_common = dict(
    prompt="/srd:backlog gaps",
    tags=BASE_TAGS + CORPUS_TAGS + DRAFT_TAGS,
    files={"kb/_inbox.md": INBOX},
    mocks={"list_gaps": gaps_world(GAPS_4), "get_doc": GET_DOC_4, "list_docs": LIST_DOCS_4},
)
URL_4 = "https://docs.example.com/operations/storage-housekeeping"
DRAFT_4 = r'"file_path":"[^"]*drafts/sound-file-retention\.md"'
CORPUS_WRITE = r'"file_path":"[^"]*/(kb|docs)/(?!_inbox)'


write_case(
    "backlog--clusters-gaps-and-drafts-outside-the-corpus",
    max_turns=80,
    answers=['To which cluster to work: "The Sound File retention one."',
             'To any question about the fact the page must state: "Raw Sound Files are deleted 400 days '
             'after upload, archived or not. Only an EXAMPLE administrator can change that period, and only '
             'for a whole EXAMPLE Instance. The 90-day move to the archive tier stays as documented."',
             'To where the draft goes: "Put it at `drafts/sound-file-retention.md`."',
             f'Once the draft is ready: "I\'ve published it: {URL_4} — the docs pull runs tonight."',
             'To any offer of another cluster or list: "No, that\'s all for today."'],
    graders={
        "b2-searches-before-drafting": order(("mcp__srd__search", "[Rr]etention|[Dd]elet"), ("Write", DRAFT_4)),
        "b2-reads-cited-page-before-drafting": order(("mcp__srd__get_doc", "storage-housekeeping|" + HK_ID),
                                                     ("Write", DRAFT_4)),
        "b2-draft-fixes-unranked-structurally": file_rx(
            "drafts/sound-file-retention.md",
            r"^aliases:[^\n]*(retention|delet)|^#+ [^\n]*(retention|delet)", flags="im"),
        "b2-draft-adds-absent-prose": file_rx("drafts/sound-file-retention.md", r"400 days"),
        "b3-draft-written": ("type: file_exists\npath: drafts/sound-file-retention.md\nexists: true", ""),
        "b3-no-write-into-a-source": never("Write", CORPUS_WRITE),
        "b3-no-edit-into-a-source": never("Edit", CORPUS_WRITE),
        "b4-no-fill": never("mcp__srd__fill_gap"),
        "b4-no-wontfix": never("mcp__srd__wontfix_gap"),
        "b4-says-open-until-pulled": llm("After the user gives the published URL, the agent's own reply text tells "
                                         "the user the cluster's gaps stay open until the page is pulled into the corpus."),
    },
    **case4_common,
)

# --- 5. sweeps-a-rejected-srd ---------------------------------------------

REJ, CO = "wishlist-v2", "gift-cards"


def table(head, rows):
    w = [max(len(r[i]) for r in [head, *rows]) for i in range(len(head))]
    line = lambda r: "| " + " | ".join(c.ljust(n) for c, n in zip(r, w)) + " |"
    return "\n".join([line(head), "|" + "|".join("-" * (n + 2) for n in w) + "|", *map(line, rows)]) + "\n"


PROV_5 = table(["Section", "Source"], [["Shared wishlist links", f"{REJ} interview"],
                                       ["Wishlist visibility", f"{REJ}, {CO} interviews"],
                                       ["Wishlist size limit", f"{REJ} interview"],
                                       ["Gift wrap", f"{CO} interview"]])
WL_PAGE = f"""---
title: Wishlists
attested: 2026-09-02
srd_ref: {REJ}, {CO}
last_verified: 2026-09-20
---

# Wishlists

## Shared wishlist links

> Not in the platform docs. Attested {REJ} interview 2026-09-02.

A reader can create a read-only link to one wishlist. The link never expires.

## Wishlist visibility

> Not in the platform docs. Attested {REJ} interview 2026-09-02; {CO}
> interview 2026-09-20.

A wishlist is private until its owner shares it.

## Wishlist size limit

> Not in the platform docs. Attested {REJ} interview 2026-09-02.

A wishlist holds at most 200 titles.

## Gift wrap

> Not in the platform docs. Attested {CO} interview 2026-09-20.

A gift card bought for a wishlist title can be gift-wrapped.

## Provenance

Where each section of this page comes from.

{PROV_5}"""


def srd_doc(title, objective, status):
    return f"""# SRD: {title}

- **Objective:** {objective}
- **Owners:** Ada Brook (primary), Lev Ortiz (secondary)
- **Initiative:** https://tickets.example.com/browse/BOOK-{len(title)}
- **Status:** {status}
- **Designs:** N/A

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to
be interpreted as described in RFC 2119 and RFC 8174.
"""


SRDS_5 = {
    f"initiatives/{REJ}/srd.md": srd_doc("Wishlist sharing v2", "Let a reader share a wishlist by link.",
                                         "REJECTED"),
    f"initiatives/{CO}/srd.md": srd_doc("Gift cards", "Let a reader buy a gift card for a wishlist title.",
                                        "ACCEPTED"),
}
LIST_DOCS_5 = json.dumps({"docs": [
    {"id": i, "path": i, "rank": r, "title": t} for i, r, t in [
        ("docs/guidelines_for_software_requirements_documents.md", 6,
         "Guidelines for Software Requirements Documents"),
        ("docs/glossary/main_glossary.md", 5, "Main Glossary"),
        ("kb/wishlists.md", 1, "Wishlists"),
        ("kb/_inbox.md", 1, "Knowledge base inbox"),
        (f"initiatives/{REJ}/srd.md", None, "SRD: Wishlist sharing v2"),
        (f"initiatives/{CO}/srd.md", None, "SRD: Gift cards"),
    ]]}, separators=(",", ":")).replace(',"rank":null', "")
GET_DOC_5 = "---\ntype: agent\n---\nAnswer each id or path with its document below, verbatim.\n\n" + "".join(
    f"For `{i}`:\n\n````markdown\n{b.rstrip()}\n````\n\n" for i, b in
    [*SRDS_5.items(), ("kb/wishlists.md", WL_PAGE), ("kb/_inbox.md", INBOX)]
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


REVERT_5 = gap("gap-0040", f"Wishlist size limit rests on rejected SRD {REJ}", REJ, ["wishlist size limit"],
               f"Abandoned SRD {REJ} (REJECTED) attested this section; no other SRD attests it.",
               doc_id="kb/wishlists.md", heading=["Wishlists", "Wishlist size limit"],
               created="2026-09-28T09:00:00Z")
REVERT_5["kind"] = "wrong"
GAPS_5 = [
    gap("gap-0031", "Gift card expiry", CO, [], "Does a gift card expire?", answer="deferred",
        created="2026-09-20T11:00:00Z"),
    gap("gap-0035", "Gift card refund window", CO, ["gift card refund"],
        "The docs do not say how long a gift card can be refunded.", created="2026-09-21T10:00:00Z"),
    REVERT_5,
]
WORLD_5 = store_world(GAPS_5)
RG = "mcp__srd__report_gap"

write_case(
    "backlog--sweeps-a-rejected-srd",
    prompt="/srd:backlog",
    tags=BASE_TAGS + CORPUS_TAGS + ["skill:report-doc-gap", "sec:report-doc-gap:the-gap-tools",
                                    "sec:report-doc-gap:the-gap-record", "sec:report-doc-gap:workflow"],
    max_turns=60,
    files={"kb/wishlists.md": WL_PAGE, "kb/_inbox.md": INBOX,
           **{p: b for p, b in SRDS_5.items()}},
    dirs=(f"initiatives/{REJ}", f"initiatives/{CO}"),
    mocks={"list_docs": LIST_DOCS_5, "get_doc": GET_DOC_5,
           **{t: WORLD_5 for t in ("list_gaps", "report_gap", "update_gap", "submit_gap", "reopen_gap")}},
    graders={
        "b1-two-gaps": used(RG, lo=2, hi=2),
        "b1-both-wrong": used(RG, '"kind":"wrong"', 2, 2),
        "b1-links-section": used(RG, "[Ss]hared [Ww]ishlist [Ll]inks", 1, 1),
        "b1-visibility-section": used(RG, "[Ww]ishlist [Vv]isibility", 1, 1),
        "b1-both-submitted": used("mcp__srd__submit_gap", lo=2, hi=2),
        "b2-detail-names-co-attester": used(RG, r'"detail":"(?:[^"\\]|\\.)*' + CO, 1, 1),
        "b3-none-for-covered-section": never(RG, "[Ss]ize [Ll]imit"),
        "b3-no-hit-on-covered-gap": never("mcp__srd__update_gap", "gap-0040"),
        "b4-sweep-in-opening": rx(rf"{REJ}[^\n]*(reject|\b2\b|two)|reject[^\n]*{REJ}", flags="i"),
        "b4-no-kb-write": never("Write", KB_EDIT),
        "b4-no-kb-edit": never("Edit", KB_EDIT),
    },
)

# --- 6. rechecks-stale-gaps -----------------------------------------------

GC_PAGE = """---
title: Gift cards
attested: 2026-09-20
srd_ref: gift-cards, checkout-v3
last_verified: 2026-09-30
---

# Gift cards

## Refund window

> Not in the platform docs. Attested gift-cards interview 2026-09-20.

A buyer may return an unused gift card for a full refund during the first 14
days after purchase. Later requests go to support, case by case.

## Gift card expiry

> Not in the platform docs. Attested gift-cards interview 2026-09-20;
> checkout-v3 interview 2026-09-29.

A gift card expires 24 months after purchase; its unspent balance is then
lost.

## Provenance

Where each section of this page comes from.

""" + table(["Section", "Source"], [["Refund window", "gift-cards interview"],
                                     ["Gift card expiry", "gift-cards, checkout-v3 interviews"]])
HK_PAGE_6 = """# Storage housekeeping

## Nightly jobs

The housekeeping job runs at 02:00 Instance time and compacts the time-series
store.

## Archive tier

Recordings older than 90 days move to the archive tier. Archived recordings
stay playable but load more slowly.
"""
H_OLD = ["9f2c4e1a7b3d5f60812a4c6e8b0d2f4a6c8e0a2b4d6f8a0c2e4a6b8d0f2a4c6e",
         "1b3d5f7092a4c6e8f0b2d4a6c8e0f2b4d6a8c0e2f4b6d8a0c2e4f6b8d0a2c4e6",
         "c4e6a8b0d2f4a6c8e0b2d4f6a8c0e2b4d6f8a0c2e4b6d8f0a2c4e6b8d0f2a4c6"]


def filled(g, refs, stale_refs):
    g.update(status="filled", filled_by=refs, stale=True,
             stale_refs=[{"ref": r, "reason": why} for r, why in stale_refs])
    return g


GC = "kb/gift-cards.md"
GAPS_6 = [
    filled(gap("gap-0050", "Gift card refund window", "gift-cards", ["gift card refund window"],
               "The docs do not say how long a gift card can be refunded.",
               claim="An unused gift card can be refunded within 14 days of purchase.",
               doc_id=GC, heading=["Gift cards", "Refund window"], created="2026-09-20T11:00:00Z"),
           [{"ref": f"{GC}#refund-window", "hash": H_OLD[0]}], [(f"{GC}#refund-window", "changed")]),
    filled(gap("gap-0051", "Gift card expiry", "gift-cards", ["gift card expiry"],
               "The docs do not say whether a gift card expires.",
               claim="A gift card never expires.", doc_id=GC, heading=["Gift cards", "Gift card expiry"],
               created="2026-09-20T11:05:00Z"),
           [{"ref": f"{GC}#gift-card-expiry", "hash": H_OLD[1]}], [(f"{GC}#gift-card-expiry", "changed")]),
    filled(gap("gap-0052", "When recordings move to the archive tier", "leak-archive",
               ["recording archive tier", "recordings older than 90 days"],
               "Nowhere states when recordings leave hot storage.",
               claim="Recordings older than 90 days move to the archive tier.", doc_id=HK_ID,
               heading=["Storage housekeeping", "Cold storage"], created="2026-09-08T10:12:00Z"),
           [{"ref": f"{HK_ID}#cold-storage", "hash": H_OLD[2]}], [(f"{HK_ID}#cold-storage", "vanished")]),
    gap("gap-0055", "Tag name length limit", "tag-import", ["tag name length"],
        "No maximum length for a Tag node name is documented.", created="2026-09-25T09:00:00Z"),
]
SECTIONS_6 = [f"{GC}#refund-window", f"{GC}#gift-card-expiry", f"{GC}#provenance",
              f"{HK_ID}#nightly-jobs", f"{HK_ID}#archive-tier"]
WORLD_6 = f"""---
type: agent
---
The documentation-gap store of the srd server. At the start of this run
the store holds exactly these gaps:

{chr(10).join(json.dumps(g, separators=(",", ":")) for g in GAPS_6)}

Every earlier gap call this run changes the store; always answer from the
store as those calls left it. The corpus sections that resolve right now are
exactly: {", ".join(f"`{x}`" for x in SECTIONS_6)} (`{HK_DOC}` is accepted for
`{HK_ID}` and stored as `{HK_ID}`).

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
        ("docs/guidelines_for_software_requirements_documents.md",
         "docs/guidelines_for_software_requirements_documents.md", 6,
         "Guidelines for Software Requirements Documents"),
        ("docs/glossary/main_glossary.md", "docs/glossary/main_glossary.md", 5, "Main Glossary"),
        (HK_ID, HK_DOC, 4, "Storage housekeeping"),
        (GC, GC, 1, "Gift cards"),
        ("kb/_inbox.md", "kb/_inbox.md", 1, "Knowledge base inbox"),
    ]]}, separators=(",", ":"))
GET_DOC_6 = "---\ntype: agent\n---\nAnswer each id or path with its document below, verbatim.\n\n" + "".join(
    f"For `{i}`:\n\n````markdown\n{b.rstrip()}\n````\n\n" for i, b in
    [(f"{HK_ID}` or `{HK_DOC}", HK_PAGE_6), (GC, GC_PAGE), ("kb/_inbox.md", INBOX)]
) + 'For any other id answer {"error":"document not found"}.\n'
SEARCH_6 = f"""---
type: agent
---
Answer {{"results":[...]}} with these corpus sections, each a result
{{"title","id","path","rank","heading_path","text","score"}}, keeping only the
ones whose text or heading shares a word (ignoring case and plurals) with the
query, best match first; none matching answers {{"results":[]}}:

- id `{HK_ID}`, path `{HK_DOC}`, rank 4, title "Storage housekeeping",
  heading_path ["Storage housekeeping", "Archive tier"], text "Recordings
  older than 90 days move to the archive tier. Archived recordings stay
  playable but load more slowly."
- id `{HK_ID}`, path `{HK_DOC}`, rank 4, title "Storage housekeeping",
  heading_path ["Storage housekeeping", "Nightly jobs"], text "The
  housekeeping job runs at 02:00 Instance time and compacts the time-series
  store."
- id `{GC}`, path `{GC}`, rank 1, title "Gift cards", heading_path
  ["Gift cards", "Refund window"], text "A buyer may return an unused gift
  card for a full refund during the first 14 days after purchase. Later
  requests go to support, case by case."
- id `{GC}`, path `{GC}`, rank 1, title "Gift cards", heading_path
  ["Gift cards", "Gift card expiry"], text "A gift card expires 24 months
  after purchase; its unspent balance is then lost."
"""
FG = "mcp__srd__fill_gap"


def call(*parts):
    return "^" + "".join(f"(?=.*{x})" for x in parts)


write_case(
    "backlog--rechecks-stale-gaps",
    prompt="/srd:backlog",
    tags=BASE_TAGS + CORPUS_TAGS,
    max_turns=50,
    files={GC: GC_PAGE, "kb/_inbox.md": INBOX},
    mocks={"list_docs": LIST_DOCS_6, "get_doc": GET_DOC_6, "search": SEARCH_6,
           **{t: WORLD_6 for t in ("list_gaps", "fill_gap", "reopen_gap", "update_gap", "wontfix_gap")}},
    graders={
        "b1-refreshes-gap-0050": used(FG, call('"gap_id":"gap-0050"',
                                               r'"filled_by":\["kb/gift-cards\.md#refund-window"\]',
                                               '"complete":true'), 1, 1),
        "b1-no-reopen-0050": never("mcp__srd__reopen_gap", "gap-0050"),
        "b2-reopens-gap-0051": used("mcp__srd__reopen_gap", call('"gap_id":"gap-0051"', '"reason":"[^"]'),
                                    1, 1),
        "b2-no-fill-0051": never(FG, "gap-0051"),
        "b3-repoints-gap-0052": used(FG, call('"gap_id":"gap-0052"',
                                              rf'"filled_by":\["{HK_ID}#archive-tier"\]',
                                              '"complete":true'), 1, 1),
        "b3-never-the-vanished-ref": never(FG, "cold-storage"),
        "b4-lists-stale-before-filling": order(("mcp__srd__list_gaps", '"stale":true'), FG),
        "b4-clause-in-counts": rx(r"stale[^\n]{0,80}(reopen|refresh)|(reopen|refresh)[^\n]{0,80}stale",
                                  flags="i"),
    },
)
