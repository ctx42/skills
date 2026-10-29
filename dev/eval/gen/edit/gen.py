#!/usr/bin/env python3
"""Generate srd/evals/edit--* native cases."""
import os, shutil, textwrap

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../srd/evals"))

PC = open(os.path.join(ROOT, "fixtures/project-config.md")).read()

NOTICE = """> [!INFO]
> The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
> "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
> document are to be interpreted as described in
> [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
> [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
> appear in all capitals, as shown here."""
CONVENTIONS = "## Conventions\n\n" + NOTICE

INTRO = ("This document specifies how the Booking API checks each booking request "
         "a customer sends, and how the system limits slot swaps on a booked "
         "customer mission. It does not cover how launch slots are priced.")

TERMS = [("Booking Request",
          "A customer's request, sent through the Booking API, to book one launch "
          "slot for one payload.")]

INCLUDED = ["Checks on every booking request the Booking API receives.",
            "Limits on slot swaps for a booked customer mission."]
EXCLUDED = ["Pricing of launch slots."]

PB = [("PB-1", "The system MUST reject a booking request that names no launch slot with HTTP status 400."),
      ("PB-2", "The system MUST reject a booking request whose launch slot starts in fewer than 21 days with HTTP status 409."),
      ("PB-3", "The system MUST reject a booking request whose payload mass exceeds the payload limit of the vehicle with HTTP status 422.")]
SW = [("SW-1", "The system MUST refuse a second slot swap for the same customer mission."),
      ("SW-2", "The system MUST refuse a slot swap requested less than 14 days before the booked launch slot.")]
SRD = "initiatives/payload-booking/srd"
SRD_RE = "initiatives/payload-booking/srd"


def wrap(s, w=80, indent=""):
    return "\n".join(textwrap.wrap(s, w, break_on_hyphens=False, subsequent_indent=indent))


def table(rows):
    rows = [("Field", "Value")] + rows
    w0 = max(len(a) for a, _ in rows)
    w1 = max(len(b) for _, b in rows)
    out = []
    for i, (a, b) in enumerate(rows):
        out.append("| " + a.ljust(w0) + " | " + b.ljust(w1) + " |")
        if i == 0:
            out.append("|" + "-" * (w0 + 2) + "|" + "-" * (w1 + 2) + "|")
    return "\n".join(out)


def req(rid, text):
    return wrap(f"- `{rid}` {text}", indent="  ")


def srd(lifecycle="DRAFT", tracking="[SF-151](https://tracker.example.com/browse/SF-151)",
        maintainer="@dana.k", reviewers="@ethan.p, @grace.l", mockups="none", intro=INTRO,
        terms=TERMS, included=INCLUDED, excluded=EXCLUDED, groups=None, tail="",
        title="Payload Booking", notice="std"):
    # notice: "std" = Conventions section after the Introduction (where the
    # eval standard puts it); "none" = absent; "header" = the bare notice
    # directly below the header table, misplaced.
    if groups is None:
        groups = [("Booking Requests", PB), ("Slot Swaps", SW)]
    rows = [("Summary", "Specify how the Booking API checks booking requests."),
            ("Maintainer", maintainer),
            ("Reviewers", reviewers),
            ("Tracking", tracking),
            ("Lifecycle", lifecycle),
            ("Mockups", mockups)]
    p = [f"# {title}", table(rows), "[[TOC]]"] + ([NOTICE] if notice == "header" else [])
    p += ["## Introduction", wrap(intro)] + ([CONVENTIONS] if notice == "std" else [])
    p += ["## Boundaries", "### Included"]
    if included == "TODO":
        p += ["""<!-- Included derives from the requirements. Leave the `--- TODO ---` marker
     below until the requirements settle, then replace it with one line per
     change this SRD delivers. Resolve the marker before the SRD leaves DRAFT. -->""",
              "--- TODO ---"]
    else:
        p.append("\n".join(wrap(f"- {s}", indent="  ") for s in included))
    p.append("### Excluded")
    p.append("\n".join(wrap(f"- {s}", indent="  ") for s in excluded))
    if terms:
        p.append("## Terms")
        for t, d in terms:
            p += [f"### {t}", wrap(d)]
    p.append("## Requirements")
    for name, reqs in groups:
        p.append(f"### {name}")
        items = []
        for item in reqs:
            if isinstance(item, str):  # raw block (comment)
                if items:
                    p.append("\n".join(items))
                    items = []
                p.append(item)
            else:
                items.append(req(*item))
        if items:
            p.append("\n".join(items))
    out = "\n\n".join(p) + "\n"
    if tail:
        out += "\n" + tail.strip("\n") + "\n"
    return out


def review(body, title="Payload Booking"):
    return f"""---
prepared: 2026-09-28 10:00
updated: 2026-09-28 10:00
source: {SRD}.md
---

# SRD Review — {title}

{body.strip()}
"""


def scaffold(files):
    s = ["#!/usr/bin/env bash", "set -euo pipefail", "cat > project-config.md <<'EOF_PC'", PC.rstrip("\n"), "EOF_PC"]
    dirs = sorted({os.path.dirname(f) for f in files if os.path.dirname(f)})
    for d in dirs:
        s.append(f"mkdir -p {d}")
    for i, (path, content) in enumerate(files.items()):
        tag = f"EOF_{i}"
        s += [f"cat > {path} <<'{tag}'", content.rstrip("\n"), tag]
    return "\n".join(s) + "\n"


PERSONA = """Automated eval: the user is absent. Whenever the skill would stop and wait
for the user, take the next scripted answer below as the reply and continue
in this same run; never end the run to wait. If none fits, give the most
plausible answer and continue.
Before taking a scripted answer, write out in full, as your reply text, the
message you would send the user at that point (every proposal with its
location, before/after text and choices), then write the answer you take on a
line of its own as `User: <answer>`, and only then continue. Never apply a
change whose proposal you have not written out this way.

Scripted answers (pick the one that fits the question):
"""


BASE_TAGS = ["skill:edit", "sec:edit:usage", "sec:edit:boundaries", "sec:edit:sources-of-truth",
             "sec:edit:session-start-every-mode", "sec:edit:edit-discipline", "sec:edit:modes",
             "sec:edit:session-end-every-mode", "sec:edit:self-learning",
             "ref:create/project-config", "ref:create/doc-corpus", "ref:create/authoring-guide"]


def g_regex(target, pat, flags=None, match=None):
    fm = ["type: regex"]
    fm.append(f"target: {target}")
    if match:
        fm.append(f"match: {match}")
    if flags:
        fm.append(f'flags: "{flags}"')
    return "---\n" + "\n".join(fm) + "\n---\n" + pat + "\n"


def g_file(path, pat, flags=None, match=None):
    pat = pat.replace(" ", r"\s+")  # tolerate the fixture's hard wrapping
    return g_regex("{source: file, path: %s}" % path, pat, flags, match)


def g_last(pat, flags=None, match=None):
    return g_regex("last_message", pat, flags, match)


def g_trace(pat, flags=None, match=None):
    return g_regex("trace", pat, flags, match)


def g_used(tool, input_match=None, mn=None, mx=None, arm=None):
    fm = ["type: tool_used", f"tool: {tool}"]
    if input_match:
        fm.append(f"input_match: '{input_match}'")
    if mn is not None:
        fm.append(f"min: {mn}")
    if mx is not None:
        fm.append(f"max: {mx}")
    if arm:
        fm.append(f"arm: {arm}")
    return "---\n" + "\n".join(fm) + "\n---\n"


def g_never(tool, input_match=None):
    return g_used(tool, input_match, 0, 0, "both")


def g_order(btool, bmatch, atool, amatch):
    def side(t, m):
        return "{tool: %s%s}" % (t, f", input_match: '{m}'" if m else "")
    return f"---\ntype: tool_order\nbefore: {side(btool, bmatch)}\nafter: {side(atool, amatch)}\n---\n"


def g_exists(path, exists):
    return f"---\ntype: file_exists\npath: {path}\nexists: {'true' if exists else 'false'}\n---\n"


TXT = r'"type":"text","text":"(?:[^"\\]|\\.)*'
SRD_EDIT = '"file_path":"[^"]*initiatives/payload-booking/srd\\.md"'


ENGLISH = "The user writes English; reply in English."


def write_case(name, tags, body, files, graders, answers=None, extra_prompt=None,
               max_turns=60, timeout=300, mocks=None):
    d = os.path.join(ROOT, name)
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, "graders"))
    alltags = [f"case:{name}"] + BASE_TAGS + [t for t in tags if t not in BASE_TAGS]
    fm = [f"tags: [{', '.join(alltags)}]", "runs: 1", f"max_turns: {max_turns}",
          f"timeout_seconds: {timeout}", "allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]"]
    asp = ENGLISH
    if answers:
        asp += "\n" + PERSONA + (extra_prompt + "\n" if extra_prompt else "") + "\n".join(
            f"{i}. {a}" for i, a in enumerate(answers, 1))
    elif extra_prompt:
        asp += "\n" + extra_prompt
    if asp:
        fm.append("append_system_prompt: |")
        for line in asp.splitlines():
            fm.append(("  " + line) if line else "")
    open(os.path.join(d, "prompt.md"), "w").write("---\n" + "\n".join(fm) + "\n---\n\n" + body + "\n")
    open(os.path.join(d, "case.yaml"), "w").write(
        f'schema_version: "1.1"\nname: {name}\ncontext:\n  scaffold_script: scaffold.sh\n')
    sp = os.path.join(d, "scaffold.sh")
    open(sp, "w").write(scaffold(files))
    os.chmod(sp, 0o755)
    for gname, content in graders.items():
        content = content.replace(r'(?:[^\"\\\\]|\\\\.)*', r'(?:[^"\\]|\\.)*')
        open(os.path.join(d, "graders", gname + ".md"), "w").write(content)
    for tool, content in (mocks or {}).items():
        md = os.path.join(d, "mocks", "srd")
        os.makedirs(md, exist_ok=True)
        open(os.path.join(md, tool + ".md"), "w").write(content)


def pair(name, tags, body, files, gate_graders, full_graders, answers, mocks=None, **kw):
    write_case(f"edit--{name}", tags, body, files, full_graders, answers, mocks=mocks, **kw)


DLOG = ["sec:edit:decision-log", "ref:edit/decision-log"]
REVIEW = ["ref:review/review-file"]

# ---------------------------------------------------------------- 1

# ---------------------------------------------------------------- 2

# ---------------------------------------------------------------- 3

# ---------------------------------------------------------------- 4

# ---------------------------------------------------------------- 5

# ---------------------------------------------------------------- 6

# b2/b3 sit at a pause, which scripted runs answer silently: a gate whose
# prompt carries the signal shows the first candidate turn itself.

# ---------------------------------------------------------------- 7

# ---------------------------------------------------------------- 8
s8 = srd(intro=INTRO.replace("checks each booking request", "authorises and checks each booking request"),
         groups=[("Booking Requests", [
             ("PB-1", "The system MUST reject an unauthorised booking request with HTTP status 401."),
             PB[1],
             ("PB-3", "The system MUST reject a booking request whose Mission Manifest can not be parsed with HTTP status 422.")]),
             ("Slot Swaps", [SW[0], ("SW-2", "The system MUST refuse a slot swap requested shortly before the booked launch slot.")])])
r8 = review("""## Errata

- [ ] #4 [minor, linguistic] PB-1 uses British spelling: `unauthorised` →
  `unauthorized`. (SRD:house)

- [ ] #7 [minor, linguistic] PB-3 uses an open form: `can not` → `cannot`.
  (SRD:house)

- [ ] #9 [minor, linguistic] PB-2 misspells a word: `recieves` → `receives`.
  (SRD:house)

---

## Requirements

- [ ] #5 [major, verifiability] SW-2: "shortly before" is vague — state the
  swap deadline. (SRD:RQT-6)""")
AUTOFIX = REVIEW + DLOG + ["ref:edit/autofix", "ref:create/errata"]
pair("autofix-bulk-applies-errata", AUTOFIX, f"/srd:edit {SRD}.md autofix",
     {f"{SRD}.md": s8, f"{SRD}.review.md": r8},
     {
         "b2-no-glossary-call": g_never("mcp__srd__glossary_terms"),
         "b3-lists-all-three": g_last(r"^(?=.*#4)(?=.*#7)(?=.*#9)", "s"),
         "b3-one-batch-confirmation": g_last(r"^[^\n]*\?[^\n]*$", "m", "count:1"),  # one question for the batch
     },
     {
         "b1-unlisted-spelling-kept": g_file(f"{SRD}.md", r"authorises"),
         "b1-non-errata-finding-kept": g_file(f"{SRD}.md", r"shortly\s+before"),
         "b2-no-glossary-call": g_never("mcp__srd__glossary_terms"),
         "b2-no-gate-line": g_trace(r'"type":"text","text":"[^"]{0,200}(approval gate|Lifecycle (is )?`?(DRAFT|IN REVIEW|APPROVED|WITHDRAWN)|(is|it\'s) (approved|frozen|under sign-off|in progress|in-progress|a draft|in draft))', "i", "not_contains"),
         "b4-applied-pb1": g_file(f"{SRD}.md", r"- `PB-1` The system MUST reject an unauthorized booking request"),
         "b4-applied-pb3": g_file(f"{SRD}.md", r"Mission\s+Manifest\s+cannot\s+be\s+parsed"),
         "b4-third-reported-stale": g_last(r"#9.{0,300}(stale|no longer|not found|absent|reworded|zero|0 occurrences|does not (appear|occur|contain)|doesn't|isn't|not in)", "is"),
         "b5-review-not-edited": g_never("Edit", '"file_path":"[^"]*payload-booking/srd\\.review\\.md"'),
         "b5-review-not-written": g_never("Write", '"file_path":"[^"]*payload-booking/srd\\.review\\.md"'),
         "b5-review-not-invoked": g_never("Skill", '"skill":"(srd:)?review'),
         "b5-handoff-command": g_last(rf"review {SRD_RE}\.md check #(4,7|7,4)(?![,\d])"),
         "b6-manifest-names-all": g_last(r"^(?=.*#4)(?=.*#7)(?=.*#9)(?=.*\bcheck\b)", "s"),
         "b6-no-check-outcome": g_last(r"(check|review) (has |have )?(moved|resolved|ticked|closed)|(were|are|have been) (moved|ticked|closed)|now (sit |are )?(in|under) `?## Resolved", "i", "not_contains"),
     },
     ["To the batch confirmation: \"Yes\"."])

# ---------------------------------------------------------------- 9

# ---------------------------------------------------------------- 10

# ---------------------------------------------------------------- 11
s11 = srd(groups=[("Booking Requests", [
    PB[0],
    ("PB-2", "The Booking API retries a failed slot lookup against the Launch Calendar before it rejects the booking request."),
    PB[2]]),
    ("Slot Swaps", SW)])
# The proposal is a pause, which scripted runs answer silently: the gate ends
# there and grades it; the full case grades what follows the user's YN.
CG_TAGS = DLOG + ["ref:edit/modes", "ref:edit/corpus-edits",
                  "skill:report-doc-gap", "skill:kb"]
CG_QUERY = (f"/srd:edit {SRD}.md PB-2 the Booking API retries a failed slot lookup three "
            "times, that is what it does today; make PB-2 say so")
write_case("edit--corpus-grounded-edit-routes-the-unconfirmable--gate", CG_TAGS, CG_QUERY,
           {f"{SRD}.md": s11},
           {
               "b1-search-before-proposal": g_used("mcp__srd__search", None, 1),
               "b1-no-edit-before-key": g_never("Edit", SRD_EDIT),
               "b2-no-gap-question": g_last(r"(gap|backlog|documentation)[^.?!]{0,200}\?", "i", "not_contains"),
               "b3-fact-in-proposal": g_last(r"(three|\b3\b)[\s\S]*(Skip|\*\*S\*\*)"),
               "b4-no-bank-question": g_last(r"(\bbank\b|(add|record|save|write|capture|keep) (this|it|that|these)[^.?!]{0,60}(knowledge base|\bkb\b|inbox))[^.?!]*\?", "i", "not_contains"),
           }, max_turns=30)
write_case("edit--corpus-grounded-edit-routes-the-unconfirmable", CG_TAGS, CG_QUERY,
           {f"{SRD}.md": s11},
           {
               "b1-search-before-edit": g_order("mcp__srd__search", None, "Edit", SRD_EDIT),
               "b1-gap-names-queries": g_used("mcp__srd__report_gap", '"search_terms":\\["', 1),
               "b2-gap-is-draft": g_used("mcp__srd__report_gap", '"draft":true', 1),
               "b5-kb-invoked": g_used("Skill", '"skill":"srd:kb"', 1),
               "b5-gap-skill-invoked": g_used("Skill", '"skill":"srd:report-doc-gap"', 1),
               "b5-fact-in-kb": g_file("kb/_inbox.md", r"(three|\b3\b)[\s\S]{0,80}retr|retr[\s\S]{0,80}(three|\b3\b)", "i"),
           },
           ["To a proposal for PB-2 that states three retries: \"YN\".",
            "To an offer to file or work documentation gaps: \"File it.\"",
            "Anything else: \"That's all — close the session.\""])

# ---------------------------------------------------------------- 12

# ---------------------------------------------------------------- 13

# b1 is a pause after the log write; a stop case ends there, so the log on
# disk and the SW-1 proposal in the last message show the order.

# ---------------------------------------------------------------- 14

# ---------------------------------------------------------------- 15

# ---------------------------------------------------------------- 16

# ---------------------------------------------------------------- 17

# ---------------------------------------------------------------- 18

# ---------------------------------------------------------------- 19
s19 = srd(groups=[("Booking Requests", [
    PB[0],
    ("PB-2", "The system MUST check the launch slot quickly."),
    ("PB-3", "The system must reject a booking request whose payload mass exceeds the payload limit of the vehicle with HTTP status 422.")]),
    ("Slot Swaps", SW)])
write_case("edit--feedback-without-a-review-file", REVIEW + ["ref:edit/modes"], f"/srd:edit {SRD}.md #2",
           {f"{SRD}.md": s19},
           {
               "b1-names-missing-file": g_last(r"srd\.review\.md"),
               "b2-no-findings-invented": g_last(r"quickly|RQT-6|CLR-4|PB-2|PB-3", None, "not_contains"),
               "b3-no-edit": g_never("Edit"),
               "b3-no-write": g_never("Write"),
               "b3-no-decision-log": g_exists(f"{SRD}.decisions.md", False),
               "b4-no-draft-check": g_never("mcp__srd__list_gaps"),
               "b4-no-start-report": g_last(r"Lifecycle|draft|Decision log|manifest", "i", "not_contains"),
               "b4-at-most-two-lines": g_last(r"(?:^(?!.*(?:policy|directive|approval))[^\n]*\S[^\n]*$[\s\S]*?){3}", "m", "not_contains"),
               "b5-no-menu": g_last(r"srd:review|\b(run|use|try)\s+`?/?(srd:)?review\b|paste|drop(ping)?\s+(the|`#)|without\s+(the\s+)?`?#|re-?run", "i", "not_contains"),
           },
           max_turns=20)
# ---------------------------------------------------------------- 20, 21
PB1_UK = ("PB-1", "The system MUST reject an unauthorised booking request with HTTP status 401.")
NOTICE_GROUPS = [("Booking Requests", [PB1_UK, PB[1], PB[2]]), ("Slot Swaps", SW)]
r_notice = review("""## Errata

- [ ] #4 [minor, linguistic] PB-1 uses British spelling: `unauthorised` →
  `unauthorized`. (SRD:house)

- [ ] #10 [minor, structure] Conventions: the section quoting the
  obligation-word notice is missing: `(missing)` →

""" + "\n".join(("  " + l).rstrip() for l in CONVENTIONS.splitlines()) + """

  (SRD:DOC-9)""")
NOTICE_RE = r'The keywords "MUST"'
BELOW_HEADER = r"\[\[TOC\]\]\s*\n(## Conventions|> \[!INFO\]|> The keywords)"
PB1_FIXED = r"- `PB-1` The system MUST reject an unauthorized booking request"
SRD_FILE = "{source: file, path: %s.md}" % SRD

write_case("edit--autofix-inserts-missing-notice", AUTOFIX, f"/srd:edit {SRD}.md autofix",
           {f"{SRD}.md": srd(groups=NOTICE_GROUPS, notice="none"), f"{SRD}.review.md": r_notice},
           {
               "b1-inserted-after-introduction": g_regex(
                   SRD_FILE,
                   r"## Introduction\s*\n[^#]*?\n## Conventions\s*\n+> \[!INFO\]\s*\n> " + NOTICE_RE
                   + r".{0,600}?shown here\.\s*\n## Boundaries", "s"),
               "b1-not-below-header": g_regex(SRD_FILE, BELOW_HEADER, None, "not_contains"),
               "b1-exactly-once": g_regex(SRD_FILE, NOTICE_RE + ".*" + NOTICE_RE, "s", "not_contains"),
               "b2-applied-pb1": g_file(f"{SRD}.md", PB1_FIXED),
               "b3-handoff-command": g_last(rf"review {SRD_RE}\.md check #(4,10|10,4)(?![,\d])"),
           },
           ["To the batch confirmation: \"Yes\"."])

write_case("edit--autofix-misplaced-notice-is-stale", AUTOFIX, f"/srd:edit {SRD}.md autofix",
           {f"{SRD}.md": srd(groups=NOTICE_GROUPS, notice="header"), f"{SRD}.review.md": r_notice},
           {
               "b1-no-second-notice": g_regex(SRD_FILE, NOTICE_RE + ".*" + NOTICE_RE, "s", "not_contains"),
               "b1-no-conventions-added": g_regex(SRD_FILE, r"^## Conventions", "m", "not_contains"),
               "b1-left-in-place": g_regex(SRD_FILE, BELOW_HEADER),
               "b2-reported-stale": g_last(r"#10.{0,300}(stale|already|present|exists|misplaced|not (inserted|applied)|skipp)", "is"),
               "b3-applied-pb1": g_file(f"{SRD}.md", PB1_FIXED),
               "b3-handoff-command": g_last(rf"review {SRD_RE}\.md check #4(?![,\d])"),
           },
           ["To the batch confirmation: \"Yes\"."])

# ---------------------------------------------------------------- 22, 23
s_sum = srd(groups=[("Booking Requests", PB), ("Slot Swaps", SW)])
d_sum = """# Changes — Payload Booking

## 2026-09-30 15:20

### Requirements

SW-2 now refuses a slot swap requested less than 14 days before the booked
launch slot, instead of "shortly before the booked launch slot".
Reason: "a tester can count 14 days."

PB-2 now rejects a booking request whose launch slot starts in fewer than 21
days, instead of 28 days.
Reason: "the build order freezes 21 days out; 28 turned good bookings away."

PB-3 now has the system as its subject: "The system MUST reject …" instead of
"A booking request … MUST be rejected".
Reason: "this makes the system the subject."

## 2026-09-30 09:10

### Requirements

PB-1 now rejects a booking request that names no launch slot, instead of "an
incomplete booking request".
Reason: "names a condition a tester can create."

PB-2 now rejects a booking request only when its launch slot starts in fewer
than 28 days.
Reason: "the factory needs time before the build order freezes."

## 2026-09-29

### Requirements

SW-2 was added: the system refuses a slot swap requested shortly before the
booked launch slot.
Reason: "a swap must not land after the build order freezes."
"""
r_sum = review("""## Requirements

- [ ] #12 [major, verifiability] SW-1: "second slot swap" does not say whether
  a swap that was rolled back counts — state it. (SRD:RQT-5)

---

## Resolved

- [x] #3 [blocker, coverage] Boundaries, Included: no requirement says how late
  a slot swap may be requested — add one. (SRD:BND-2) — added SW-2.

- [x] #5 [blocker, verifiability] PB-1: "incomplete" names no condition a
  tester can create — state it. (SRD:RQT-5) — PB-1 now names a request with no
  launch slot.

- [x] #6 [major, logical] PB-2: a booking accepted after the build order
  freezes cannot be built — state the cutoff. (SRD:consistency) — PB-2 now
  rejects a booking request inside a cutoff.

- [x] #8 [major, verifiability] SW-2: "shortly before" is vague — state the
  swap deadline. (SRD:RQT-6) — SW-2 now refuses a swap less than 14 days out.

- [x] #10 [major, linguistic] PB-3: "MUST be rejected" is passive — rewrite with
  "the system" as subject. (SRD:CLR-1) — PB-3 now has the system as subject.

---

## Withdrawn

- #2 [minor, terminology] Booking Request is defined twice (withdrawn: one
  entry, confirmed by author).

- #4 [major, redundancy] PB-1 and PB-2 overlap (withdrawn 2026-09-30 09:30:
  distinct conditions, confirmed by author).

- #9 [minor, format] SW-1: a trailing space after the word "mission"
  (withdrawn 2026-09-30 15:40: the sync restores it).""")
SUM_FILES = {f"{SRD}.md": s_sum, f"{SRD}.decisions.md": d_sum, f"{SRD}.review.md": r_sum}
SUM_TAGS = DLOG + REVIEW + ["ref:edit/summary"]
NO_MD = r"\*|\x60|^#"

write_case("edit--summary-default-newest-block", SUM_TAGS, f"/srd:edit {SRD}.md summary", SUM_FILES,
           {
               "b1-newest-changes": g_last(r"^(?=[\s\S]*14[ -]day)(?=[\s\S]*21[ -]day)"),
               "b1-no-earlier-block": g_last(r"no launch slot|incomplete", "i", "not_contains"),
               "b2-links-8": g_last(r"14[ -]day[^\n]*\(#8\)"),
               "b2-not-3": g_last(r"#3\b", None, "not_contains"),
               "b3-lists-9": g_last(r"#9\b"),
               "b3-not-4": g_last(r"#4\b", None, "not_contains"),
               "b3-not-2": g_last(r"#2\b", None, "not_contains"),
               "b4-wording-section": g_last(r"^Wording:?\s*$[\s\S]*(PB-3|#10)", "m"),
               "b4-wording-last": g_last(r"(PB-3|#10)[\s\S]*^Wording:?\s*$", "m", "not_contains"),
               "b5-header": g_last(r"^Payload Booking: changes 2026-09-30 15:20\s*$", "m"),
               "b5-no-markdown": g_last(NO_MD, "m", "not_contains"),
               "b6-no-write": g_never("Write"),
               "b6-no-edit": g_never("Edit"),
               "b7-groups": g_last(r"^(?=[\s\S]*^Booking Requests:?\s*$)(?=[\s\S]*^Slot Swaps:?\s*$)", "m"),
               "b8-not-12": g_last(r"#12\b", None, "not_contains"),
           },
           max_turns=20)

write_case("edit--summary-merges-a-day", SUM_TAGS, f"/srd:edit {SRD}.md summary 2026-09-30", SUM_FILES,
           {
               "b1-header": g_last(r"^Payload Booking: changes 2026-09-30\s*$", "m"),
               "b2-both-blocks": g_last(r"^(?=[\s\S]*no launch slot)(?=[\s\S]*14[ -]day)", "i"),
               "b3-pb2-end-state": g_last(r"21[ -]day", None, "count:1"),
               "b3-no-28": g_last(r"28 days|28-day", "i", "not_contains"),
               "b4-lists-4-and-9": g_last(r"^(?=[\s\S]*#4\b)(?=[\s\S]*#9\b)"),
               "b4-not-2": g_last(r"#2\b", None, "not_contains"),
               "b5-not-3": g_last(r"#3\b", None, "not_contains"),
               "b6-no-write": g_never("Write"),
               "b6-no-edit": g_never("Edit"),
           },
           max_turns=20)

print("done")
