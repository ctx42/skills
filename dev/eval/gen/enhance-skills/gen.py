#!/usr/bin/env python3
"""Generate craft/evals/enhance-skills--* native eval cases.

Re-runnable; owns only enhance-skills--*.
"""
import json
import os
import re
import shutil
import uuid
import random

# Seeded so a rerun reproduces the committed history files byte for byte.
_rng = random.Random(42)


def _uuid4():
    return uuid.UUID(int=_rng.getrandbits(128), version=4)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
EVALS = os.path.join(ROOT, "craft/evals")
PFX = "enhance-skills--"

ENGLISH = "The user writes English; reply in English.\n"
PERSONA = """Automated eval: the user is absent. Whenever the skill would stop and wait
for the user, take the next scripted answer below as the reply and continue
in this same run; never end the run to wait. If none fits, give the most
plausible answer and continue.
Before taking a scripted answer, write out in full, as your reply text, the
message you would send the user at that point.
"""
WIRING = """Eval wiring: this workspace is the user's writable git checkout of the
ctx42-skills plugins. The skills this session used ran from it ({dirs}), not
from the read-only plugin copy this run loads: read and write those workspace
files, never the loaded copy. The environment sets AGENT_DATA_DIR to
`.agent-data` at the root of this workspace, so
`${{AGENT_DATA_DIR:-$HOME/.agent-data}}` resolves to ./.agent-data here; never
touch the real home directory.
"""
NOTICE = ("Ignore any trailing notice about a company directive "
          "(«Nutzung von Claude und andere AI-Agents»). ")

BASE_TAGS = ["skill:enhance-skills", "sec:enhance-skills:usage",
             "sec:enhance-skills:lessons-store", "sec:enhance-skills:harvest",
             "sec:enhance-skills:lesson-format", "sec:enhance-skills:output",
             "sec:enhance-skills:self-learning"]
RETRO_TAGS = BASE_TAGS + ["sec:enhance-skills:retrofit"]
TOOLS = ["Read", "Glob", "Grep", "Skill", "Write", "Edit"]

# ---------------------------------------------------------------- graders


# Runs have Bash: a file read may be Read or a shell cat/sed.
READ_ANY = r'"name":"(?:Read|Bash)","input":\{"(?:file_path|command)":"(?:[^"\\]|\\.)*?'


def g_regex(pattern, target="last_message", flags=None, match=None):
    fm = ["type: regex"]
    if target.startswith("file:"):
        fm.append(f"target: {{source: file, path: {target[5:]}}}")
    else:
        fm.append(f"target: {target}")
    if match:
        fm.append(f'match: "{match}"')
    if flags:
        fm.append(f'flags: "{flags}"')
    return "---\n" + "\n".join(fm) + "\n---\n" + pattern + "\n"


def g_not(pattern, target="last_message", flags=None):
    return g_regex(pattern, target, flags, "not_contains")


def g_tool(tool, input_match=None, min_=None, max_=None, both=False):
    fm = ["type: tool_used", f"tool: {tool}"]
    if input_match:
        fm.append(f"input_match: '{input_match}'")
    if min_ is not None:
        fm.append(f"min: {min_}")
    if max_ is not None:
        fm.append(f"max: {max_}")
    if both:
        fm.append("arm: both")
    return "---\n" + "\n".join(fm) + "\n---\n"


def g_never(tool, input_match=None):
    return g_tool(tool, input_match, 0, 0, True)


def g_exists(path, exists=True):
    return (f"---\ntype: file_exists\npath: \"{path}\"\n"
            f"exists: {str(exists).lower()}\n---\n")


def g_llm(claim):
    return f"---\ntype: llm\nfocus: last_message\n---\n{NOTICE}{claim}\n"


WAITS = r"\?|confirm|approv|go ahead|go-ahead|say (yes|go)|reply (yes|go)|once you"

# ---------------------------------------------------------------- history


class History:
    """A hand-built session transcript for context.history_file (--resume)."""

    def __init__(self):
        self.sid = str(_uuid4())
        self.prev = None
        self.lines = []
        self.n = 0

    def _add(self, typ, msg, meta=False):
        u = str(_uuid4())
        self.n += 1
        line = {
            "parentUuid": self.prev, "isSidechain": False,
            "userType": "external", "cwd": "/work/project",
            "sessionId": self.sid, "version": "2.1.288", "type": typ,
            "message": msg, "uuid": u,
            "timestamp": f"2026-10-01T10:{self.n:02d}:00.000Z"}
        if meta:
            line["isMeta"] = True
        self.lines.append(line)
        self.prev = u

    def user(self, text):
        self._add("user", {"role": "user", "content": text})

    def command(self, name, args="", base=None):
        """A slash-command skill invocation as Claude Code records it."""
        self.user(f"<command-message>{name}</command-message>\n"
                  f"<command-name>/{name}</command-name>\n"
                  f"<command-args>{args}</command-args>")
        if base:
            self._add("user", {"role": "user", "content": [{
                "type": "text",
                "text": f"Base directory for this skill: {base}\n\n"
                        f"(skill instructions loaded from {base}/SKILL.md)"}]},
                meta=True)

    def _assistant(self, content, stop):
        self._add("assistant", {
            "id": f"msg_{_uuid4().hex[:24]}", "type": "message",
            "role": "assistant", "model": "claude-opus-5-5",
            "content": content, "stop_reason": stop, "stop_sequence": None,
            "usage": {"input_tokens": 10, "output_tokens": 10}})

    def say(self, text):
        self._assistant([{"type": "text", "text": text}], "end_turn")

    def tool(self, text, name, inp, result):
        tid = f"toolu_{_uuid4().hex[:24]}"
        content = ([{"type": "text", "text": text}] if text else [])
        content.append({"type": "tool_use", "id": tid, "name": name,
                        "input": inp})
        self._assistant(content, "tool_use")
        self._add("user", {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": tid, "content": result}]})

    def dump(self):
        return "\n".join(json.dumps(x) for x in self.lines) + "\n"

# ---------------------------------------------------------------- fixtures


BLOCK_TMPL = """## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/<plugin>/<skill>.md`,
the sibling winning a conflict — a read-only install writes the second, and what
it learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule to the sibling when this directory
is writable, else to the fallback, creating it, and report where.
"""


def block(plugin, skill):
    return BLOCK_TMPL.replace("<plugin>", plugin).replace("<skill>", skill)


def skill_md(name, desc, body, plugin=None):
    s = (f"---\nname: {name}\ndescription: >\n  {desc}\nlicense: MIT\n---\n\n"
         f"# {name}\n\n{body.strip()}\n")
    if plugin:
        s += "\n" + block(plugin, name)
    return s


CM_BODY = """Writes a git commit message for the staged change using Conventional
Commits with a Linux kernel-style body.

## Steps

1. Read the staged diff (`git diff --cached`).
2. Write the summary line, then the body.
3. Show the message; commit only when asked.

## Summary line

- Type: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `style`, `build`,
  `ci`, `chore`, `revert`
- Scope: optional, short noun
- Description: imperative, lowercase, no period, ideally ≤ 50 chars (hard 72)

## Body

- Wrap at 72 columns.
- Imperative mood.
- Explain why the change was made; the diff shows what.

## Output

Print the message in one fenced block and nothing else."""


def cm_md(with_block=True):
    return skill_md("cm", "Writes git commit messages (Conventional Commits).",
                    CM_BODY, "craft" if with_block else None)


REVIEW_BODY = """Done-time Go quality review of a diff, a package, or a module.

## Steps

1. Read the target files.
2. Check each against the style rules and for correctness: bugs, edge cases,
   error handling.
3. Report findings grouped as Bugs, then Style, each with `file:line`.

## Output

One line per finding; no preamble."""

STYLE_BODY = """Enforced Go coding style; the rulebook to read before writing Go and a
style-only pass that lists offenses across a target and proposes fixes.

## Steps

1. List the `.go` files in the target.
2. Check each against the rules below and report every offense with
   `file:line`.
3. Apply the fixes the user accepts.

## Rules

- Receivers are a short type abbreviation, never a single letter.
- Wrap errors with `%w` and add context.
- Name the actual value `have` and the expected value `want` in tests.

## Output

One line per offense; no preamble."""

DOC_SMITH_BODY = """Writes and reviews technical documentation and user manuals.

## Steps

1. Read the sources the user names.
2. Draft or review the document section by section.
3. Write the result where the user asks.

## Output

Name the file written and the sections touched."""

PLAN_SMITH_BODY = """Writes an implementation plan as numbered checkbox items with a status
summary table.

## Steps

1. Read the brief.
2. Write the plan as numbered checkbox items, then the status table.
3. Save the plan and name its path.

## Output

The path written and the item count."""

FOO_BODY = """Formats the quarterly widget report from the raw export.

## Usage

```
/foo <export.csv>
```

## Steps

1. Read the export the user names.
2. Group rows by widget family; sum each family's units.
3. Write `report.md` beside the export.

## Output

Name the report written and the families it covers; nothing else."""

SRD_CREATE_BODY = """Authors a new Software Requirement Document (SRD) to the SRD standard.

## Steps

1. Load the SRD standard from the srd-doc server (`get_doc`) and obey every
   rule it states.
2. Interview the user for the gaps.
3. Write the SRD. Set the header `Status` to one of the standard's STA-1
   values, written exactly as the standard spells them; a new SRD starts at
   `IN PROGRESS`.

## Output

The path written and the open questions."""

SRD_STANDARD = """# SRD standard (frozen eval copy)

## Header

**STA-1:** The "Status" field MUST be one of: "IN PROGRESS", "PROPOSED",
"ACCEPTED", or "REJECTED".

**STA-2:** An SRD that requires changes to the UI MUST NOT have a "Status" of
"ACCEPTED" until its designs are linked.
"""

PLAN_LESSONS = """# Lessons

Rules learned for the `plan-smith` skill. Read before running; obey each line.

- Number items continuously across sections; never restart at 1.
- Default the plan path to tmp/<slug>-plan.md without asking.
"""


def heredocs(files):
    out = []
    for i, (path, body) in enumerate(files.items()):
        d = os.path.dirname(path)
        if d:
            out.append(f"mkdir -p {d}")
        if not body.endswith("\n"):
            body += "\n"
        out.append(f"cat > {path} <<'EOF_{i}'\n{body}EOF_{i}")
    return ("#!/usr/bin/env bash\nset -euo pipefail\n"
            + "\n".join(out) + "\n")

# ---------------------------------------------------------------- writer


def write_case(name, tags, prompt, graders, files=None, history=None,
               asp="", max_turns=40, timeout=300):
    name = PFX + name
    d = os.path.join(EVALS, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "graders"))
    fm = [f"tags: [case:{name}, {', '.join(tags)}]", "runs: 1",
          f"max_turns: {max_turns}", f"timeout_seconds: {timeout}",
          f"allowed_tools: [{', '.join(TOOLS)}]",
          "append_system_prompt: |"]
    fm += ["  " + ln if ln else "" for ln in (ENGLISH + asp).rstrip("\n").split("\n")]
    with open(os.path.join(d, "prompt.md"), "w") as f:
        f.write("---\n" + "\n".join(fm) + "\n---\n\n" + prompt + "\n")
    y = ['schema_version: "1.1"', f"name: {name}", "context:"]
    if files:
        y.append("  scaffold_script: scaffold.sh")
    if history:
        y.append("  history_file: history.jsonl")
    with open(os.path.join(d, "case.yaml"), "w") as f:
        f.write("\n".join(y) + "\n")
    if files:
        p = os.path.join(d, "scaffold.sh")
        with open(p, "w") as f:
            f.write(heredocs(files))
        os.chmod(p, 0o755)
    if history:
        with open(os.path.join(d, "history.jsonl"), "w") as f:
            f.write(history.dump())
    for gname, body in graders.items():
        with open(os.path.join(d, "graders", gname + ".md"), "w") as f:
            f.write(body)


def wiring(*dirs):
    return WIRING.format(dirs=", ".join(f"./{d}/" for d in dirs))


def answers(*lines):
    return "\n" + PERSONA + "\n" + "\n".join(
        f"{i}. {a}" for i, a in enumerate(lines, 1)) + "\n"


def js_escape(text):
    """Escape text for a JavaScript regex; newlines become \\n."""
    return re.sub(r"[\\^$.|?*+()\[\]{}/]", lambda m: "\\" + m.group(0),
                  text).replace("\n", r"\n")


def words_re(text):
    """Whitespace-tolerant regex for a run of words."""
    return r"\s+".join(js_escape(w) for w in text.split())


MAX_LINES_5 = r"\S[^\n]*(\n\s*)+\S[^\n]*(\n\s*)+\S[^\n]*(\n\s*)+\S[^\n]*(\n\s*)+\S"
THREE_BULLETS = r"^- [\s\S]*^- [\s\S]*^- "
TWO_BULLETS = r"^- [\s\S]*^- "
LONG_LINE = r"^.{81,}$"

# ---------------------------------------------------------------- 1


def case_no_corrections():
    h = History()
    h.command("craft:cm", base="./craft/skills/cm")
    h.tool("", "Bash", {"command": "git diff --cached"},
           "diff --git a/store/cache.go b/store/cache.go\n"
           "--- a/store/cache.go\n+++ b/store/cache.go\n"
           "@@ -12,6 +12,10 @@ func (cac *Cache) Get(key string) (Item, bool) {\n"
           "+\tif cac.ttl > 0 && time.Since(itm.stored) > cac.ttl {\n"
           "+\t\tdelete(cac.items, key)\n+\t\treturn Item{}, false\n+\t}\n")
    h.say("```\nfeat(store): expire cache entries after their TTL\n\n"
          "`Cache.Get` returned entries forever, so a configured TTL had no\n"
          "effect. Drop an entry on read once it is older than the TTL and\n"
          "report it as missing.\n```")
    h.user("perfect, thanks")
    h.say("Glad it fits.")
    write_case(
        "no-corrections", BASE_TAGS, "/craft:enhance-skills",
        {
            "b1-reports-none": g_regex(
                r"no (new )?(lessons?|corrections?|rules?)|nothing (to (record|file|capture|learn)|qualif|was corrected|worth)|"
                r"(lessons?|corrections?)[^\n]{0,20}\bnone\b", flags="i"),
            "b1-no-cm-lessons": g_exists("craft/skills/cm/LESSONS.md", False),
            "b1-no-agent-data": g_exists(".agent-data/ctx42-skills/lessons/craft/cm.md", False),
            "b1-no-write": g_never("Write"),
            "b1-no-edit": g_never("Edit"),
            "b2-no-rule": g_llm("The reply proposes no rule or lesson to "
                                "record; saying that there is nothing to "
                                "record is fine."),
            "b3-short": g_not(MAX_LINES_5),
            "b3-no-narration": g_llm("The reply does not narrate the scan and "
                                     "does not list the candidate items it "
                                     "considered and rejected."),
        },
        files={"craft/skills/cm/SKILL.md": cm_md()}, history=h,
        asp=wiring("craft/skills/cm"))

# ---------------------------------------------------------------- 2


ROWS_GO = """package store

import "database/sql"

// LoadAll reads every table in names and returns the row counts.
func LoadAll(db *sql.DB, names []string) (map[string]int, error) {
	out := map[string]int{}
	for _, name := range names {
		rows, err := db.Query("SELECT id FROM " + name)
		if err != nil {
			return nil, err
		}
		defer rows.Close()
		for rows.Next() {
			out[name]++
		}
	}
	return out, nil
}
"""


def review_history():
    h = History()
    h.command("go:review", "./store", base="./go/skills/review")
    h.tool("", "Read", {"file_path": "store/load.go"}, ROWS_GO)
    h.say("**Bugs**\n\n- store/load.go:9 — table name concatenated into the "
          "query; quote it or check it against an allow-list.\n\n**Style**\n\n"
          "- store/load.go:13 — nit: `defer rows.Close()` inside the loop; "
          "close explicitly at the end of each iteration.")
    h.user("that's not a nit, it's a real leak — the file handle lives until "
           "the function returns. Flag resource leaks as bugs, not style.")
    h.say("Agreed. Re-filed under **Bugs**:\n\n- store/load.go:13 — `defer "
          "rows.Close()` inside the loop holds every result set (and its "
          "connection) open until `LoadAll` returns; close each `rows` before "
          "the next iteration.")
    return h


REVIEW_FILES = {"go/skills/review/SKILL.md":
                skill_md("review", "Done-time Go quality review.", REVIEW_BODY, "go")}


def case_correction_generalized():
    tgt = "file:go/skills/review/LESSONS.md"
    write_case(
        "correction-generalized--gate", BASE_TAGS, "/craft:enhance-skills",
        {
            "b1-no-write": g_never("Write"),
            "b1-no-edit": g_never("Edit"),
            "b1-waits": g_regex(WAITS, flags="i"),
            "b2-names-leaks": g_regex(r"leak", flags="i"),
            "b2-generalizes": g_llm(
                "The proposed rule is stated generally, about resource leaks "
                "being bugs rather than style, not as a note about this run's "
                "rows.Close loop or about the user disagreeing."),
            "b3-target": g_regex(r"go/skills/review/LESSONS\.md"),
            "b3-not-agent-data": g_not(r"lessons/go/review\.md"),
        },
        files=REVIEW_FILES, history=review_history(),
        asp=wiring("go/skills/review"))
    write_case(
        "correction-generalized", BASE_TAGS, "/craft:enhance-skills",
        {
            "b2-rule-on-leaks": g_regex(r"leak", tgt, flags="i"),
            "b2-not-run-specific": g_not(
                r"the user|disagreed|this run|that loop|LoadAll", tgt, flags="i"),
            "b2-one-rule": g_not(TWO_BULLETS, tgt, flags="m"),
            "b3-in-place": g_exists("go/skills/review/LESSONS.md"),
            "b3-no-agent-data": g_exists(".agent-data/ctx42-skills/lessons/go/review.md", False),
            "b3-body-untouched": g_not(r"leak", "file:go/skills/review/SKILL.md", flags="i"),
            "b4-header": g_regex(r"^# Lessons\n", tgt),
        },
        files=REVIEW_FILES, history=review_history(),
        asp=wiring("go/skills/review") + answers("Yes, write it."))

# ---------------------------------------------------------------- 3


def case_task_fact():
    h = History()
    h.command("craft:doc-smith", "write the operator chapter of docs/manual.md "
              "from src/dispatch/", base="./craft/skills/doc-smith")
    h.say("Drafted the operator chapter in docs/manual.md: opening the "
          "dispatcher screen, assigning a job, and handling a failed upload.")
    h.user("call it the Dispatch Board, not the dispatcher screen — that's "
           "what the UI says")
    h.say("Renamed every \"dispatcher screen\" to \"Dispatch Board\" (7 places).")
    h.user("put the output in docs/ops/, not docs/")
    h.say("Moved the chapter to docs/ops/manual.md.")
    h.say("Added a troubleshooting note: \"A failed upload is retried 3 times, "
          "30 seconds apart, before the job is marked Failed.\"")
    h.user("you made that number up — if the source doesn't say it, don't "
           "assert it.")
    h.say("You're right: src/dispatch/ never states a retry count or interval. "
          "Replaced it with \"A failed upload is retried automatically before "
          "the job is marked Failed.\"")
    tgt = "file:craft/skills/doc-smith/LESSONS.md"
    write_case(
        "task-fact-is-not-a-lesson", BASE_TAGS, "/craft:enhance-skills",
        {
            "b1-files-fabrication-rule": g_regex(
                r"assert|invent|fabricat|made up|make up|never state|unsourced|"
                r"not (stated|in the source)|source", tgt, flags="i"),
            "b2-no-terminology": g_not(r"Dispatch Board|dispatcher screen", tgt, flags="i"),
            "b2-no-output-dir": g_not(r"docs/ops", tgt),
            "b3-at-most-two-rules": g_not(THREE_BULLETS, tgt, flags="m"),
        },
        files={"craft/skills/doc-smith/SKILL.md":
               skill_md("doc-smith", "Writes and reviews technical documentation.",
                        DOC_SMITH_BODY, "craft")},
        history=h, asp=wiring("craft/skills/doc-smith") + answers("Yes, write it."))

# ---------------------------------------------------------------- 4


def attribution_history():
    h = History()
    h.user("Rename the `ListExports` handler to `Exports` and push the branch.")
    h.say("Renamed `ListExports` to `Exports` in api/export.go and its two "
          "callers, and ran `git push origin fix/export-empty-csv`.")
    h.user("never run git push unless I ask for it in that same message — I "
           "review before anything leaves my machine.")
    h.say("Understood; I won't push without an explicit ask.")
    h.command("craft:cm", base="./craft/skills/cm")
    h.say("```\nfeat(api): rename export handler\n\n"
          "Rename `ListExports` to `Exports` to match the other handlers.\n```\n\n"
          "Type `feat` taken from the branch prefix.")
    h.user("derive the commit type from the diff, not the branch name — "
           "a rename with no behaviour change is a refactor.")
    h.say("```\nrefactor(api): rename export handler\n\n"
          "Rename `ListExports` to `Exports` to match the other handlers.\n```")
    h.command("srd:create", "specs/export.md", base="./srd/skills/create")
    h.say("Wrote specs/export.md with header `Status: in progress`.")
    h.user("Status values are uppercase — IN PROGRESS, not in progress.")
    h.say("Fixed: `Status: IN PROGRESS`.")
    return h


ATTR_FILES = {
    "craft/skills/cm/SKILL.md": cm_md(),
    "srd/skills/create/SKILL.md": skill_md(
        "create", "Authors a new SRD to the SRD standard.", SRD_CREATE_BODY, "srd"),
    "srd/evals/mocks/srd-doc/fixtures/srd-standard.md": SRD_STANDARD,
}
ATTR_WIRING = wiring("craft/skills/cm", "srd/skills/create") + (
    "srd:create loads the SRD standard live from the srd-doc server, which this\n"
    "run does not have; the frozen copy at\n"
    "./srd/evals/mocks/srd-doc/fixtures/srd-standard.md is identical to it.\n")


def case_attribution():
    write_case(
        "attribute-to-the-driving-skill--gate", BASE_TAGS, "/craft:enhance-skills",
        {
            "b1-cm-target": g_regex(r"craft/skills/cm/LESSONS\.md"),
            "b1-cm-rule": g_regex(r"diff", flags="i"),
            "b2-names-where-it-lives": g_regex(
                r"STA-1|create/SKILL\.md|SRD standard|the standard", flags="i"),
            "b2-status-dropped": g_llm(
                "The Status-uppercase correction is not proposed as a lesson "
                "for any skill; the reply says it is dropped because the SRD "
                "standard (STA-1) or srd:create's own body already carries it."),
            "b4-push-named": g_regex(r"push", flags="i"),
            "b4-push-not-filed": g_llm(
                "The git push correction is not proposed as a lesson for any "
                "skill; the reply says it belongs to the agent's standing "
                "instructions (for example CLAUDE.md) or to no skill."),
            "b5-no-write": g_never("Write"),
            "b5-no-edit": g_never("Edit"),
            "b5-waits": g_regex(WAITS, flags="i"),
        },
        files=ATTR_FILES, history=attribution_history(), asp=ATTR_WIRING)
    cm = "file:craft/skills/cm/LESSONS.md"
    write_case(
        "attribute-to-the-driving-skill", BASE_TAGS, "/craft:enhance-skills",
        {
            "b1-cm-rule-written": g_regex(r"diff", cm, flags="i"),
            "b2-no-srd-lessons": g_exists("srd/skills/create/LESSONS.md", False),
            "b2-no-srd-agent-data": g_exists(".agent-data/ctx42-skills/lessons/srd/create.md", False),
            "b3-no-srd-write": g_never("Write", "srd/"),
            "b3-no-srd-edit": g_never("Edit", "srd/"),
            "b3-no-status-in-cm": g_not(r"status|uppercase|lowercase", cm, flags="i"),
            "b4-no-push-in-cm": g_not(r"push", cm, flags="i"),
            "b4-no-push-in-cm-body": g_not(r"push", "file:craft/skills/cm/SKILL.md", flags="i"),
        },
        files=ATTR_FILES, history=attribution_history(),
        asp=ATTR_WIRING + answers("Yes, write it."))

# ---------------------------------------------------------------- 5


def case_retrofit():
    foo = skill_md("foo", "Formats the quarterly widget report.", FOO_BODY)
    tgt = "file:craft/skills/foo/SKILL.md"
    words = block("craft", "foo")
    write_case(
        "retrofit-missing-block", RETRO_TAGS, "/craft:enhance-skills craft/skills/foo",
        {
            "b1-body-untouched": g_regex("^" + js_escape(foo.rstrip("\n")), tgt),
            "b1-after-output": g_regex(r"\n## Output\n[\s\S]*\n## Self-learning\n", tgt),
            "b1-last-section": g_not(r"\n## Self-learning\n[\s\S]*\n## ", tgt),
            "b2-exact-words": g_regex(words_re(words), tgt),
            "b2-wrapped-80": g_not(LONG_LINE, tgt, flags="m"),
            "b3-literal-path": g_regex(
                js_escape("${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/craft/foo.md"), tgt),
            "b3-not-expanded": g_not(r"/home/|<plugin>|<skill>", tgt),
            "b4-no-lessons": g_exists("craft/skills/foo/LESSONS.md", False),
            "b4-no-agent-data": g_exists(".agent-data/ctx42-skills/lessons/craft/foo.md", False),
            "b5-names-file": g_regex(r"foo/SKILL\.md"),
            "b5-no-restate": g_not(r"Obey this skill's lessons|sibling winning|absence is the normal"),
        },
        files={"craft/skills/foo/SKILL.md": foo},
        asp=RETRO_WIRING + answers("Yes, go ahead."))

RETRO_WIRING = """Eval wiring: this workspace is the user's writable git checkout of the
ctx42-skills plugins; the skill to retrofit is ./craft/skills/foo/ in it. Edit
that workspace file, never the read-only plugin copy this run loads. The
environment sets AGENT_DATA_DIR to `.agent-data` at the root of this
workspace; never touch the real home directory.
"""

# ---------------------------------------------------------------- 6


def plan_history():
    h = History()
    h.command("craft:plan-smith", "add CSV export to the reports page",
              base="./craft/skills/plan-smith")
    h.tool("", "Glob", {"pattern": "docs/**"},
           "docs/index.md\ndocs/plans/search-plan.md\ndocs/api.md")
    h.say("Wrote the plan to tmp/csv-export-plan.md: 9 items, all N.")
    h.user("stop guessing the path — when I've got a docs tree, put the plan "
           "in docs/plans/ and tell me, don't dump it in tmp.")
    h.say("Moved it to docs/plans/csv-export-plan.md.")
    return h


PLAN_FILES = {
    "craft/skills/plan-smith/SKILL.md": skill_md(
        "plan-smith", "Writes implementation plans.", PLAN_SMITH_BODY, "craft"),
    "craft/skills/plan-smith/LESSONS.md": PLAN_LESSONS,
}


def case_supersede():
    write_case(
        "supersede-a-contradicted-lesson--gate", BASE_TAGS, "/craft:enhance-skills",
        {
            "b1-reads-lessons": g_regex(READ_ANY + r"plan-smith/LESSONS", "trace"),
            "b1-flags-conflict": g_regex(
                r"supersed|replac|rewrit|contradict|overrul|conflict", flags="i"),
            "b4-shows-old-line": g_regex(r"tmp/<slug>-plan\.md|without asking"),
            "b4-shows-new-rule": g_regex(r"docs/plans|docs tree", flags="i"),
            "b4-no-write": g_never("Write"),
            "b4-no-edit": g_never("Edit"),
        },
        files=PLAN_FILES, history=plan_history(),
        asp=wiring("craft/skills/plan-smith"))
    tgt = "file:craft/skills/plan-smith/LESSONS.md"
    write_case(
        "supersede-a-contradicted-lesson", BASE_TAGS, "/craft:enhance-skills",
        {
            "b2-old-line-gone": g_not(
                r"^- Default the plan path to tmp/<slug>-plan\.md without asking\.$", tgt, flags="m"),
            "b2-new-rule-on-file": g_regex(r"docs/plans|docs tree", tgt, flags="i"),
            "b2-one-path-rule": g_regex(r"^- [^\n]*(\n  [^\n]*)*(path|docs/plans|tmp)", tgt,
                                        flags="mi", match="count:1"),
            "b2-other-rule-kept": g_regex(r"Number items continuously", tgt),
            "b3-one-sentence": g_not(
                r"^- (?=(?:[^\n]|\n  )*docs/plans)(?:[^\n]|\n  )*?(\.\s+\S|;)", tgt, flags="m"),
        },
        files=PLAN_FILES, history=plan_history(),
        asp=wiring("craft/skills/plan-smith") + answers("Yes, write it."))

# ---------------------------------------------------------------- 7


INSTALL = "home/.claude/plugins/cache/ctx42-skills/craft/skills/cm"


def case_read_only():
    h = History()
    h.command("craft:cm", base="./" + INSTALL)
    h.say("```\nchore(http): raise the client timeout to 30s\n\n"
          "Slow uploads hit the 10s default and failed.\n```")
    h.user("stop reaching for `chore` — every commit has a real type, and "
           "`chore` tells the reader nothing.")
    h.say("```\nfix(http): raise the client timeout to 30s\n\n"
          "Slow uploads hit the 10s default and failed.\n```")
    asp = ("Eval wiring: the cm skill this session used ran from a plugin install,\n"
           f"./{INSTALL}/ relative to this workspace (the\n"
           "user's ~/.claude/plugins/cache/... stand-in; the run's own $HOME is not\n"
           "it). There is no checkout of cm. The environment sets\n"
           "AGENT_DATA_DIR to `.agent-data` at the root of this workspace, so\n"
           "`${AGENT_DATA_DIR:-$HOME/.agent-data}` resolves to ./.agent-data here;\n"
           "never touch the real home directory.\n")
    store = ".agent-data/ctx42-skills/lessons/craft/cm.md"
    write_case(
        "read-only-install", BASE_TAGS, "/craft:enhance-skills",
        {
            "b1-store-created": g_exists(store),
            "b1-rule-in-store": g_regex(r"chore", "file:" + store),
            "b2-no-cache-write": g_never("Write", "plugins/cache"),
            "b2-no-cache-edit": g_never("Edit", "plugins/cache"),
            "b2-no-cache-lessons": g_exists(f"{INSTALL}/LESSONS.md", False),
            "b2-no-retrofit": g_not(r"Self-learning", f"file:{INSTALL}/SKILL.md"),
            "b3-names-path": g_regex(r"\.agent-data/ctx42-skills/lessons/craft/cm\.md"),
        },
        files={f"{INSTALL}/SKILL.md": cm_md(with_block=False)}, history=h,
        asp=asp + answers("Yes, write it."))

# ---------------------------------------------------------------- 8


def case_terse():
    h = History()
    h.command("go:style", "./parse", base="./go/skills/style")
    h.say("Fixed the offense at parse/parse_test.go:14 (`got` → `have`) and "
          "rewrote `TestParse` as a table-driven test.")
    h.user("fix the offense in place, don't restructure tests I didn't ask "
           "you to touch")
    h.say("Reverted the table rewrite; only the `got` → `have` rename remains.")
    h.command("go:style", "./...", base="./go/skills/style")
    h.say("12 offenses: 9 in vendor/github.com/x/y/, 3 in parse/.")
    h.user("skip vendored and generated files, they're not ours to style")
    h.say("Re-ran without vendor/: 3 offenses, all in parse/.")
    h.command("craft:cm", base="./craft/skills/cm")
    h.say("```\nchore(parse): rename test variables\n```")
    h.user("stop reaching for `chore`; every commit has a real type")
    h.say("```\ntest(parse): name test results have and want\n```")
    h.command("craft:enhance-skills")
    h.say("Proposed lessons:\n\n"
          "**go:style** → go/skills/style/LESSONS.md (new)\n"
          "- Fix a flagged offense in place; never restructure a test the "
          "user did not ask you to touch.\n"
          "- Skip vendored and generated files when checking style.\n\n"
          "**craft:cm** → craft/skills/cm/LESSONS.md (new)\n"
          "- Never use the `chore` type; every commit has a real type.\n\n"
          "Write these?")
    st = "file:go/skills/style/LESSONS.md"
    cm = "file:craft/skills/cm/LESSONS.md"
    write_case(
        "terse-output", BASE_TAGS, "/craft:enhance-skills yes, write them",
        {
            "b1-style-header": g_regex(r"^# Lessons\n", st),
            "b1-style-two-rules": g_regex(TWO_BULLETS, st, flags="m"),
            "b1-style-not-three": g_not(THREE_BULLETS, st, flags="m"),
            "b1-style-vendor": g_regex(r"vendor", st, flags="i"),
            "b1-style-restructure": g_regex(r"restructur|table", st, flags="i"),
            "b1-cm-header": g_regex(r"^# Lessons\n", cm),
            "b1-cm-chore": g_regex(r"chore", cm),
            "b1-cm-one-rule": g_not(TWO_BULLETS, cm, flags="m"),
            "b2-style-path": g_regex(r"go/skills/style/LESSONS\.md"),
            "b2-cm-path": g_regex(r"craft/skills/cm/LESSONS\.md"),
            "b2-counts": g_regex(r"\b(2|two)\b[\s\S]*\b(1|one)\b|\b(1|one)\b[\s\S]*\b(2|two)\b", flags="i"),
            "b3-no-restated-rules": g_not(r"vendor|table-driven|restructure|chore", flags="i"),
            "b4-no-narration": g_not(r"^(I'll|I will|Let me|Now I|Reading|Appending|Writing)", flags="mi"),
            "b4-no-preamble-or-summary": g_llm(
                "The reply has no preamble before the per-skill write report "
                "and no closing summary after it."),
            "b5-no-file-pasted": g_not(r"# Lessons|Rules learned for"),
        },
        files={
            "go/skills/style/SKILL.md": skill_md("style", "Enforced Go coding style.", STYLE_BODY, "go"),
            "craft/skills/cm/SKILL.md": cm_md(),
        },
        history=h, asp=wiring("go/skills/style", "craft/skills/cm"))

# ---------------------------------------------------------------- 9


def case_body_rules():
    h = History()
    h.command("craft:cm", base="./craft/skills/cm")
    h.say("```\nfix(sync): retry a dropped upload once before failing the job\n\n"
          "A single dropped connection failed the whole sync job, although the "
          "server accepts\na repeated upload of the same chunk. Retry once "
          "before giving up.\n```")
    h.user("the body wraps at 72, not 80.")
    h.say("```\nfix(sync): retry a dropped upload once before failing the job\n\n"
          "A single dropped connection failed the whole sync job, although\n"
          "the server accepts a repeated upload of the same chunk. Retry\n"
          "once before giving up.\n```")
    write_case(
        "body-already-rules-it", BASE_TAGS, "/craft:enhance-skills",
        {
            "b1-reads-skill": g_regex(READ_ANY + r"craft/skills/cm/SKILL", "trace"),
            "b2-no-lessons": g_exists("craft/skills/cm/LESSONS.md", False),
            "b2-no-agent-data": g_exists(".agent-data/ctx42-skills/lessons/craft/cm.md", False),
            "b2-no-write": g_never("Write"),
            "b2-no-edit": g_never("Edit"),
            "b3-already-there": g_regex(r"already", flags="i"),
            "b3-names-72": g_regex(r"72"),
            "b3-points-at-reword": g_regex(
                r"reword|rewrit|rephras|strengthen|sharpen|more (prominent|explicit)|"
                r"skill edit|edit(ing)? (the |that |its )?(`?SKILL\.md`?|line|body)",
                flags="i"),
            "b4-does-not-ask": g_llm(
                "The reply does not ask the user whether the 72-column "
                "correction should still be filed as a lesson, or what to do "
                "with the duplicate."),
        },
        files={"craft/skills/cm/SKILL.md": cm_md()}, history=h,
        asp=wiring("craft/skills/cm"))

# ---------------------------------------------------------------- 10


APPROVED = "never restructure, rename, or reshape code the task did not ask about, even when the change looks like an obvious improvement"


def case_approved():
    h = History()
    h.command("go:review", "./cache", base="./go/skills/review")
    h.say("**Bugs**\n\n- cache/lru.go:41 — `Evict` reads `len(cac.order)` "
          "without the lock.\n\nAlso refactored `keyFor` into a "
          "`keyBuilder` type so its three call sites share one code path.")
    h.user("I didn't ask you to touch keyFor — revert that.")
    h.say("Reverted `keyFor` to its original form; only the `Evict` finding "
          "stands.")
    h.command("craft:enhance-skills")
    h.say("Proposed lesson:\n\n**go:review** → go/skills/review/LESSONS.md "
          f"(new)\n- {APPROVED}\n\nWrite it?")
    tgt = "file:go/skills/review/LESSONS.md"
    w = words_re(APPROVED[1:])
    write_case(
        "writes-the-rule-that-was-approved", BASE_TAGS,
        "/craft:enhance-skills yes, write it",
        {
            "b1-words-on-disk": g_regex(r"[Nn]" + w, tgt),
            "b2-nothing-added": g_regex(r"^- [Nn]" + w + r"\.?[ \t]*$(?!\n  \S)", tgt, flags="m"),
            "b3-wrapped-80": g_not(LONG_LINE, tgt, flags="m"),
        },
        files=REVIEW_FILES, history=h, asp=wiring("go/skills/review"))


def main():
    for d in os.listdir(EVALS):
        if d.startswith(PFX):
            shutil.rmtree(os.path.join(EVALS, d))
    case_no_corrections()
    case_correction_generalized()
    case_task_fact()
    case_attribution()
    case_retrofit()
    case_supersede()
    case_read_only()
    case_terse()
    case_body_rules()
    case_approved()
    print("\n".join(sorted(d for d in os.listdir(EVALS) if d.startswith(PFX))))


if __name__ == "__main__":
    main()
