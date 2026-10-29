#!/usr/bin/env python3
"""Generate srd/evals/edit--* native cases."""
import os, shutil, textwrap

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../srd/evals"))

PC = open(os.path.join(ROOT, "fixtures/project-config.md")).read()

NOTICE = """> The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
> "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and
> "OPTIONAL" in this document are to be interpreted as described in BCP 14
> [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
> [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
> appear in all capitals, as shown here."""
CONVENTIONS = "## Conventions\n\n" + NOTICE

INTRO = ("This document specifies how the API Gateway checks the Login Token that "
         "accompanies each API request, and how it locks a user account after "
         "repeated failed sign-in attempts. It does not cover how Login Tokens are "
         "issued or refreshed.")

TERMS = [("Login Token",
          "A signed credential that identifies a signed-in user for a limited time.")]

INCLUDED = ["Validation of the Login Token on every API request.",
            "Lockout of a user account after repeated failed sign-in attempts."]
EXCLUDED = ["Issuing and refreshing Login Tokens."]

GW = [("GW-1", "The system MUST reject an API request that carries no Login Token with HTTP status 401."),
      ("GW-2", "The system MUST reject an API request whose Login Token has expired with HTTP status 401."),
      ("GW-3", "The system MUST reject an API request whose Login Token signature is invalid with HTTP status 401.")]
LCK = [("LCK-1", "The system MUST lock a user account after 5 consecutive failed sign-in attempts."),
       ("LCK-2", "The system MUST unlock a locked user account 15 minutes after it was locked.")]


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


def srd(lifecycle="DRAFT", tracking="[WRK-512](https://tickets.example.com/browse/WRK-512)",
        maintainer="@dev.lead", reviewers="@qa.lead, @sec.lead", mockups="none", intro=INTRO,
        terms=TERMS, included=INCLUDED, excluded=EXCLUDED, groups=None, tail="",
        title="Login Token Validation", notice="std"):
    # notice: "std" = Conventions section after the Introduction (where the
    # eval standard puts it); "none" = absent; "header" = the bare notice
    # directly below the header table, misplaced.
    if groups is None:
        groups = [("Gateway Rules", GW), ("Account Lockout", LCK)]
    rows = [("Summary", "Specify how the API Gateway validates Login Tokens."),
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


def review(body, title="Login Token Validation"):
    return f"""---
prepared: 2026-09-28 10:00
updated: 2026-09-28 10:00
source: specs/login.md
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
LOGIN_EDIT = '"file_path":"[^"]*specs/login\\.md"'


def edit_old(snippet):
    return '"file_path":"[^"]*specs/login\\.md","old_string":"[^"]*' + snippet


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
s8 = srd(intro=INTRO.replace("checks the Login Token", "authorises each API request by checking the Login Token"),
         groups=[("Gateway Rules", [
             ("GW-1", "The system MUST reject an unauthorised API request with HTTP status 401."),
             GW[1],
             ("GW-3", "The system MUST reject an API request whose Login Token can not be verified with HTTP status 401.")]),
             ("Account Lockout", [LCK[0], ("LCK-2", "The system MUST unlock a locked user account after a short while.")])])
r8 = review("""## Errata

- [ ] #4 [minor, linguistic] GW-1 uses British spelling: `unauthorised` →
  `unauthorized`. (SRD:house)

- [ ] #7 [minor, linguistic] GW-3 uses an open form: `can not` → `cannot`.
  (SRD:house)

- [ ] #9 [minor, linguistic] GW-2 misspells a word: `recieves` → `receives`.
  (SRD:house)

---

## Requirements

- [ ] #5 [major, verifiability] LCK-2: "after a short while" is vague — state
  the unlock delay. (SRD:RQT-6)""")
AUTOFIX = REVIEW + DLOG + ["ref:edit/autofix", "ref:create/errata"]
pair("autofix-bulk-applies-errata", AUTOFIX, "/srd:edit specs/login.md autofix",
     {"specs/login.md": s8, "specs/login.review.md": r8},
     {
         "b2-no-glossary-call": g_never("mcp__srd__glossary_terms"),
         "b3-lists-all-three": g_last(r"^(?=.*#4)(?=.*#7)(?=.*#9)", "s"),
         "b3-one-batch-confirmation": g_last(r"^[^\n]*\?[^\n]*$", "m", "count:1"),  # one question for the batch
     },
     {
         "b1-unlisted-spelling-kept": g_file("specs/login.md", r"authorises"),
         "b1-non-errata-finding-kept": g_file("specs/login.md", r"a short\s+while"),
         "b2-no-glossary-call": g_never("mcp__srd__glossary_terms"),
         "b2-no-gate-line": g_trace(r'"type":"text","text":"[^"]{0,200}(approval gate|Lifecycle (is )?`?(DRAFT|IN REVIEW|APPROVED|WITHDRAWN)|(is|it\'s) (approved|frozen|under sign-off|in progress|in-progress|a draft|in draft))', "i", "not_contains"),
         "b4-applied-gw1": g_file("specs/login.md", r"- `GW-1` The system MUST reject an unauthorized API request"),
         "b4-applied-gw3": g_file("specs/login.md", r"Login Token\s+cannot\s+be\s+verified"),
         "b4-third-reported-stale": g_last(r"#9.{0,300}(stale|no longer|not found|absent|reworded|zero|0 occurrences|does not (appear|occur|contain)|doesn't|isn't|not in)", "is"),
         "b5-review-not-edited": g_never("Edit", '"file_path":"[^"]*login\\.review\\.md"'),
         "b5-review-not-written": g_never("Write", '"file_path":"[^"]*login\\.review\\.md"'),
         "b5-review-not-invoked": g_never("Skill", '"skill":"(srd:)?review'),
         "b5-handoff-command": g_last(r"review specs/login\.md check #(4,7|7,4)(?![,\d])"),
         "b6-manifest-names-all": g_last(r"^(?=.*#4)(?=.*#7)(?=.*#9)(?=.*\bcheck\b)", "s"),
         "b6-no-check-outcome": g_last(r"(check|review) (has |have )?(moved|resolved|ticked|closed)|(were|are|have been) (moved|ticked|closed)|now (sit |are )?(in|under) `?## Resolved", "i", "not_contains"),
     },
     ["To the batch confirmation: \"Yes\"."])

# ---------------------------------------------------------------- 9

# ---------------------------------------------------------------- 10

# ---------------------------------------------------------------- 11
s11 = srd(groups=[("Gateway Rules", [
    GW[0],
    ("GW-2", "The API Gateway retries a failed token check against the identity service before it rejects the API request."),
    GW[2]]),
    ("Account Lockout", LCK)])
# The proposal is a pause, which scripted runs answer silently: the gate ends
# there and grades it; the full case grades what follows the user's YN.
CG_TAGS = DLOG + ["ref:edit/modes", "ref:edit/corpus-edits",
                  "skill:report-doc-gap", "skill:kb"]
CG_QUERY = ("/srd:edit specs/login.md GW-2 the gateway retries a failed token check three "
            "times, that is what it does today; make GW-2 say so")
write_case("edit--corpus-grounded-edit-routes-the-unconfirmable--gate", CG_TAGS, CG_QUERY,
           {"specs/login.md": s11},
           {
               "b1-search-before-proposal": g_used("mcp__srd__search", None, 1),
               "b1-no-edit-before-key": g_never("Edit", LOGIN_EDIT),
               "b2-no-gap-question": g_last(r"(gap|backlog|documentation)[^.?!]{0,200}\?", "i", "not_contains"),
               "b3-fact-in-proposal": g_last(r"(three|\b3\b)[\s\S]*(Skip|\*\*S\*\*)"),
               "b4-no-bank-question": g_last(r"(\bbank\b|(add|record|save|write|capture|keep) (this|it|that|these)[^.?!]{0,60}(knowledge base|\bkb\b|inbox))[^.?!]*\?", "i", "not_contains"),
           }, max_turns=30)
write_case("edit--corpus-grounded-edit-routes-the-unconfirmable", CG_TAGS, CG_QUERY,
           {"specs/login.md": s11},
           {
               "b1-search-before-edit": g_order("mcp__srd__search", None, "Edit", LOGIN_EDIT),
               "b1-gap-names-queries": g_used("mcp__srd__report_gap", '"search_terms":\\["', 1),
               "b2-gap-is-draft": g_used("mcp__srd__report_gap", '"draft":true', 1),
               "b5-kb-invoked": g_used("Skill", '"skill":"srd:kb"', 1),
               "b5-gap-skill-invoked": g_used("Skill", '"skill":"srd:report-doc-gap"', 1),
               "b5-fact-in-kb": g_file("kb/_inbox.md", r"(three|\b3\b)[\s\S]{0,80}retr|retr[\s\S]{0,80}(three|\b3\b)", "i"),
           },
           ["To a proposal for GW-2 that states three retries: \"YN\".",
            "To an offer to file or work documentation gaps: \"File it.\"",
            "Anything else: \"That's all — close the session.\""])

# ---------------------------------------------------------------- 12

# ---------------------------------------------------------------- 13

# b1 is a pause after the log write; a stop case ends there, so the log on
# disk and the LCK-1 proposal in the last message show the order.

# ---------------------------------------------------------------- 14

# ---------------------------------------------------------------- 15

# ---------------------------------------------------------------- 16

# ---------------------------------------------------------------- 17

# ---------------------------------------------------------------- 18

# ---------------------------------------------------------------- 19
s19 = srd(groups=[("Gateway Rules", [
    GW[0],
    ("GW-2", "The system MUST validate the Login Token quickly."),
    ("GW-3", "The system must reject an API request whose Login Token signature is invalid with HTTP status 401.")]),
    ("Account Lockout", LCK)])
write_case("edit--feedback-without-a-review-file", REVIEW + ["ref:edit/modes"], "/srd:edit specs/login.md #2",
           {"specs/login.md": s19},
           {
               "b1-names-missing-file": g_last(r"login\.review\.md"),
               "b2-no-findings-invented": g_last(r"quickly|RQT-6|CLR-4|GW-2|GW-3", None, "not_contains"),
               "b3-no-edit": g_never("Edit"),
               "b3-no-write": g_never("Write"),
               "b3-no-decision-log": g_exists("specs/login.decisions.md", False),
               "b4-no-draft-check": g_never("mcp__srd__list_gaps"),
               "b4-no-start-report": g_last(r"Lifecycle|draft|Decision log|manifest", "i", "not_contains"),
               "b4-at-most-two-lines": g_last(r"(?:^(?!.*(?:policy|directive|approval))[^\n]*\S[^\n]*$[\s\S]*?){3}", "m", "not_contains"),
               "b5-no-menu": g_last(r"srd:review|\b(run|use|try)\s+`?/?(srd:)?review\b|paste|drop(ping)?\s+(the|`#)|without\s+(the\s+)?`?#|re-?run", "i", "not_contains"),
           },
           max_turns=20)
# ---------------------------------------------------------------- 20, 21
GW1_UK = ("GW-1", "The system MUST reject an unauthorised API request with HTTP status 401.")
NOTICE_GROUPS = [("Gateway Rules", [GW1_UK, GW[1], GW[2]]), ("Account Lockout", LCK)]
r_notice = review("""## Errata

- [ ] #4 [minor, linguistic] GW-1 uses British spelling: `unauthorised` →
  `unauthorized`. (SRD:house)

- [ ] #10 [minor, structure] Conventions: the section quoting the
  obligation-word notice is missing: `(missing)` →

""" + "\n".join(("  " + l).rstrip() for l in CONVENTIONS.splitlines()) + """

  (SRD:DOC-9)""")
NOTICE_RE = r'The key words "MUST"'
BELOW_HEADER = r"\[\[TOC\]\]\s*\n(## Conventions|> The key words)"
GW1_FIXED = r"- `GW-1` The system MUST reject an unauthorized API request"

write_case("edit--autofix-inserts-missing-notice", AUTOFIX, "/srd:edit specs/login.md autofix",
           {"specs/login.md": srd(groups=NOTICE_GROUPS, notice="none"), "specs/login.review.md": r_notice},
           {
               "b1-inserted-after-introduction": g_regex(
                   "{source: file, path: specs/login.md}",
                   r"## Introduction\s*\n[^#]*?\n## Conventions\s*\n+" + NOTICE_RE
                   + r".{0,600}?shown here\.\s*\n## Boundaries", "s"),
               "b1-not-below-header": g_regex("{source: file, path: specs/login.md}", BELOW_HEADER, None,
                                              "not_contains"),
               "b1-exactly-once": g_regex("{source: file, path: specs/login.md}",
                                          NOTICE_RE + ".*" + NOTICE_RE, "s", "not_contains"),
               "b2-applied-gw1": g_file("specs/login.md", GW1_FIXED),
               "b3-handoff-command": g_last(r"review specs/login\.md check #(4,10|10,4)(?![,\d])"),
           },
           ["To the batch confirmation: \"Yes\"."])

write_case("edit--autofix-misplaced-notice-is-stale", AUTOFIX, "/srd:edit specs/login.md autofix",
           {"specs/login.md": srd(groups=NOTICE_GROUPS, notice="header"), "specs/login.review.md": r_notice},
           {
               "b1-no-second-notice": g_regex("{source: file, path: specs/login.md}",
                                              NOTICE_RE + ".*" + NOTICE_RE, "s", "not_contains"),
               "b1-no-conventions-added": g_regex("{source: file, path: specs/login.md}", r"^## Conventions", "m",
                                                  "not_contains"),
               "b1-left-in-place": g_regex("{source: file, path: specs/login.md}", BELOW_HEADER),
               "b2-reported-stale": g_last(r"#10.{0,300}(stale|already|present|exists|misplaced|not (inserted|applied)|skipp)", "is"),
               "b3-applied-gw1": g_file("specs/login.md", GW1_FIXED),
               "b3-handoff-command": g_last(r"review specs/login\.md check #4(?![,\d])"),
           },
           ["To the batch confirmation: \"Yes\"."])

# ---------------------------------------------------------------- 22, 23
s_sum = srd(groups=[("Gateway Rules", [
    GW[0],
    ("GW-2", "The system MUST reject an API request whose Login Token expired more than 30 seconds ago with HTTP status 401."),
    GW[2]]),
    ("Account Lockout", LCK)])
d_sum = """# Changes — Login Token Validation

## 2026-09-30 15:20

### Requirements

LCK-2 now unlocks a locked user account 15 minutes after it was locked,
instead of "after a short while".
Reason: "a tester can wait 15 minutes and check."

GW-2 now rejects a Login Token that expired more than 30 seconds ago, instead
of 60 seconds.
Reason: "security asked for a shorter grace."

GW-3 now has the system as its subject: "The system MUST reject …" instead of
"An API request … MUST be rejected".
Reason: "this makes the system the subject."

## 2026-09-30 09:10

### Requirements

GW-1 now rejects an API request that carries no Login Token, instead of "an
unauthorised API request".
Reason: "names a condition a tester can create."

GW-2 now rejects a Login Token only once it expired more than 60 seconds ago.
Reason: "client clocks drift."

## 2026-09-29

### Requirements

LCK-2 was added: the system unlocks a locked user account after a short while.
Reason: "accounts must not stay locked forever."
"""
r_sum = review("""## Requirements

- [ ] #12 [major, verifiability] LCK-1: "consecutive" does not say whether a
  successful sign-in resets the count — state it. (SRD:RQT-5)

---

## Resolved

- [x] #3 [blocker, coverage] Boundaries, Included: no requirement says when a
  locked account unlocks — add one. (SRD:BND-2) — added LCK-2.

- [x] #5 [blocker, verifiability] GW-1: "unauthorised" names no condition a
  tester can create — state it. (SRD:RQT-5) — GW-1 now names a request with no
  Login Token.

- [x] #6 [major, logical] GW-2: a client whose clock runs behind sees fresh
  Login Tokens rejected — state the tolerance. (SRD:consistency) — GW-2 now
  allows a grace period after expiry.

- [x] #8 [major, verifiability] LCK-2: "after a short while" is vague — state
  the unlock delay. (SRD:RQT-6) — LCK-2 now unlocks after 15 minutes.

- [x] #10 [major, linguistic] GW-3: "MUST be rejected" is passive — rewrite with
  "the system" as subject. (SRD:CLR-1) — GW-3 now has the system as subject.

---

## Withdrawn

- #2 [minor, terminology] Login Token is defined twice (withdrawn: one entry,
  confirmed by author).

- #4 [major, redundancy] GW-1 and GW-2 overlap (withdrawn 2026-09-30 09:30:
  distinct conditions, confirmed by author).

- #9 [minor, format] LCK-1: a trailing space after the word "attempts"
  (withdrawn 2026-09-30 15:40: the sync restores it).""")
SUM_FILES = {"specs/login.md": s_sum, "specs/login.decisions.md": d_sum, "specs/login.review.md": r_sum}
SUM_TAGS = DLOG + REVIEW + ["ref:edit/summary"]
NO_MD = r"\*|\x60|^#"

write_case("edit--summary-default-newest-block", SUM_TAGS, "/srd:edit specs/login.md summary", SUM_FILES,
           {
               "b1-newest-changes": g_last(r"^(?=[\s\S]*15[ -]minute)(?=[\s\S]*30[ -]second)"),
               "b1-no-earlier-block": g_last(r"no Login Token|unauthori[sz]ed", "i", "not_contains"),
               "b2-links-8": g_last(r"15[ -]minute[^\n]*\(#8\)"),
               "b2-not-3": g_last(r"#3\b", None, "not_contains"),
               "b3-lists-9": g_last(r"#9\b"),
               "b3-not-4": g_last(r"#4\b", None, "not_contains"),
               "b3-not-2": g_last(r"#2\b", None, "not_contains"),
               "b4-wording-section": g_last(r"^Wording:?\s*$[\s\S]*(GW-3|#10)", "m"),
               "b4-wording-last": g_last(r"(GW-3|#10)[\s\S]*^Wording:?\s*$", "m", "not_contains"),
               "b5-header": g_last(r"^Login Token Validation: changes 2026-09-30 15:20\s*$", "m"),
               "b5-no-markdown": g_last(NO_MD, "m", "not_contains"),
               "b6-no-write": g_never("Write"),
               "b6-no-edit": g_never("Edit"),
               "b7-groups": g_last(r"^(?=[\s\S]*^Gateway Rules:?\s*$)(?=[\s\S]*^Account Lockout:?\s*$)", "m"),
               "b8-not-12": g_last(r"#12\b", None, "not_contains"),
           },
           max_turns=20)

write_case("edit--summary-merges-a-day", SUM_TAGS, "/srd:edit specs/login.md summary 2026-09-30", SUM_FILES,
           {
               "b1-header": g_last(r"^Login Token Validation: changes 2026-09-30\s*$", "m"),
               "b2-both-blocks": g_last(r"^(?=[\s\S]*no Login Token)(?=[\s\S]*15[ -]minute)", "i"),
               "b3-gr2-end-state": g_last(r"30[ -]second", None, "count:1"),
               "b3-no-60": g_last(r"60 seconds|60-second", "i", "not_contains"),
               "b4-lists-4-and-9": g_last(r"^(?=[\s\S]*#4\b)(?=[\s\S]*#9\b)"),
               "b4-not-2": g_last(r"#2\b", None, "not_contains"),
               "b5-not-3": g_last(r"#3\b", None, "not_contains"),
               "b6-no-write": g_never("Write"),
               "b6-no-edit": g_never("Edit"),
           },
           max_turns=20)

print("done")
