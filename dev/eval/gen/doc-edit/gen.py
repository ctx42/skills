#!/usr/bin/env python3
"""Generate srd/evals/doc-edit--* native eval cases."""
import json
import os
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
EV = os.path.join(ROOT, "srd/evals")
PC = open(os.path.join(EV, "fixtures/project-config.md")).read()
SUITE_DOCS = json.loads(open(os.path.join(EV, "mocks/srd/list_docs.md")).read())["docs"]

ENGLISH = "The user writes English; reply in English."
PERSONA = """Automated eval: the user is absent. Whenever the skill would stop and wait
for the user, take the next scripted answer below as the reply and continue
in this same run; never end the run to wait. If none fits, give the most
plausible answer and continue.

Scripted answers (pick the one that fits the question):
"""

BASE_TAGS = [
    "skill:doc-edit", "sec:doc-edit:usage", "sec:doc-edit:boundaries",
    "sec:doc-edit:sources-of-truth", "sec:doc-edit:session-start",
    "sec:doc-edit:edit-loop", "sec:doc-edit:facts",
    "sec:doc-edit:document-kinds", "sec:doc-edit:session-end",
    "ref:create/project-config", "ref:create/doc-corpus",
]

GLOSSARY = """---
title: Starforge Terms
---

# Starforge Terms

## Hot-Fire

A static firing of an engine or Stage at the test site.

## Hot-Fire Campaign

The series of Hot-Fires that clears a Stage to fly. Campaign hot-fires are
scheduled between 06:00 and 10:00 site time.
"""

SCRUB_REFUNDS = """---
id: 1000000105
title: Scrub Refunds
url: https://wiki.example.com/pages/1000000105
---

# Scrub Refunds

A scrub refund returns part or all of a launch slot fee to the customer when a
launch attempt is scrubbed.

## Refund rates

A weather or factory scrub refunds 100% of the slot fee. A customer-caused
scrub refunds 80% of it.

## Refund record

Each refund is recorded against the customer mission and the launch slot that
was scrubbed.
"""

SRD = """# Booster Turnaround

| Field      | Value                                               |
|------------|-----------------------------------------------------|
| Summary    | Plan each booster's turnaround without a planner.   |
| Maintainer | @dana.k                                             |
| Reviewers  | @john.k                                             |
| Tracking   | [SF-118](https://tracker.example.com/browse/SF-118) |
| Lifecycle  | DRAFT                                               |
| Mockups    | none                                                |

## Introduction

This document specifies how the platform plans a booster's turnaround on its
own once the booster lands on the drone ship Meridian. The system will plan
the turnaround work; it will not change how a booster is inspected.

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in RFC 2119 and RFC 8174 when, and only when, they
appear in all capitals, as shown here.

## Boundaries

### Included

- Planning the turnaround of an Ember booster after it lands.

### Excluded

- Changing how a landed booster is inspected.

## Requirements

### Booster Turnaround (BT)

- `BT-1` The system MUST open a turnaround plan when an Ember booster lands on
  Meridian.
- `BT-2` The system should kind of book the booster's next flight close enough
  to the end of its turnaround, more or less.
"""

GAP_0410 = {
    "id": "gap-0410", "status": "open", "kind": "missing", "answer": "",
    "ask": [], "asked": "",
    "srd_ref": "scrub-refunds", "doc_id": "1000000105", "heading_path": ["Scrub Refunds"],
    "search_terms": ["scrub refund payout deadline"], "hits": 2,
    "created": "2026-09-20T09:00:00Z", "filled_by": [],
    "topic": "Payout deadline for a scrub refund",
    "demand": "REF-3 needs the deadline by which a refund is paid out",
    "detail": "No corpus page states how many working days after a scrub its "
              "refund is paid out.",
    "target_claim": "", "file": "gap-0410-payout-deadline-for-a-scrub-refund.md",
}

NO_HITS = '{"results":[]}\n'


def world(gaps):
    if gaps:
        held = "At the start of this run the store holds exactly these gaps:\n\n" + \
            "\n\n".join(json.dumps(g, separators=(",", ":"), ensure_ascii=False) for g in gaps)
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
  `hits`) and answers {{"ok":true}}. Any other gap_id answers
  `ERROR: gap <gap_id> is not an editable draft or open gap`.
- submit_gap moves the draft named by `gap_id` to status `open` and answers
  {{"ok":true}}; a gap_id that is not a draft answers
  `ERROR: gap <gap_id> is not a draft`.
- discard_gap deletes the draft named by `gap_id` and answers
  {{"ok":true}}; same error rule as submit_gap.
- fill_gap on an open gap sets `filled_by` to the given list and, when
  `complete` is true, status `filled`; `remaining` replaces its detail. It
  answers {{"ok":true}}. An entry whose identity starts with `initiatives/`
  or `http` answers `ERROR: <entry> is not a corpus section outside the
  initiatives folder`; a gap_id that is not open or filled answers
  `ERROR: gap <gap_id> is not open`.
- list_gaps answers {{"gaps":[...]}} with the full current record of every
  gap that matches the call's filters: `status` keeps only gaps in exactly
  that status, `srd_ref` keeps only gaps whose srd_ref contains that text; an
  empty or missing filter keeps every gap. A `query` keeps only gaps whose
  topic, detail, or search_terms share a word with it, best match first,
  each with a `score` field. No match answers {{"gaps":[]}}.
"""


GAP_TOOLS = ["list_gaps", "report_gap", "update_gap", "submit_gap", "discard_gap", "fill_gap"]


def gap_mocks(gaps):
    w = world(gaps)
    return {f"{t}.md": w for t in GAP_TOOLS}


def get_doc(ident, path, text):
    return f"""---
type: agent
---
For the id `{ident}` or the path `{path}` answer with this document:

{text.split('---', 2)[2].strip()}

For any other id answer {{"error":"document not found"}}.
"""


def scaffold(files):
    s = ["#!/usr/bin/env bash", "set -euo pipefail",
         "cat > project-config.md <<'EOF_PC'", PC.rstrip("\n"), "EOF_PC"]
    for d in sorted({os.path.dirname(f) for f in files if os.path.dirname(f)}):
        s.append(f"mkdir -p {d}")
    for i, (path, content) in enumerate(files.items()):
        s += [f"cat > {path} <<'EOF_{i}'", content.rstrip("\n"), f"EOF_{i}"]
    return "\n".join(s) + "\n"


def g(fm, body=None):
    out = "---\n" + "\n".join(fm) + "\n---\n"
    return out + body + "\n" if body is not None else out


def g_regex(target, pat, flags=None, match=None):
    fm = ["type: regex", f"target: {target}"]
    if match:
        fm.append(f"match: {match}")
    if flags:
        fm.append(f'flags: "{flags}"')
    return g(fm, pat)


def g_file(path, pat, flags=None, match=None):
    return g_regex("{source: file, path: %s}" % path, pat, flags, match)


def g_used(tool, input_match=None, mn=None, mx=None, arm=None):
    fm = ["type: tool_used", f"tool: {tool}"]
    if input_match:
        fm.append(f"input_match: '{input_match}'")
    for k, v in (("min", mn), ("max", mx), ("arm", arm)):
        if v is not None:
            fm.append(f"{k}: {v}")
    return g(fm)


def g_never(tool, input_match=None):
    return g_used(tool, input_match, 0, 0, "both")


def g_order(btool, bmatch, atool, amatch):
    def side(t, m):
        return "{tool: %s%s}" % (t, f", input_match: '{m}'" if m else "")
    return g(["type: tool_order", f"before: {side(btool, bmatch)}", f"after: {side(atool, amatch)}"])


def write(path, text, mode=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)
    if mode:
        os.chmod(path, mode)


def case(name, prompt, files, graders, tags=(), answers=None, mocks=None, max_turns=50, timeout=300):
    d = os.path.join(EV, f"doc-edit--{name}")
    if os.path.isdir(d):
        shutil.rmtree(d)
    alltags = [f"case:doc-edit--{name}"] + BASE_TAGS + [t for t in tags if t not in BASE_TAGS]
    asp = ENGLISH
    if answers:
        asp += "\n" + PERSONA + "\n".join(f"{i}. {a}" for i, a in enumerate(answers, 1))
    fm = [f"tags: [{', '.join(alltags)}]", "runs: 1", f"max_turns: {max_turns}",
          f"timeout_seconds: {timeout}", "allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]",
          "append_system_prompt: |"]
    fm += [("  " + line) if line else "" for line in asp.splitlines()]
    write(os.path.join(d, "prompt.md"), "---\n" + "\n".join(fm) + "\n---\n\n" + prompt + "\n")
    write(os.path.join(d, "case.yaml"),
          f'schema_version: "1.1"\nname: doc-edit--{name}\ncontext:\n  scaffold_script: scaffold.sh\n')
    write(os.path.join(d, "scaffold.sh"), scaffold(files), 0o755)
    for fname, body in (mocks or {}).items():
        write(os.path.join(d, "mocks/srd", fname), body)
    for gname, body in graders.items():
        write(os.path.join(d, "graders", gname + ".md"), body)


GLO = "docs/glossary/terms.md"
REF = "docs/operations/scrub-refunds.md"
SRD_PATH = "initiatives/booster-turnaround/srd.md"
RDG = ["skill:report-doc-gap", "sec:report-doc-gap:invocation", "sec:report-doc-gap:workflow",
       "sec:report-doc-gap:the-gap-tools", "sec:report-doc-gap:the-gap-record"]

# 1 ------------------------------------------------------------------------
case(
    "glossary-entry-files-an-unconfirmable-fact",
    f"/srd:doc-edit {GLO} add to the Hot-Fire Campaign entry that a campaign "
    "runs all its hot-fires on one test stand",
    {GLO: GLOSSARY},
    tags=RDG,
    mocks={**gap_mocks([]), "get_doc.md": get_doc(GLO, GLO, GLOSSARY), "search.md": NO_HITS},
    answers=[
        "Asked whether the 06:00–10:00 hot-fire window is right, or to confirm it: "
        "\"I can't confirm that window — John K would know. Leave it as it is.\"",
        "To a proposal adding the one-test-stand fact to the Hot-Fire Campaign entry: \"Y\".",
        "To an offer to file, change, or drop a documentation gap: \"File it.\"",
        "Anything else: \"That's all — close the session.\"",
    ],
    graders={
        "b1-dedup-before-capture": g_order("mcp__srd__list_gaps", '"query":"[^"]+',
                                           "mcp__srd__report_gap", None),
        "b1-draft-on-the-glossary": g_regex(
            "mock_calls",
            r'^(?=[^\n]*"tool":"[^"]*report_gap")(?=[^\n]*"draft":true)'
            r'(?=[^\n]*"doc_id":"docs/glossary/terms\.md")[^\n]*$', "m"),
        "b2-answer-deferred": g_regex(
            "mock_calls",
            r'^(?=[^\n]*"tool":"[^"]*(report_gap|update_gap)")[^\n]*"answer":"deferred"', "m"),
        "b3-gap-filed": g_used("mcp__srd__submit_gap", "gap-0901", 1),
        "b4-fact-written": g_file(GLO, r"## Hot-Fire Campaign[\s\S]*one\s+test\s+stand"),
        "b4-window-kept": g_file(GLO, r"between\s+06:00\s+and\s+10:00"),
        "b5-front-matter-kept": g_file(GLO, r"^---\ntitle: Starforge Terms\n---\n"),
    },
)

# 2 ------------------------------------------------------------------------
REF_DOC = {"id": "1000000105", "path": REF, "rank": 4, "title": "Scrub Refunds"}
docs2 = [d for d in SUITE_DOCS if d.get("path") != REF] + [REF_DOC] \
    if REF_DOC not in SUITE_DOCS else SUITE_DOCS
case(
    "resolves-a-gap-in-the-edited-document",
    f"/srd:doc-edit {REF} add the payout deadline: a scrub refund is paid out "
    "within 10 working days of the scrub",
    {REF: SCRUB_REFUNDS},
    tags=["sec:doc-edit:resolving-a-gap"],
    mocks={**gap_mocks([GAP_0410]),
           "list_docs.md": json.dumps({"docs": docs2}, separators=(",", ":")) + "\n",
           "get_doc.md": get_doc("1000000105", REF, SCRUB_REFUNDS),
           "search.md": NO_HITS},
    answers=[
        "To a proposal that adds the 10-working-day payout deadline: \"Y\".",
        "Anything else: \"That's all — close the session.\"",
    ],
    graders={
        "b1-open-gaps-before-edit": g_order("mcp__srd__list_gaps", '"status":"open"',
                                            "Edit", '"file_path":"[^"]*scrub-refunds\\.md"'),
        "b2-fact-written": g_file(REF, r"10\s+working\s+days"),
        "b3-filled-by-id": g_regex(
            "mock_calls",
            r'^(?=[^\n]*"tool":"[^"]*fill_gap")(?=[^\n]*"gap_id":"gap-0410")'
            r'(?=[^\n]*"filled_by":\["1000000105#[a-z0-9-]+"\])(?=[^\n]*"complete":true)[^\n]*$', "m"),
        "b3-never-by-path": g_never("mcp__srd__fill_gap", "docs/operations"),
        "b3-edit-before-fill": g_order("Edit", '"file_path":"[^"]*scrub-refunds\\.md"',
                                       "mcp__srd__fill_gap", None),
        "b4-upstream-is-users": g_regex("last_message", r"upstream|\bpush", "i"),
        "b5-front-matter-kept": g_file(
            REF, r"^---\nid: 1000000105\ntitle: Scrub Refunds\n"
                 r"url: https://wiki\.example\.com/pages/1000000105\n---\n"),
        "b5-no-kb-handoff": g_never("Skill", '"skill":"(srd:)?kb"'),
    },
)

# 3 ------------------------------------------------------------------------
case(
    "hands-an-srd-to-edit",
    f"/srd:doc-edit {SRD_PATH} tighten the wording of BT-2",
    {SRD_PATH: SRD},
    tags=["skill:edit"],
    max_turns=30,
    graders={
        "b1-invokes-edit": g_used("Skill", '"skill":"(srd:)?edit"', 1),
        "b2-no-edit": g_never("Edit"),
        "b2-no-write": g_never("Write"),
    },
)

print("ok")
