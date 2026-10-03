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

INTRO = ("This document specifies how the API Gateway checks the Login Token that "
         "accompanies each API request, and how it locks a user account after "
         "repeated failed sign-in attempts. It does not cover how Login Tokens are "
         "issued or refreshed.")

GLOSSARY = [("Login Token",
             "A signed credential that identifies a signed-in user for a limited time.")]

INSCOPE = ["Validation of the Login Token on every API request.",
           "Lockout of a user account after repeated failed sign-in attempts."]
OSC = ["Issuing and refreshing Login Tokens."]

GR = [("GR-1", "The system MUST reject an API request that carries no Login Token with HTTP status 401."),
      ("GR-2", "The system MUST reject an API request whose Login Token has expired with HTTP status 401."),
      ("GR-3", "The system MUST reject an API request whose Login Token signature is invalid with HTTP status 401.")]
LCK = [("LCK-1", "The system MUST lock a user account after 5 consecutive failed sign-in attempts."),
       ("LCK-2", "The system MUST unlock a locked user account 15 minutes after it was locked.")]


def wrap(s, w=80):
    return "\n".join(textwrap.wrap(s, w, break_on_hyphens=False))


def table(rows):
    w0 = max(len(a) for a, _ in rows)
    w1 = max(len(b) for _, b in rows)
    out = ["| " + " " * w0 + " | " + " " * w1 + " |",
           "|" + "-" * (w0 + 2) + "|" + "-" * (w1 + 2) + "|"]
    for a, b in rows:
        out.append("| " + a.ljust(w0) + " | " + b.ljust(w1) + " |")
    return "\n".join(out)


def srd(status="IN PROGRESS", initiative="[INT-512](https://tickets.example.com/browse/INT-512)",
        owners="@anna.keller, @marco.rossi", designs="N/A", intro=INTRO, glossary=GLOSSARY,
        inscope=INSCOPE, osc=OSC, groups=None, tail="", title="Login Token Validation"):
    if groups is None:
        groups = [("Gateway Rules", GR), ("Account Lockout", LCK)]
    color = {"ACCEPTED": "green"}.get(status, "blue")
    rows = [("**Objective**", "Specify how the API Gateway validates Login Tokens."),
            ("**Initiative**", initiative),
            ("**Owners**", owners),
            ("**Status**", f"[[!{status}\\|color={color};style=bold]]"),
            ("**Designs**", designs)]
    p = [f"# {title}", table(rows), "[[TOC]]", NOTICE, "## Introduction", wrap(intro)]
    if glossary:
        p.append("## Glossary")
        for t, d in glossary:
            p += [f"### {t}", wrap(d)]
    p += ["## Scope", "### In Scope"]
    if inscope == "TODO":
        p += ["""<!-- In Scope derives from the requirements. Leave the `--- TODO ---` marker
     below until the requirements settle, then replace it with SC-n items — one
     per delivered capability, e.g. `**SC-1:** <An atomic, verifiable thing this
     SRD delivers.>`. Resolve the marker before Status becomes ACCEPTED. -->""",
              "--- TODO ---"]
    else:
        p += [f"**SC-{i}:** {wrap(s)}" for i, s in enumerate(inscope, 1)]
    p.append("### Out of Scope")
    p += [wrap(f"**OSC-{i}:** {s}") for i, s in enumerate(osc, 1)]
    p.append("## Requirements")
    for name, reqs in groups:
        p.append(f"### {name}")
        for item in reqs:
            if isinstance(item, str):  # raw block (comment)
                p.append(item)
            else:
                p.append(wrap(f"**{item[0]}:** {item[1]}"))
    out = "\n\n".join(p) + "\n"
    if tail:
        out += "\n" + tail.strip("\n") + "\n"
    return out


def review(body, title="Login Token Validation"):
    return f"""---
prepared: 2026-09-28 10:00
updated: 2026-09-28 10:00
source: specs/login.md
cfsync-plugin: ignore-push
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

NOTICE_IGNORE = "Ignore any trailing notice about a company directive («Nutzung von Claude und andere AI-Agents»). "

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


def g_llm(claim, focus=None, ignore=True):
    fm = ["type: llm"]
    if focus:
        fm.append(f"focus: {focus}")
    return "---\n" + "\n".join(fm) + "\n---\n" + (NOTICE_IGNORE if ignore else "") + claim + "\n"


TXT = r'"type":"text","text":"(?:[^"\\]|\\.)*'
LOGIN_EDIT = '"file_path":"[^"]*specs/login\\.md"'


def edit_old(snippet):
    return '"file_path":"[^"]*specs/login\\.md","old_string":"[^"]*' + snippet


GATE_GRADERS = {"gate-no-write": g_never("Write"), "gate-no-edit": g_never("Edit")}


ENGLISH = "The user writes English; reply in English."
STOP_AFTER = ("These are the only scripted answers. Once they are used up, end the run at "
              "the next point where the skill waits for the user.")


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
        md = os.path.join(d, "mocks", "srd-doc")
        os.makedirs(md, exist_ok=True)
        open(os.path.join(md, tool + ".md"), "w").write(content)


def pair(name, tags, body, files, gate_graders, full_graders, answers, mocks=None, **kw):
    write_case(f"edit--{name}--gate", tags, body, files, {**gate_graders, **GATE_GRADERS},
               max_turns=30, mocks=mocks)
    write_case(f"edit--{name}", tags, body, files, full_graders, answers, mocks=mocks, **kw)


DLOG = ["sec:edit:decision-log", "ref:edit/decision-log"]
IDS = ["sec:edit:id-rules", "ref:edit/id-rules"]
REVIEW = ["ref:review/review-file"]
GLO = ["ref:create/srd-procedures"]

# ---------------------------------------------------------------- 1
s1 = srd(status="ACCEPTED", groups=[("Gateway Rules", [
    GR[0], GR[1],
    ("GR-3a", "The system SHALL validate the Login Token and log the attempt."),
    ("GR-3b", "The system MUST reject an API request whose Login Token signature is invalid with HTTP status 401.")]),
    ("Account Lockout", LCK)])
pair("interactive-non-atomic-on-approved-srd", IDS + DLOG + GLO, "/srd:edit specs/login.md",
     {"specs/login.md": s1},
     {
         "b1-states-approval-gate": g_last(r"ACCEPTED|approved", "i"),
         "b1-no-question": g_last(r"^(?!.*(?:Weisung|AI-Agents)).*\?", "m", "not_contains"),
         "b1-no-glossary-question": g_last(r"glossar[^.?!\n]*\?", "i", "not_contains"),
         "b2-names-sta4": g_last(r"STA-4"),
         "b2-authority-in-one-confirmation": g_last(r"(\bY\b|Yes)[^\n]{0,160}(authorit|agree)|(authorit|agree)[^\n]{0,160}(\bY\b|Yes)", "i"),
         "b3-grouped-summary-first": g_last(r"(Metadata|Glossary|Scope)[\s\S]*?Requirements[\s\S]*?GR-3a[\s\S]*?Before"),
         "b4-proposal-shape": g_llm("The proposal for GR-3a states its location (the entry id or a line number), the before text, the after text, and a one-line rationale.", "last_message"),
         # Add-only: a new GR-3c, or GR-3a keeps one rule because GR-1/2/3b
         # already state the other; never a renumber.
         "b5-adds-gr3c": g_last(r"GR-3c|already (covered|stated|spelled out)[^\n]{0,40}GR-(1|2|3b)", "i"),
     },
     {
         "b6-no-edit": g_never("Edit"),
         "b6-no-write": g_never("Write"),
         "b6-gr3a-intact": g_file("specs/login.md", r"\*\*GR-3a:\*\* The system SHALL validate the Login Token and log the attempt\.\n\n\*\*GR-3b:\*\*"),
         "b6-no-decision-log": g_exists("specs/login.decisions.md", False),
     },
     ["To the proposal that splits GR-3a: \"S — the approving authority has not agreed.\"",
      "To any later proposal: \"S\".",
      "When the skill asks how to go on or which entry is next: \"That's all — close the session.\""])

# ---------------------------------------------------------------- 2
s2 = srd(groups=[("Gateway Rules", [
    GR[0], GR[1],
    ("GR-3", "The system MUST validate the Login Token signature and log the attempt."),
    ("GR-4", "An API request with a revoked Login Token is rejected by the system with HTTP status 401."),
    ("GR-5", "The system MUST reject an API request whose Login Token was issued for another API Gateway with HTTP status 401. Note: this mirrors the legacy portal.")]),
    ("Account Lockout", LCK)])
r2 = review("""## Requirements

- [ ] #1 [minor, style] GR-4: passive voice ("is rejected by the system") —
  restate with the system as subject. (SRD:LANG-1)

- [ ] #2 [major, extra-text] GR-5: carries a note ("Note: this mirrors the
  legacy portal.") — remove the note. (SRD:REQ-7)

- [ ] #3 [blocker, atomicity] GR-3: states two rules ("validate ... and log
  ...") — split into one rule each. (SRD:REQ-1)""")
pair("apply-a-review-file", REVIEW + IDS + DLOG, "/srd:edit specs/login.md specs/login.review.md",
     {"specs/login.md": s2, "specs/login.review.md": r2},
     {
         "b1-blocker-first": g_llm("The first proposal the reply puts to the user addresses finding #3 (the blocker on GR-3), not finding #1 or #2.", "last_message"),
         "b2-refers-by-number": g_last(r"#3"),
     },
     {
         "b1-blocker-before-major": g_order("Edit", edit_old("and log"), "Edit", edit_old("legacy portal")),
         "b1-major-before-minor": g_order("Edit", edit_old("legacy portal"), "Edit", edit_old("is rejected by")),
         "b2-revalidation-reported": g_trace(LOGIN_EDIT + r"[\s\S]*" + TXT + r"(re-?validat|re-?check|broke nothing|nothing (new|else)|introduced no|no new|final check)", "i"),
         "b3-review-not-edited": g_never("Edit", '"file_path":"[^"]*login\\.review\\.md"'),
         "b3-review-not-written": g_never("Write", '"file_path":"[^"]*login\\.review\\.md"'),
         "b4-points-at-check": g_last(r"review specs/login\.md check"),
         "b4-manifest": g_last(r"^(?=[\s\S]*#1)(?=[\s\S]*#2)(?=[\s\S]*#3)(?=[\s\S]*(left|flagged))", "i"),
     },
     ["To every proposal: \"YN\".",
      "When the skill asks how to go on: \"Next finding.\"",
      "When no findings are left: \"Close the session.\""])

# ---------------------------------------------------------------- 3
s3 = srd(groups=[("Gateway Rules", GR + [("GR-4", "The system MUST respond fast to a token validation request.")]),
                 ("Account Lockout", LCK)])
pair("targeted-edit-by-description", DLOG, '/srd:edit specs/login.md fix the vague "fast" requirement',
     {"specs/login.md": s3},
     {
         "b1-names-gr4": g_last(r"GR-4"),
         "b1-confirms-match": g_llm("The reply identifies GR-4 as the requirement it takes to be the vague \"fast\" one and lets the user confirm or correct that match before anything is edited.", "last_message"),
         "b2-cites-req5-6": g_last(r"REQ-[56]"),
         "b2-placeholder": g_last(r"<[^<>\n]+>"),
         "b2-no-invented-figure": g_llm("The proposed after text for GR-4 states its threshold as a named placeholder, not as a concrete number of milliseconds or seconds.", "last_message"),
     },
     {
         "b2-placeholder-landed": g_file("specs/login.md", r"\*\*GR-4:\*\*[^*]*<[^<>\n]+>"),
         "b3-revalidation-reported": g_llm("The reply reports whether re-validating GR-4 and its cross-references found any new problem.", "last_message"),
     },
     ["To the proposal for GR-4 (including any match confirmation in it): \"Y\".",
      "Anything else: \"That's all — close the session.\""])

# ---------------------------------------------------------------- 4
s4 = srd(initiative="", owners="", designs="",
         intro=INTRO + " A request that is not authorised never reaches a backend service.",
         groups=[("Gateway Rules", [
             GR[0],
             ("GR-2", "The system MUST reject an API request whose Login Token has expired with HTTP status 401, whatever the behaviour of the calling client."),
             ("GR-3", "The system must reject an API request whose Login Token signature is invalid with HTTP status 401."),
             ("GR-4", "The system MUST reject an API request whose Login Token was revoked with HTTP status 401. For example, a token signed with a retired key.")]),
             ("Account Lockout", LCK)])
pair("polish-leaves-metadata-and-meaning", DLOG, "/srd:edit specs/login.md polish",
     {"specs/login.md": s4},
     {
         "b1-one-proposal": g_last(r"^(?![\s\S]*\bBefore\b[\s\S]*\bBefore\b)[\s\S]*\bBefore\b[\s\S]*\bAfter\b"),
         "b1-asks-confirmation": g_last(r"\bYN\b|Yes Next"),
     },
     {
         "b2-meaning-kept": g_file("specs/login.md", r"^(?=.*carries no Login Token with HTTP status\s+401)(?=.*whose Login Token has\s+expired)(?=.*signature is\s+invalid)(?=.*was revoked)(?=.*5 consecutive failed)(?=.*15 minutes after)", "s"),
         "b3-owners-empty": g_file("specs/login.md", r"\*\*Owners\*\*\s*\|\s*\|"),
         "b3-initiative-empty": g_file("specs/login.md", r"\*\*Initiative\*\*\s*\|\s*\|"),
         "b3-designs-empty": g_file("specs/login.md", r"\*\*Designs\*\*\s*\|\s*\|"),
         "b3-status-untouched": g_file("specs/login.md", r"\*\*Status\*\*\s*\|\s*\[\[!IN PROGRESS\\\|color=blue;style=bold\]\]"),
         "b3-flags-metadata": g_last(r"^(?=.*Owners)(?=.*Initiative)(?=.*Designs)", "s"),
         "b4-manifest": g_last(r"^(?=[\s\S]*behavior)(?=[\s\S]*GR-3)(?=[\s\S]*GR-4)"),
     },
     ["To every proposal: \"YN\".",
      "When the skill asks how to go on: \"Next.\"",
      "When nothing is left: \"Close the session.\""])

# ---------------------------------------------------------------- 5
s5 = srd(groups=[("Gateway Rules", [
    GR[0],
    ("GR-2", "The system must reject an API request whose Login Token has expired with HTTP status 401."),
    GR[2],
    ("GR-4", "The system MUST answer a token validation request quickly.")]),
    ("Account Lockout", [LCK[0], ("LCK-2", "The system MUST unlock a locked user account after a while.")])])
pair("terse-output", DLOG + GLO, "/srd:edit specs/login.md",
     {"specs/login.md": s5},
     {
         "b1-proposal-opens-with-change": g_last(r"^---\n(?:\n|[^\n]*\bno (findings|issues)\b[^\n]*\n)*\*\*[A-Z]+-\d+[a-z]?\*\*\s*\((line|`)", "mi"),  # first proposal opens on its location
     },
     {
         "b2-names-each-edit": g_last(r"^(?=[\s\S]*GR-2)(?=[\s\S]*GR-4)(?=[\s\S]*LCK-2)"),
         "b2-no-diff-reprint": g_last(r"^[\s>*_-]*(Before|After)\b|```", "mi", "not_contains"),
         "b3-names-decision-log": g_last(r"specs/login\.decisions\.md"),
         "b3-not-md-md": g_last(r"login\.md\.decisions", None, "not_contains"),
         "b3-log-not-reprinted": g_last(r"cfsync-plugin|^## \d{4}-\d\d-\d\d\s*\n+###", "m", "not_contains"),
     },
     ["To every proposal: \"YN\".",
      "When the skill asks how to go on: \"Next entry.\"",
      "When nothing is left: \"Close the session.\""])

# ---------------------------------------------------------------- 6
s6 = srd(inscope="TODO", groups=[
    ("Token Validation", [("TV-1", "The system MUST reject an API request whose Login Token signature is invalid with HTTP status 401."),
                          ("TV-2", "The system MUST reject an API request that carries no Login Token with HTTP status 401.")]),
    ("Token Expiry", [("TE-1", "The system MUST reject an API request whose Login Token has expired with HTTP status 401."),
                      ("TE-2", "The system MUST treat a Login Token as expired 60 minutes after it was issued.")]),
    ("Account Lockout", LCK)])
pair("generate-in-scope-on-signal", DLOG + ["sec:edit:draft-scaffolds", "ref:edit/draft-scaffolds", "ref:create/srd-procedures"],
     "/srd:edit specs/login.md",
     {"specs/login.md": s6},
     {
         "b1-no-sco2-before-signal": g_llm("The reply raises no SCO-2 finding (an In Scope item or requirement lacking coverage) against the In Scope `--- TODO ---` marker; saying the SCO-2 check is on hold while the marker stands is fine.", "last_message"),
         "b1-no-scope-items-before-signal": g_last(r"\bSC-\d", None, "not_contains"),
     },
     {
         "b4-marker-gone": g_file("specs/login.md", r"--- TODO ---", None, "not_contains"),
         "b4-merged-item": g_file("specs/login.md", r"\*\*SC-\d:\*\*\s+Validation of the Login Token signature\s+and\s+expiry on every API\s+request\."),
         "b4-reworded-item": g_file("specs/login.md", r"\*\*SC-\d:\*\*\s+Lockout of a user account after repeated\s+failed\s+sign-in\s+attempts\."),
         "b4-two-items-no-gap": g_file("specs/login.md", r"^(?=[\s\S]*\*\*SC-1:\*\*)(?=[\s\S]*\*\*SC-2:\*\*)(?![\s\S]*\*\*SC-3:\*\*)"),
         "b4-coverage-rechecked": g_trace(r'"old_string":"[^"]*--- TODO ---[\s\S]*' + TXT + r"SCO-[23]"),
     },
     ["The first time the skill stops for an answer, whatever it asked: \"The requirements are final now — please fill In Scope.\"",
      "To the candidate about token validation (signature or missing token): \"Merge it with the token expiry candidate into one item: Validation of the Login Token signature and expiry on every API request.\"",
      "To the candidate about token expiry, if asked about it on its own: \"Merge it with the token validation candidate, as I said.\"",
      "To the candidate about account lockout: \"E — reword it to: Lockout of a user account after repeated failed sign-in attempts.\"",
      "To any other proposal or candidate: \"Y\".",
      "When the skill asks how to go on and In Scope is filled: \"Close the session.\""])

# b2/b3 sit at a pause, which scripted runs answer silently: a gate whose
# prompt carries the signal shows the first candidate turn itself.
write_case("edit--generate-in-scope-on-signal--gate-signal",
           DLOG + ["sec:edit:draft-scaffolds", "ref:edit/draft-scaffolds", "ref:create/srd-procedures"],
           "/srd:edit specs/login.md — the requirements are final now, please fill In Scope.",
           {"specs/login.md": s6},
           {
               # A candidate labelled SC-n (bold label, or a list/heading line
               # opening with one); explaining the later numbering is fine.
               "b2-candidates-unnumbered": g_last(r"\*\*SC-\d:\*\*|^[ \t#*]*(?:\d+\.\s*)?\**SC-\d\b", "m", "not_contains"),
               "b3-first-candidate": g_last(r"[Cc]andidate"),
               "b3-one-at-a-time": g_last(r"[Cc]andidate\s*(2|two)\b|[Cc]andidates\s*(2|two)\b", None, "not_contains"),
               **GATE_GRADERS,
           })

# ---------------------------------------------------------------- 7
todo7 = """## TODO

1. Confirm the HTTP status for a revoked Login Token with the API team.

2. Decide whether lockout applies to service accounts."""
s7 = srd(tail=todo7)
write_case("edit--add-to-todo-on-demand", DLOG + ["sec:edit:draft-scaffolds", "ref:edit/draft-scaffolds"],
           "Add: confirm the lockout threshold with security to TODO — then close the session",
           {"specs/login.md": s7},
           {
               "b1-appended-as-item-3": g_file("specs/login.md", r"^2\. Decide whether lockout applies to service accounts\.\n\n?3\. [^\n]*lockout threshold[^\n]*security", "im"),
               "b1-items-above-unchanged": g_file("specs/login.md", r"^## TODO\n\n1\. Confirm the HTTP status for a revoked Login Token with the API team\.\n", "m"),
               # Runs have Bash: an append (`>>`) writes the item as well as Edit.
               "b2-applied-without-asking": g_trace(
                   r'"name":"(?:Edit|Write)","input":\{[^}]*"file_path":"[^"]*specs/login\.md"'
                   r'|"command":"(?:[^"\\]|\\.)*(?:>>?|sed -i)\s*\S*login\.md'),
               "b3-reports-one-line": g_last(r"revoked Login Token|service accounts", "i", "not_contains"),
               "b4-todo-blocks-accepted": g_last(r"^(?=.*TODO)(?=.*ACCEPTED)", "s"),
           },
           extra_prompt="""Session so far: the user ran `/srd:edit specs/login.md`. The srd:edit skill
front-loaded its issue summary and the user skipped (`S`) its one proposal,
on GR-2. The edit session on specs/login.md is still running: load the
srd:edit skill with the Skill tool and continue it with the user's next
message, which follows.""")

# ---------------------------------------------------------------- 8
s8 = srd(intro=INTRO.replace("checks the Login Token", "authorises each API request by checking the Login Token"),
         groups=[("Gateway Rules", [
             ("GR-1", "The system MUST reject an unauthorised API request with HTTP status 401."),
             GR[1],
             ("GR-3", "The system MUST reject an API request whose Login Token can not be verified with HTTP status 401.")]),
             ("Account Lockout", [LCK[0], ("LCK-2", "The system MUST unlock a locked user account after a short while.")])])
r8 = review("""## Errata

- [ ] #4 [minor, linguistic] GR-1 uses British spelling: `unauthorised` →
  `unauthorized`. (SRD:house)

- [ ] #7 [minor, linguistic] GR-3 uses an open form: `can not` → `cannot`.
  (SRD:LANG-2)

- [ ] #9 [minor, linguistic] GR-2 misspells a word: `recieves` → `receives`.
  (SRD:LANG-2)

---

## Requirements

- [ ] #5 [major, verifiability] LCK-2: "after a short while" is vague — state
  the unlock delay. (SRD:REQ-6)""")
AUTOFIX = REVIEW + DLOG + ["ref:edit/autofix", "ref:create/errata"]
pair("autofix-bulk-applies-errata", AUTOFIX, "/srd:edit specs/login.md autofix",
     {"specs/login.md": s8, "specs/login.review.md": r8},
     {
         "b2-no-glossary-call": g_never("mcp__srd-doc__glossary_terms"),
         "b3-lists-all-three": g_last(r"^(?=.*#4)(?=.*#7)(?=.*#9)", "s"),
         "b3-one-batch-confirmation": g_last(r"^[^\n]*\?[^\n]*$", "m", "count:1"),  # one question for the batch
     },
     {
         "b1-unlisted-spelling-kept": g_file("specs/login.md", r"authorises"),
         "b1-non-errata-finding-kept": g_file("specs/login.md", r"a short\s+while"),
         "b2-no-glossary-call": g_never("mcp__srd-doc__glossary_terms"),
         "b2-no-gate-line": g_trace(r'"type":"text","text":"[^"]{0,200}(approval gate|Status (is )?`?(ACCEPTED|IN PROGRESS)|(is|it\'s) (approved|in progress|in-progress))', "i", "not_contains"),
         "b4-applied-gr1": g_file("specs/login.md", r"\*\*GR-1:\*\* The system MUST reject an unauthorized API request"),
         "b4-applied-gr3": g_file("specs/login.md", r"Login Token\s+cannot\s+be\s+verified"),
         "b4-third-reported-stale": g_last(r"#9.{0,300}(stale|no longer|not found|absent|reworded|zero|0 occurrences|does not (appear|occur|contain)|doesn't|isn't|not in)", "is"),
         "b5-review-not-edited": g_never("Edit", '"file_path":"[^"]*login\\.review\\.md"'),
         "b5-review-not-written": g_never("Write", '"file_path":"[^"]*login\\.review\\.md"'),
         "b5-review-not-invoked": g_never("Skill", '"skill":"(srd:)?review'),
         "b5-handoff-command": g_last(r"review specs/login\.md check (#4 #7|#7 #4)(?! #)"),
         "b6-manifest-names-all": g_last(r"^(?=.*#4)(?=.*#7)(?=.*#9)(?=.*\bcheck\b)", "s"),
         "b6-no-check-outcome": g_last(r"(check|review) (has |have )?(moved|resolved|ticked|closed)|(were|are|have been) (moved|ticked|closed)|now (sit |are )?(in|under) `?## Resolved", "i", "not_contains"),
     },
     ["To the batch confirmation: \"Yes\"."])

# ---------------------------------------------------------------- 9
AUD_FIELDS = ["the user identifier", "the time in UTC", "the source IP address", "the user agent string",
              "the result code", "the Login Token identifier", "the request path", "the HTTP method",
              "the response status", "the client application identifier", "the API Gateway node name",
              "the request identifier", "the tenant identifier", "the session identifier",
              "the failure reason", "the token issuer", "the token audience", "the token expiry time",
              "the signing key identifier", "the request size in bytes", "the response time in milliseconds",
              "the TLS protocol version", "the client certificate fingerprint", "the geographic region of the source IP address",
              "the number of the attempt within the current lockout window", "the API version requested",
              "the identity provider name", "the authentication method", "the correlation identifier",
              "the forwarding proxy address", "the account lock state", "the count of prior failures",
              "the time the Login Token was issued", "the scope list of the Login Token", "the device identifier",
              "the operating system name", "the locale of the request", "the referring host", "the retry counter",
              "the audit schema version", "the build number of the API Gateway", "the data center name",
              "the network zone of the source", "the rate limit bucket", "the consent version", "the password age in days",
              "the multi-factor method used", "the time zone of the user", "the queue latency", "the cache hit flag",
              "the replica identifier", "the region of the identity service"]


def s9_build(n):
    aud = []
    for i in range(n):
        f = AUD_FIELDS[i]
        txt = f"The system MUST include {f} in the Audit Record of each sign-in attempt."
        if i == 2:
            txt = f"The system MUST include {f} in the Audit Record of each authorisation attempt."
        aud.append((f"AUD-{i+1}", txt))
    gr = [GR[0], GR[1], GR[2],
          ("GR-4a", "The system MUST check the Login Token signature against the current signing key of the identity service."),
          ("GR-4b", "The system MUST fetch a new signing key from the identity service promptly whenever the identity service publishes one, so that a Login Token signed with the new key is accepted by the API Gateway from the moment it is first presented by any client application on any API Gateway node."),
          ("GR-5", "The system must reject an API request whose Login Token was revoked with HTTP status 401.")]
    lck = [LCK[0], ("LCK-2", "The system MUST unlock a locked user account after a reasonable time.")]
    glossary = GLOSSARY + [("Audit Record", "A stored entry that describes one sign-in attempt for later inspection.")]
    return srd(glossary=glossary, inscope=INSCOPE + ["An Audit Record for every sign-in attempt."],
               groups=[("Audit", aud), ("Gateway Rules", gr), ("Account Lockout", lck)])


for n in range(10, len(AUD_FIELDS) + 1):
    t9 = s9_build(n)
    lines = t9.split("\n")
    start = next(i for i, l in enumerate(lines, 1) if l.startswith("**GR-4b:**"))
    end = next(i for i, l in enumerate(lines, 1) if l.startswith("**GR-5:**")) - 2
    if start + 1 <= 210 <= end:
        break
else:
    raise SystemExit("could not place line 210 in GR-4b")
print("case 9: GR-4b spans lines", start, "-", end)
pair("interactive-from-a-line-number", DLOG + GLO, "/srd:edit specs/login.md 210",
     {"specs/login.md": t9},
     {
         "b1-starts-at-gr4b": g_last(r"GR-4b"),
         "b1-no-whole-summary": g_last(r"authoris|AUD-\d", "i", "not_contains"),
     },
     {
         "b2-gr4b-before-gr5": g_order("Edit", edit_old("promptly"), "Edit", edit_old("must reject")),
         "b2-gr5-before-lck2": g_order("Edit", edit_old("must reject"), "Edit", edit_old("reasonable")),
         "b2-nothing-before-210-edited": g_never("Edit", edit_old("authoris")),
         "b3-closing-pass-whole-document": g_last(r"authoris", "i"),
     },
     ["To every proposal: \"YN\".",
      "When the skill asks how to go on: \"Next entry.\"",
      "When nothing is left: \"Close the session.\""])

# ---------------------------------------------------------------- 10
s10 = srd(groups=[("Gateway Rules", [
    ("GR-1", "The system MUST reject an unauthorised API request with HTTP status 401."),
    ("GR-2", "The system MUST validate the Login Token quickly."),
    ("GR-3", "The system must reject an API request whose Login Token has expired with HTTP status 401."),
    ("GR-4", "The system MUST reject an API request whose Login Token signature is invalid with HTTP status 401. Note: this mirrors the legacy portal."),
    ("GR-5", "An API request with a revoked Login Token is rejected by the system with HTTP status 401."),
    ("GR-6", "The system MUST log each failed token check, including but not limited to expired and invalid Login Tokens.")]),
    ("Account Lockout", LCK)])
r10 = review("""## Requirements

- [ ] #1 [minor, linguistic] GR-1 uses British spelling ("unauthorised") —
  use US English. (SRD:house)

- [ ] #2 [major, verifiability] GR-2: "quickly" is vague — state a measurable
  limit. (SRD:REQ-6)

- [ ] #3 [minor, style] GR-3: the keyword "must" is lowercase — capitalize it.
  (SRD:LANG-4)

- [ ] #4 [major, extra-text] GR-4: carries a note ("Note: this mirrors the
  legacy portal.") — remove the note. (SRD:REQ-7)

- [ ] #5 [minor, style] GR-5: passive voice ("is rejected by the system") —
  restate with the system as subject. (SRD:LANG-1)

- [ ] #6 [major, completeness] GR-6: "including but not limited to" leaves the
  list open — close the list. (SRD:LANG-7)""")
pair("feedback-from-a-finding-number", REVIEW + DLOG, "/srd:edit specs/login.md #2",
     {"specs/login.md": s10, "specs/login.review.md": r10},
     {
         "b1-enters-at-2": g_last(r"^(?![\s\S]*unauthori)[\s\S]*#2[\s\S]*\*\*GR-2:\*\*[^\n]*quickly"),
     },
     {
         "b3-2-before-6": g_order("Edit", edit_old("quickly"), "Edit", edit_old("not limited")),
         "b3-6-before-1": g_order("Edit", edit_old("not limited"), "Edit", edit_old("unauthorised")),
         "b3-1-before-3": g_order("Edit", edit_old("unauthorised"), "Edit", edit_old("must reject")),
         "b2-3-before-4": g_order("Edit", edit_old("must reject"), "Edit", edit_old("legacy portal")),
         "b2-4-before-5": g_order("Edit", edit_old("legacy portal"), "Edit", edit_old("is rejected by")),
         "b4-review-not-edited": g_never("Edit", '"file_path":"[^"]*login\\.review\\.md"'),
         "b4-review-not-written": g_never("Write", '"file_path":"[^"]*login\\.review\\.md"'),
         "b4-points-at-check": g_last(r"review specs/login\.md check"),
     },
     ["To the proposal for finding #2: \"YN\".",
      "To the proposal that comes right after finding #2: \"Not yet — do #6 next.\"",
      "To every other proposal: \"YN\".",
      "When the skill asks how to go on: \"Next finding.\"",
      "When no findings are left: \"Close the session.\""])

# ---------------------------------------------------------------- 11
s11 = srd(groups=[("Gateway Rules", [
    GR[0],
    ("GR-2", "The API Gateway retries a failed token check against the identity service before it rejects the API request."),
    GR[2]]),
    ("Account Lockout", LCK)])
write_case("edit--corpus-grounded-edit-routes-the-unconfirmable",
           DLOG + ["sec:edit:documentation-corpus", "ref:edit/corpus-edits", "skill:report-doc-gap", "skill:kb"],
           "/srd:edit specs/login.md GR-2",
           {"specs/login.md": s11},
           {
               "b1-search-before-edit": g_order("mcp__srd-doc__search", None, "Edit", LOGIN_EDIT),
               "b1-gap-names-queries": g_used("mcp__srd-doc__report_gap", '"search_terms":\\["', 1),
               "b2-gap-is-draft": g_used("mcp__srd-doc__report_gap", '"draft":true', 1),
               "b2-no-interruption": g_trace(r"User: \\?\"?The gateway retries(?:(?!User: )[\s\S])*?(gap|backlog|documentation)[^\"]{0,300}\?(?:(?!User: )[\s\S])*?User: \\?\"?YN", None, "not_contains"),
               "b3-fact-in-proposal": g_trace(TXT + r"(three|\b3\b)(?:[^\"\\\\]|\\\\.)*(Skip|\*\*S\*\*)[\s\S]*" + edit_old("retr")),
               "b4-no-bank-question": g_trace(r"\{\"type\":\"assistant\"[^\n]*\"type\":\"text\",\"text\":\"[^\n]*(\bbank\b|(add|record|save|write|capture|keep) (this|it|that|these)[^.?!\\]{0,60}(knowledge base|\bkb\b|inbox))[^.?!\\]*\?", "i", "not_contains"),
               "b5-kb-invoked": g_used("Skill", '"skill":"srd:kb"', 1),
               "b5-gap-skill-invoked": g_used("Skill", '"skill":"srd:report-doc-gap"', 1),
               "b5-fact-in-kb": g_file("kb/_inbox.md", r"(three|\b3\b)[\s\S]{0,80}retr|retr[\s\S]{0,80}(three|\b3\b)", "i"),
           },
           ["If the skill asks what to change in GR-2, or proposes GR-2 with a placeholder for the retry count: \"The gateway retries a failed token check three times — that is what it does today. Make GR-2 say so.\"",
            "To a proposal for GR-2 that states three retries: \"YN\".",
            "To an offer to file or work documentation gaps: \"File it.\"",
            "Anything else: \"That's all — close the session.\""])

# ---------------------------------------------------------------- 12
s12 = srd(groups=[("Gateway Rules", GR + [("GR-4", "The system MUST answer a token validation request quickly.")]),
                  ("Account Lockout", LCK)])
gaps12 = ('{"gaps":[{"id":"gap-0311","status":"draft","kind":"missing","topic":"Token check retry count at the API Gateway",'
          '"doc_id":"","heading_path":null,"source_url":"","demand":"GR-2 needs the retry count","target_claim":"The API Gateway retries a failed token check a fixed number of times.",'
          '"detail":"No document states how often the gateway retries a failed token check.","search_terms":["token check retry"],"srd_ref":"specs/login.md"},'
          '{"id":"gap-0312","status":"draft","kind":"missing","topic":"Default lockout duration for user accounts",'
          '"doc_id":"","heading_path":null,"source_url":"","demand":"LCK-2 needs the lockout duration","target_claim":"A locked user account unlocks after a fixed duration.",'
          '"detail":"No document states the default lockout duration.","search_terms":["lockout duration"],"srd_ref":"specs/login.md"}]}\n')
pair("session-start-drains-prior-drafts", DLOG + GLO + ["skill:report-doc-gap"], "/srd:edit specs/login.md",
     {"specs/login.md": s12},
     {
         "b1-draft-check-before-delegate": g_order("mcp__srd-doc__list_gaps", None, "Skill", '"skill":"srd:report-doc-gap"'),
         "b1-names-both-topics": g_last(r"^(?=.*retr)(?=.*(lockout duration|stays locked|locked by default|lock(out)? (period|time)|how long[^\n]{0,60}lock))", "is"),
         "b1-count": g_last(r"\b(two|2)\b", "i"),
         "b2-offers-to-work-them": g_last(r"(work|handle|go through|file)[^?\n]{0,80}\bnow\b[^\n]*\?", "i"),
     },
     {
         "b3-drafts-not-discarded": g_never("mcp__srd-doc__discard_gap"),
         "b3-drafts-not-submitted": g_never("mcp__srd-doc__submit_gap"),
         "b3-drafts-not-updated": g_never("mcp__srd-doc__update_gap"),
         "b3-proceeds-to-interactive": g_trace(r'"skill":"srd:report-doc-gap"[\s\S]*' + TXT + r"GR-4(?:[^\"\\\\]|\\\\.)*(Skip|\*\*S\*\*)"),
     },
     ["To the offer to work the draft gaps now: \"Not now — get on with the edit.\"",
      "To every edit proposal: \"S\".",
      "When the skill asks how to go on: \"Close the session.\""],
     mocks={"list_gaps": gaps12})

# ---------------------------------------------------------------- 13
s13 = srd(osc=OSC + ["Retention of token validation logs."],
          groups=[("Gateway Rules", GR + [("GR-4", "The system MUST retain each token validation log entry for 90 days.")]),
                  ("Account Lockout", [("LCK-1", "The system must lock a user account after 5 consecutive failed sign-in attempts."), LCK[1]])])
write_case("edit--decision-log-written-per-edit", DLOG + GLO + IDS, "/srd:edit specs/login.md",
           {"specs/login.md": s13},
           {
               "b2-frontmatter": g_file("specs/login.decisions.md", r"^---\n+cfsync-plugin:\s*ignore-push\s*\n+---"),
               "b3-reason-verbatim": g_file("specs/login.decisions.md", r"retention isn't ours, drop it"),
               "b3-not-a-diff": g_file("specs/login.decisions.md", r"^(\+|```|@@)", "m", "not_contains"),
               "b4-skip-not-logged": g_file("specs/login.decisions.md", r"LCK-1|\bmust\b.{0,40}MUST", "s", "not_contains"),
               "b5-manifest-points-at-block": g_last(r"login\.decisions\.md[\s\S]{0,300}##\s*\d{4}-\d\d-\d\d"),
           },
           ["To the first proposal: \"Y — retention isn't ours, drop it\".",
            "When the skill says the entry has nothing further or asks how to go on, the first time: \"Next entry.\"",
            "To the next proposal: \"S\".",
            "After that, whenever the skill asks how to go on or proposes anything: \"That's all — close the session.\""])

# b1 is a pause after the log write; a stop case ends there, so the log on
# disk and the LCK-1 proposal in the last message show the order.
write_case("edit--decision-log-written-per-edit--stop", DLOG + GLO + IDS, "/srd:edit specs/login.md",
           {"specs/login.md": s13},
           {
               "b1-logged": g_file("specs/login.decisions.md", r"retention isn't ours, drop it"),
               "b1-next-proposal-shown": g_last(r"LCK-1"),
               "b1-no-second-edit": g_never("Edit", r'"old_string":"[^"]*must lock'),
           },
           ["To the first proposal: \"Y — retention isn't ours, drop it\".",
            "When the skill says the entry has nothing further or asks how to go on: \"Next entry.\""],
           extra_prompt=STOP_AFTER)

# ---------------------------------------------------------------- 14
s14 = srd(status="ACCEPTED", groups=[("Gateway Rules", GR + [
    ("GR-4", "The system MUST reject an API request whose Login Token was revoked with HTTP status 401."),
    ("GR-5", "The system MUST reject an API request whose Login Token was issued for another API Gateway with HTTP status 401."),
    ("GR-6", "The system MUST answer an API request that carries an expired Login Token with HTTP status 401."),
    ("GR-7", "The system MUST log each rejected API request with its HTTP status."),
    ("GR-8", "The system MUST NOT log the Login Token itself.")]),
    ("Account Lockout", LCK)])
r14 = review("""## Requirements

- [ ] #3 [major, redundancy] GR-6 states the same rule as GR-2 (an expired
  Login Token gets HTTP status 401) — remove GR-6. (SRD:consistency)""")
write_case("edit--removal-on-an-approved-srd", REVIEW + IDS + DLOG, "/srd:edit specs/login.md specs/login.review.md",
           {"specs/login.md": s14, "specs/login.review.md": r14},
           {
               "b1-struck-not-deleted": g_file("specs/login.md", r"\*\*GR-6:\*\*\s*~~[^~]*expired\s+Login\s+Token[^~]*~~"),
               "b2-gr7-unchanged": g_file("specs/login.md", r"\*\*GR-7:\*\* The system MUST log each rejected API request with its HTTP\s+status\."),
               "b2-gr8-unchanged": g_file("specs/login.md", r"\*\*GR-8:\*\* The system MUST NOT log the Login Token itself\."),
               "b3-logged": g_file("specs/login.decisions.md", r"GR-6"),
           },
           ["To the proposal on finding #3 (removing GR-6), including any question about the approving authority: \"Y — the approving authority has agreed to the removal.\"",
            "To any other proposal: \"S\".",
            "When the skill asks how to go on: \"That's all — close the session.\""])

# ---------------------------------------------------------------- 15
s15 = srd(initiative="INT-512", groups=[("Gateway Rules", [
    ("GR-1", "The system MUST reject an unauthorised API request with HTTP status 401."),
    ("GR-2", "The system MUST validate the Login Token quickly."),
    ("GR-3", "The system must reject an API request whose Login Token has expired with HTTP status 401.")]),
    ("Account Lockout", LCK)])
r15 = review("""## Metadata

- [ ] #2 [major, metadata] Initiative: names INT-512 but does not link to the
  initiative in the ticketing system — add the link. (SRD:STR-3)

## Requirements

- [ ] #1 [minor, linguistic] GR-1 uses British spelling ("unauthorised") —
  use US English. (SRD:house)

- [ ] #3 [major, verifiability] GR-2: "quickly" is vague — state a measurable
  limit. (SRD:REQ-6)

- [ ] #4 [minor, style] GR-3: the keyword "must" is lowercase — capitalize it.
  (SRD:LANG-4)""")
pair("finding-outside-the-mandate", REVIEW + DLOG, "/srd:edit specs/login.md #2",
     {"specs/login.md": s15, "specs/login.review.md": r15},
     {
         "b1-says-outside-mandate": g_llm("The reply says finding #2 (the Initiative link) is outside what this edit run may fix, and does not propose an edit for it (no Before/After and no Yes/Skip choice for #2; telling the user what to change by hand is not a proposal).", "last_message"),
         "b2-authors-to-fix": g_last(r"author|owner|yours to|you(?:'ll| will)? (need to|have to|must|can|should) (add|fix|link|set)|by hand|manually|yourself", "i"),
         "b2-advances-to-3": g_last(r"#3[^\n]{0,200}GR-2[\s\S]*quickly[\s\S]*<[^<>]{1,120}>"),  # a placeholder may wrap
     },
     {
         "b1-initiative-unchanged": g_file("specs/login.md", r"\*\*Initiative\*\*\s*\|\s*INT-512\s*\|"),
         "b3-review-not-edited": g_never("Edit", '"file_path":"[^"]*login\\.review\\.md"'),
         "b3-review-not-written": g_never("Write", '"file_path":"[^"]*login\\.review\\.md"'),
         "b4-manifest-flags-2": g_llm("The closing manifest lists finding #2 (the missing Initiative link) as flagged and left for the author.", "last_message"),
     },
     ["To every proposal: \"YN\".",
      "When the skill asks how to go on: \"Next finding.\"",
      "When no findings are left: \"Close the session.\""])

# ---------------------------------------------------------------- 16
s16 = srd(groups=[("Gateway Rules", [
    ("GR-1", "The system MUST reject an unauthorised API request with HTTP status 401."),
    GR[1],
    ("GR-3", "The system MUST reject an API request whose Login Token can not be verified with HTTP status 401."),
    ("GR-4", "The system MUST show the lockout banner in the warning colour and its countdown in the neutral colour.")]),
    ("Account Lockout", LCK)])
r16 = review("""## Errata

- [ ] #4 [minor, linguistic] GR-1 uses British spelling: `unauthorised` →
  `unauthorized`. (SRD:house)

- [ ] #7 [minor, linguistic] GR-3 uses an open form: `can not` → `cannot`.
  (SRD:LANG-2)

- [ ] #9 [minor, linguistic] GR-4 uses British spelling: `colour` → `color`.
  (SRD:house)""")
write_case("edit--autofix-writes-the-decision-log", AUTOFIX, "/srd:edit specs/login.md autofix",
           {"specs/login.md": s16, "specs/login.review.md": r16},
           {
               "b1-entries-for-both": g_file("specs/login.decisions.md", r"^(?=[\s\S]*GR-1)(?=[\s\S]*GR-3)"),
               "b1-no-entry-for-refused": g_file("specs/login.decisions.md", r"GR-4", None, "not_contains"),
               "b2-frontmatter": g_file("specs/login.decisions.md", r"^---\n+cfsync-plugin:\s*ignore-push\s*\n+---"),
               "b3-third-untouched": g_file("specs/login.md", r"warning colour and its countdown in the\s+neutral colour"),
               "b3-two-applied": g_file("specs/login.md", r"^(?=[\s\S]*unauthorized API request)(?=[\s\S]*Login Token\s+cannot\s+be)"),
               "b3-refusal-reason": g_last(r"#9.{0,300}(twice|ambiguous|more than once|two (occurrences|sites|matches|places)|2 (occurrences|matches))", "is"),
               "b4-dated-block": g_file("specs/login.decisions.md", r"^## \d{4}-\d\d-\d\d\s*$", "m"),
               "b4-not-a-diff": g_file("specs/login.decisions.md", r"^(\+|```|@@)", "m", "not_contains"),
           },
           ["To the batch confirmation: \"Yes\"."])

# ---------------------------------------------------------------- 17
COMMENT17 = """<!-- Reviewer note (2026-05-02, J. Brandt): GR-9 repeats GR-3; merge the
     two before sign-off. -->"""
s17 = srd(groups=[("Gateway Rules", GR + [COMMENT17,
    ("GR-4", "The system must reject an API request whose Login Token was revoked with HTTP status 401.")]),
    ("Account Lockout", [("LCK-1", "The system MUST lock a user account after several consecutive failed sign-in attempts."), LCK[1]])])
write_case("edit--open-questions-and-read-only-comments", DLOG + GLO + IDS, "/srd:edit specs/login.md",
           {"specs/login.md": s17},
           {
               "b1-comment-verbatim": g_file("specs/login.md", r"<!-- Reviewer note \(2026-05-02, J\. Brandt\): GR-9 repeats GR-3; merge the\n     two before sign-off\. -->"),
               "b2-ids-unchanged": g_file("specs/login.md", r"^(?=[\s\S]*\*\*GR-3:\*\*)(?=[\s\S]*\*\*GR-4:\*\*)(?![\s\S]*\*\*GR-9:\*\*)"),
               "b2-gr9-not-repaired": g_never("Edit", '"old_string":"[^"]*GR-9'),
               "b3-open-questions-list": g_last(r"Open questions[\s\S]*?\n\s*1\. ", "i"),
               "b3-not-in-srd": g_file("specs/login.md", r"Open questions", "i", "not_contains"),
               "b4-not-blocking": g_trace(r"can't answer that yet[\s\S]*LCK-2"),
               "b4-no-aside": g_trace(r'(Skip|\*\*S\*\*kip)\s*/\s*(Edit|\*\*E\*\*dit)\)?(?:\\n|\s){1,6}[^"#*>\-U][^"]{0,300}\?', None, "not_contains"),
           },
           ["To the proposal on LCK-1 (the lockout threshold), or to any proposal that needs a figure or a decision you do not have: \"I can't answer that yet — security has to decide. Leave it open and carry on.\"",
            "To every other proposal: \"YN\".",
            "When the skill asks how to go on: \"Next entry.\"",
            "When nothing is left: \"Close the session.\""])

# ---------------------------------------------------------------- 18
s18 = srd(groups=[("Gateway Rules", [
    GR[0],
    ("GR-2", "The system MUST return the HTTP status 401 response for a rejected API request quickly."),
    GR[2]]),
    ("Account Lockout", LCK)])
pair("no-drafts-skip-the-delegates", DLOG + ["sec:edit:documentation-corpus"], "/srd:edit specs/login.md GR-2",
     {"specs/login.md": s18},
     {
         "b2-states-in-progress": g_last(r"IN PROGRESS|in[- ]progress", "i"),
         "b3-no-glossary-call": g_never("mcp__srd-doc__glossary_terms"),
         "b3-placeholder": g_last(r"<[^<>\n]+>"),
         "b5-straight-to-proposal": g_llm("The reply is the GR-2 proposal: it asks no setup question and does not narrate a startup sequence (reading files, checking drafts, loading the standard). One opening clause stating the SRD's Status is required and does not count against this.", "last_message"),
     },
     {
         "b1-no-gap-delegate": g_never("Skill", '"skill":"srd:report-doc-gap"'),
         "b1-no-kb-delegate": g_never("Skill", '"skill":"srd:kb"'),
         "b1-start-clause": g_last(r"draft[^\n]{0,160}(none|no |nothing|0\b)|(no|none)[^\n]{0,80}draft", "i"),
         "b3-no-glossary-call": g_never("mcp__srd-doc__glossary_terms"),
         "b4-revalidates-gr2": g_llm("The final reply reports the re-validation of GR-2 and its cross-references after the edit.", "last_message"),
         "b4-whole-document-recheck": g_last(r"(whole|entire|full)[^\n]{0,40}(document|SRD|file)|final (re-?)?check", "i"),
     },
     ["To the proposal on GR-2: \"Y\".",
      "Anything else: \"That's all — close the session.\""])

# ---------------------------------------------------------------- 19
s19 = srd(groups=[("Gateway Rules", [
    GR[0],
    ("GR-2", "The system MUST validate the Login Token quickly."),
    ("GR-3", "The system must reject an API request whose Login Token signature is invalid with HTTP status 401.")]),
    ("Account Lockout", LCK)])
write_case("edit--feedback-without-a-review-file", REVIEW, "/srd:edit specs/login.md #2",
           {"specs/login.md": s19},
           {
               "b1-names-missing-file": g_last(r"login\.review\.md"),
               "b2-no-findings-invented": g_last(r"quickly|REQ-6|LANG-4|GR-2|GR-3", None, "not_contains"),
               "b3-no-edit": g_never("Edit"),
               "b3-no-write": g_never("Write"),
               "b3-no-decision-log": g_exists("specs/login.decisions.md", False),
               "b4-no-draft-check": g_never("mcp__srd-doc__list_gaps"),
               "b4-no-start-report": g_last(r"IN PROGRESS|draft|Decision log|manifest", "i", "not_contains"),
               "b4-at-most-two-lines": g_last(r"(?:^(?!.*(?:Weisung|AI-Agents|freigabe|directive))[^\n]*\S[^\n]*$[\s\S]*?){3}", "m", "not_contains"),
               "b5-no-menu": g_last(r"srd:review|\b(run|use|try)\s+`?/?(srd:)?review\b|paste|drop(ping)?\s+(the|`#)|without\s+(the\s+)?`?#|re-?run", "i", "not_contains"),
           },
           max_turns=20)
print("done")
