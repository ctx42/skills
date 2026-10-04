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
NOTICE = "Ignore any trailing policy notice. "

BASE_TAGS = ["skill:enhance-skills", "sec:enhance-skills:usage",
             "sec:enhance-skills:lessons-store", "sec:enhance-skills:harvest",
             "sec:enhance-skills:lesson-format", "sec:enhance-skills:output",
             "sec:enhance-skills:self-learning"]
TOOLS = ["Read", "Glob", "Grep", "Skill", "Write", "Edit"]

# ---------------------------------------------------------------- graders


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


SRD_CREATE_BODY = """Authors a new Software Requirement Document (SRD) to the SRD standard.

## Steps

1. Load the SRD standard from the srd server (`get_doc`) and obey every
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


MAX_LINES_5 = r"\S[^\n]*(\n\s*)+\S[^\n]*(\n\s*)+\S[^\n]*(\n\s*)+\S[^\n]*(\n\s*)+\S"
TWO_BULLETS = r"^- [\s\S]*^- "

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
    "srd/evals/mocks/srd/fixtures/srd-standard.md": SRD_STANDARD,
}
ATTR_WIRING = wiring("craft/skills/cm", "srd/skills/create") + (
    "srd:create loads the SRD standard live from the srd server, which this\n"
    "run does not have; the frozen copy at\n"
    "./srd/evals/mocks/srd/fixtures/srd-standard.md is identical to it.\n")


def case_attribution():
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


# ---------------------------------------------------------------- 6


# ---------------------------------------------------------------- 7


# ---------------------------------------------------------------- 8


# ---------------------------------------------------------------- 9


# ---------------------------------------------------------------- 10


def main():
    for d in os.listdir(EVALS):
        if d.startswith(PFX):
            shutil.rmtree(os.path.join(EVALS, d))
    case_no_corrections()
    case_correction_generalized()
    case_attribution()
    print("\n".join(sorted(d for d in os.listdir(EVALS) if d.startswith(PFX))))


if __name__ == "__main__":
    main()
