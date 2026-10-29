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
title: Main Glossary
---

# Main Glossary

## Ledger

An account book that records every payment posted to one merchant account.

## Reconciliation

The comparison of two Ledgers' postings to find a payment mismatch between
them. A reconciliation run uses postings made between 02:00 and 04:00.
"""

RECONCILIATION = """---
id: 2215906431
title: Reconciliation
url: https://wiki.example.com/pages/2215906431
---

# Reconciliation

A reconciliation run compares the postings of two Ledgers to find a payment
mismatch between them.

## Prerequisites

Both Ledgers use the same currency and close at the same cut-off.

## Results

A run reports each mismatch as an amount and the pair of postings behind it.
"""

SRD = """# Automated Reconciliation

| Field      | Value                                                 |
|------------|-------------------------------------------------------|
| Summary    | Run reconciliations without an operator.              |
| Maintainer | @anna.keller                                          |
| Reviewers  | @marek.nowak                                          |
| Tracking   | [ABC-640](https://tickets.example.com/browse/ABC-640) |
| Lifecycle  | DRAFT                                                 |
| Mockups    | none                                                  |

## Introduction

This document specifies how the platform starts reconciliation runs on its own.
The system will start runs without an operator; it will not change how a run
compares postings.

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in RFC 2119 and RFC 8174 when, and only when, they
appear in all capitals, as shown here.

## Boundaries

### Included

- Starting reconciliation runs without an operator.

### Excluded

- Changing how a run compares postings.

## Requirements

### Automation (AC)

- `AC-1` The system MUST start a reconciliation run each night.
- `AC-2` The system should kind of pick Ledgers that are close enough to each
  other, more or less.
"""

GAP_0410 = {
    "id": "gap-0410", "status": "open", "kind": "missing", "answer": "",
    "ask": [], "asked": "",
    "srd_ref": "autoco", "doc_id": "2215906431", "heading_path": ["Reconciliation"],
    "search_terms": ["reconciliation minimum overlap"], "hits": 2,
    "created": "2026-09-20T09:00:00Z", "filled_by": [],
    "topic": "Minimum posting overlap for a reconciliation run",
    "demand": "AC-1 needs the overlap a nightly run must schedule",
    "detail": "No corpus page states how many minutes two Ledgers' postings "
              "must overlap for a reconciliation run.",
    "target_claim": "", "file": "gap-0410-minimum-posting-overlap-for-a-reconciliation-run.md",
}


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


GLO = "docs/glossary/main_glossary.md"
REC = "docs/operations/reconciliation.md"
RDG = ["skill:report-doc-gap", "sec:report-doc-gap:invocation", "sec:report-doc-gap:workflow",
       "sec:report-doc-gap:the-gap-tools", "sec:report-doc-gap:the-gap-record"]

# 1 ------------------------------------------------------------------------
case(
    "glossary-entry-files-an-unconfirmable-fact",
    f"/srd:doc-edit {GLO} add to the Reconciliation entry that a reconciliation "
    "run needs two Ledgers in the same currency",
    {GLO: GLOSSARY},
    tags=RDG,
    mocks={**gap_mocks([]), "get_doc.md": get_doc(GLO, GLO, GLOSSARY)},
    answers=[
        "Asked whether the 02:00–04:00 posting window is right, or to confirm it: "
        "\"I can't confirm that window — the finance team would know. Leave it as it is.\"",
        "To a proposal adding the same-currency fact to the Reconciliation entry: \"Y\".",
        "To an offer to file, change, or drop a documentation gap: \"File it.\"",
        "Anything else: \"That's all — close the session.\"",
    ],
    graders={
        "b1-dedup-before-capture": g_order("mcp__srd__list_gaps", '"query":"[^"]+',
                                           "mcp__srd__report_gap", None),
        "b1-draft-on-the-glossary": g_regex(
            "mock_calls",
            r'^(?=[^\n]*"tool":"[^"]*report_gap")(?=[^\n]*"draft":true)'
            r'(?=[^\n]*"doc_id":"docs/glossary/main_glossary\.md")[^\n]*$', "m"),
        "b2-answer-deferred": g_regex(
            "mock_calls",
            r'^(?=[^\n]*"tool":"[^"]*(report_gap|update_gap)")[^\n]*"answer":"deferred"', "m"),
        "b3-gap-filed": g_used("mcp__srd__submit_gap", "gap-0901", 1),
        "b4-fact-written": g_file(GLO, r"## Reconciliation[\s\S]*same\s+currency"),
        "b4-window-kept": g_file(GLO, r"between\s+02:00\s+and\s+04:00"),
        "b5-front-matter-kept": g_file(GLO, r"^---\ntitle: Main Glossary\n---\n"),
    },
)

# 2 ------------------------------------------------------------------------
docs2 = SUITE_DOCS + [{"id": "2215906431", "path": REC, "rank": 3, "title": "Reconciliation"}]
case(
    "resolves-a-gap-in-the-edited-document",
    f"/srd:doc-edit {REC} add the minimum overlap: a reconciliation run needs at "
    "least 30 minutes of overlapping postings from both Ledgers",
    {REC: RECONCILIATION},
    tags=["sec:doc-edit:resolving-a-gap"],
    mocks={**gap_mocks([GAP_0410]),
           "list_docs.md": json.dumps({"docs": docs2}, separators=(",", ":")) + "\n",
           "get_doc.md": get_doc("2215906431", REC, RECONCILIATION)},
    answers=[
        "To a proposal that adds the 30-minute minimum overlap: \"Y\".",
        "Anything else: \"That's all — close the session.\"",
    ],
    graders={
        "b1-open-gaps-before-edit": g_order("mcp__srd__list_gaps", '"status":"open"',
                                            "Edit", '"file_path":"[^"]*reconciliation\\.md"'),
        "b2-fact-written": g_file(REC, r"30\s+minutes"),
        "b3-filled-by-id": g_regex(
            "mock_calls",
            r'^(?=[^\n]*"tool":"[^"]*fill_gap")(?=[^\n]*"gap_id":"gap-0410")'
            r'(?=[^\n]*"filled_by":\["2215906431#[a-z0-9-]+"\])(?=[^\n]*"complete":true)[^\n]*$', "m"),
        "b3-never-by-path": g_never("mcp__srd__fill_gap", "docs/operations"),
        "b3-edit-before-fill": g_order("Edit", '"file_path":"[^"]*reconciliation\\.md"',
                                       "mcp__srd__fill_gap", None),
        "b4-upstream-is-users": g_regex("last_message", r"upstream|\bpush", "i"),
        "b5-front-matter-kept": g_file(
            REC, r"^---\nid: 2215906431\ntitle: Reconciliation\n"
                 r"url: https://wiki\.example\.com/pages/2215906431\n---\n"),
        "b5-no-kb-handoff": g_never("Skill", '"skill":"(srd:)?kb"'),
    },
)

# 3 ------------------------------------------------------------------------
case(
    "hands-an-srd-to-edit",
    "/srd:doc-edit initiatives/autoco/srd.md tighten the wording of AC-2",
    {"initiatives/autoco/srd.md": SRD},
    tags=["skill:edit"],
    max_turns=30,
    graders={
        "b1-invokes-edit": g_used("Skill", '"skill":"(srd:)?edit"', 1),
        "b2-no-edit": g_never("Edit"),
        "b2-no-write": g_never("Write"),
    },
)

print("ok")
