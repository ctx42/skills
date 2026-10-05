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
        inscope=INSCOPE, osc=OSC, groups=None, tail="", title="Login Token Validation",
        notice="top"):
    if groups is None:
        groups = [("Gateway Rules", GR), ("Account Lockout", LCK)]
    color = {"ACCEPTED": "green"}.get(status, "blue")
    rows = [("**Objective**", "Specify how the API Gateway validates Login Tokens."),
            ("**Initiative**", initiative),
            ("**Owners**", owners),
            ("**Status**", f"[[!{status}\\|color={color};style=bold]]"),
            ("**Designs**", designs)]
    p = [f"# {title}", table(rows), "[[TOC]]"] + ([NOTICE] if notice == "top" else [])
    p += ["## Introduction", wrap(intro)] + ([NOTICE] if notice == "intro" else [])
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
         "b2-no-glossary-call": g_never("mcp__srd__glossary_terms"),
         "b3-lists-all-three": g_last(r"^(?=.*#4)(?=.*#7)(?=.*#9)", "s"),
         "b3-one-batch-confirmation": g_last(r"^[^\n]*\?[^\n]*$", "m", "count:1"),  # one question for the batch
     },
     {
         "b1-unlisted-spelling-kept": g_file("specs/login.md", r"authorises"),
         "b1-non-errata-finding-kept": g_file("specs/login.md", r"a short\s+while"),
         "b2-no-glossary-call": g_never("mcp__srd__glossary_terms"),
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

# ---------------------------------------------------------------- 10

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
               "b1-search-before-edit": g_order("mcp__srd__search", None, "Edit", LOGIN_EDIT),
               "b1-gap-names-queries": g_used("mcp__srd__report_gap", '"search_terms":\\["', 1),
               "b2-gap-is-draft": g_used("mcp__srd__report_gap", '"draft":true', 1),
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
               "b4-no-draft-check": g_never("mcp__srd__list_gaps"),
               "b4-no-start-report": g_last(r"IN PROGRESS|draft|Decision log|manifest", "i", "not_contains"),
               "b4-at-most-two-lines": g_last(r"(?:^(?!.*(?:policy|directive|approval))[^\n]*\S[^\n]*$[\s\S]*?){3}", "m", "not_contains"),
               "b5-no-menu": g_last(r"srd:review|\b(run|use|try)\s+`?/?(srd:)?review\b|paste|drop(ping)?\s+(the|`#)|without\s+(the\s+)?`?#|re-?run", "i", "not_contains"),
           },
           max_turns=20)
# ---------------------------------------------------------------- 20, 21
GR1_UK = ("GR-1", "The system MUST reject an unauthorised API request with HTTP status 401.")
NOTICE_GROUPS = [("Gateway Rules", [GR1_UK, GR[1], GR[2]]), ("Account Lockout", LCK)]
r_notice = review("""## Errata

- [ ] #4 [minor, linguistic] GR-1 uses British spelling: `unauthorised` →
  `unauthorized`. (SRD:house)

- [ ] #10 [minor, structure] Metadata: the STR-8 keyword notice is missing:
  `(missing)` →

""" + "\n".join("  " + l for l in NOTICE.splitlines()) + """

  (SRD:STR-8)""")
NOTICE_RE = r'The keywords "MUST"'
AFTER_TOC = r"\[\[TOC\]\]\s*\n> \[!INFO\]"

write_case("edit--autofix-inserts-missing-notice", AUTOFIX, "/srd:edit specs/login.md autofix",
           {"specs/login.md": srd(groups=NOTICE_GROUPS, notice="none"), "specs/login.review.md": r_notice},
           {
               "b1-inserted-after-toc": g_regex("{source: file, path: specs/login.md}",
                                                AFTER_TOC + r"\n> The keywords \"MUST\".{0,600}?shown here\.\s*\n## Introduction", "s"),
               "b1-exactly-once": g_regex("{source: file, path: specs/login.md}",
                                          NOTICE_RE + ".*" + NOTICE_RE, "s", "not_contains"),
               "b2-applied-gr1": g_file("specs/login.md", r"\*\*GR-1:\*\* The system MUST reject an unauthorized API request"),
               "b3-handoff-command": g_last(r"review specs/login\.md check (#4 #10|#10 #4)(?! #)"),
           },
           ["To the batch confirmation: \"Yes\"."])

write_case("edit--autofix-misplaced-notice-is-stale", AUTOFIX, "/srd:edit specs/login.md autofix",
           {"specs/login.md": srd(groups=NOTICE_GROUPS, notice="intro"), "specs/login.review.md": r_notice},
           {
               "b1-no-second-notice": g_regex("{source: file, path: specs/login.md}",
                                              NOTICE_RE + ".*" + NOTICE_RE, "s", "not_contains"),
               "b1-not-inserted-after-toc": g_regex("{source: file, path: specs/login.md}", AFTER_TOC, None, "not_contains"),
               "b2-reported-stale": g_last(r"#10.{0,300}(stale|already|present|exists|misplaced|not (inserted|applied)|skipp)", "is"),
               "b3-applied-gr1": g_file("specs/login.md", r"\*\*GR-1:\*\* The system MUST reject an unauthorized API request"),
               "b3-handoff-command": g_last(r"review specs/login\.md check #4(?! #)"),
           },
           ["To the batch confirmation: \"Yes\"."])

print("done")
