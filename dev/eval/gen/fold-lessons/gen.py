#!/usr/bin/env python3
"""Generate craft/evals/fold-lessons--* native eval cases.

Re-runnable; owns only fold-lessons--*.
"""
import os
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
EVALS = os.path.join(ROOT, "craft/evals")
PFX = "fold-lessons--"

ENGLISH = "The user writes English; reply in English.\n"
PERSONA = """Automated eval: the user is absent. Whenever the skill would stop and wait
for the user, take the next scripted answer below as the reply and continue
in this same run; never end the run to wait. If none fits, give the most
plausible answer and continue.
"""
WIRING = """Eval wiring: this workspace is the user's writable git checkout of the
ctx42-skills plugins; the skills to fold live here, not in the read-only
plugin copy this run loads. The environment sets AGENT_DATA_DIR to
`.agent-data` at the root of this workspace, so `$AGENT_DATA_DIR` replaces
`~/.agent-data` here; never touch the real home directory.
"""
NOTICE = "Ignore any trailing policy notice. "

TAGS = ["skill:fold-lessons", "needs-shell", "sec:fold-lessons:usage",
        "sec:fold-lessons:generic-or-not", "sec:fold-lessons:validate",
        "sec:fold-lessons:procedure", "sec:fold-lessons:output",
        "sec:fold-lessons:self-learning"]
TOOLS = ["Read", "Glob", "Grep", "Skill", "Write", "Edit", "Bash(git:*)",
         "Bash(./dev/lint-skills.sh:*)", "Bash(./dev/eval-routine.sh:*)",
         "Bash(./dev/eval-probe.py:*)"]

GIT_INIT = """git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
"""

# JSON-string body of a Bash command in the trace.
S = r'(?:[^"\\]|\\.)*'

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


def g_file(path, pattern, flags=None, absent=False):
    return g_regex(pattern, "file:" + path, flags,
                   "not_contains" if absent else None)


def g_never(tool, input_match):
    return ("---\ntype: tool_used\n"
            f"tool: {tool}\ninput_match: '{input_match}'\n"
            "min: 0\nmax: 0\narm: both\n---\n")


def g_exists(path, exists=True):
    return (f"---\ntype: file_exists\npath: \"{path}\"\n"
            f"exists: {str(exists).lower()}\n---\n")


def line_with(a, b):
    """One line naming both a and b, in either order."""
    return rf"[^\n]*(?:{a}[^\n]*{b}|{b}[^\n]*{a})"

# ---------------------------------------------------------------- fixtures


BLOCK_TMPL = """## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/craft/<skill>.md` (pass `~` as
is, the file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable. A missing file needs no comment. On a correction or self-caught
mistake, append a one-line rule — general, naming nothing from the project at
hand (its files, tests, tickets) — to the sibling when this directory is
writable, else to the fallback, creating it, and report where.
"""


def skill_md(name, desc, body):
    return (f"---\nname: {name}\ndescription: >\n  {desc}\nlicense: MIT\n---\n\n"
            f"# {name}\n\n{body.strip()}\n\n"
            + BLOCK_TMPL.replace("<skill>", name))


CM_BODY = """## Usage

```
/cm   write a commit message for the staged change
```

## Steps

1. Read the staged diff (`git diff --cached`).
2. Write the summary line, then the body.
3. Show the message; commit only when asked.

## Summary line

- Type: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `chore`.
- Scope: optional, short noun.
- Description: imperative, lowercase, no period, at most 72 chars.

## Body

- Wrap at 72 columns; explain why, the diff shows what.
- No Co-Authored-By trailer.

## Output

Report tersely: no preamble or narration. Print the message in one fenced
block."""

CM_EDIT_LINE = "- For acme-billing, scope invoice-export changes `billing`."

CM_LESSONS = """# Lessons

Rules learned for the `cm` skill. Read before running; obey each line.

- Derive the commit type from the diff, never the branch name.
- For acme-billing, use the scope `billing` because PR #412 touched
  `export.go`.
- Never add a Co-Authored-By trailer.
"""

PLAN_BODY = """## Usage

```
/plan-smith <file>   write or update the plan in <file>
```

## Steps

1. Read the plan file, or start one.
2. Write numbered checkbox items.
3. Keep the status table in step: Y implemented, N not yet, X rejected.

## Status table

- One row per item, in item order.
- Update a row when its item's state changes.

## Output

Report tersely: no preamble or narration. Name the file written. Never paste
the plan back into chat."""

PLAN_LESSONS = """# Lessons

Rules learned for the `plan-smith` skill. Read before running; obey each line.

- Mark a rejected item X in the status table, never delete its row.
- Paste the whole plan back into chat after every update.
"""

STUB_LINT = """#!/usr/bin/env bash
mkdir -p tmp && date +%s%N > tmp/.ran-lint
echo "0 error(s), 0 warning(s)."
"""
STUB_ROUTINE = """#!/usr/bin/env bash
./dev/lint-skills.sh >/dev/null && date +%s%N > tmp/.ran-routine
echo "probes: all PASS"
echo "hunt: no splits"
echo 'eval-routine: lint ok; $0.12; 41s wall'
"""
# A new probe is red at the base and green on the result.
STUB_PROBE = """#!/usr/bin/env python3
import sys
red = "--against" in sys.argv
print(("   FAIL " if red else "   PASS ") + " ".join(sys.argv[1:]))
print("probes: $0.02, 9s")
"""

CM_LESSONS_FALLBACK = """# Lessons

- Keep the summary line under 50 chars.
- Prefer `refactor` over `chore` for code moves.
"""


def scaffold(committed, after=None):
    """committed: files in the initial commit; after: shell run after it."""
    out = ["#!/usr/bin/env bash", "set -euo pipefail", GIT_INIT.rstrip()]
    for i, (path, body) in enumerate(committed.items()):
        d = os.path.dirname(path)
        if d:
            out.append(f"mkdir -p {d}")
        if not body.endswith("\n"):
            body += "\n"
        out.append(f"cat > {path} <<'EOF_{i}'\n{body}EOF_{i}")
        if path.startswith("dev/"):
            out.append(f"chmod +x {path}")
    out += ["git add -A", "git commit -qm initial"]
    if after:
        out.append(after.rstrip())
    return "\n".join(out) + "\n"

# ---------------------------------------------------------------- writer


def write_case(name, prompt, graders, scaffold_sh, asp=""):
    name = PFX + name
    d = os.path.join(EVALS, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "graders"))
    fm = [f"tags: [case:{name}, {', '.join(TAGS)}]", "runs: 1",
          "max_turns: 60", "timeout_seconds: 300",
          f"allowed_tools: [{', '.join(TOOLS)}]",
          "append_system_prompt: |"]
    fm += ["  " + ln if ln else ""
           for ln in (ENGLISH + WIRING + asp).rstrip("\n").split("\n")]
    with open(os.path.join(d, "prompt.md"), "w") as f:
        f.write("---\n" + "\n".join(fm) + "\n---\n\n" + prompt + "\n")
    with open(os.path.join(d, "case.yaml"), "w") as f:
        f.write(f'schema_version: "1.1"\nname: {name}\ncontext:\n'
                "  scaffold_script: scaffold.sh\n")
    p = os.path.join(d, "scaffold.sh")
    with open(p, "w") as f:
        f.write(scaffold_sh)
    os.chmod(p, 0o755)
    for gname, body in graders.items():
        with open(os.path.join(d, "graders", gname + ".md"), "w") as f:
            f.write(body)


def answers(*lines):
    return "\n" + PERSONA + "\n" + "\n".join(
        f"{i}. {a}" for i, a in enumerate(lines, 1)) + "\n"

# ---------------------------------------------------------------- 1


def case_gate():
    cm = "craft/skills/cm"
    # The uncommitted edit: one task-specific line under "Summary line".
    edit = (f"sed -i 's/^- Scope: optional, short noun\\.$/&\\n{CM_EDIT_LINE}/' "
            f"{cm}/SKILL.md\n"
            f"grep -q 'acme-billing' {cm}/SKILL.md")
    write_case(
        "gate-lessons-and-edits", "/craft:fold-lessons",
        {
            "b1-lessons-unchanged": g_file(
                f"{cm}/LESSONS.md",
                r"diff, never the branch name[\s\S]*acme-billing[\s\S]*"
                r"Co-Authored-By"),
            "b1-edit-unreverted": g_file(f"{cm}/SKILL.md", r"acme-billing"),
            "b1-not-folded": g_file(f"{cm}/SKILL.md", r"branch name",
                                    absent=True),
            "b2-keep-branch-rule": g_regex(
                line_with(r"branch", r"\b(?:keep|generali[sz]e)"), flags="i"),
            "b3-drop-acme-lesson": g_regex(
                line_with(r"(?:PR #?412|export\.go|lesson \(?b\)?)",
                          r"\bdrop"), flags="i"),
            "b4-revert-acme-edit": g_regex(
                line_with(r"acme", r"\brevert"), flags="i"),
            "b5-carried": g_regex(
                line_with(r"co-authored-by",
                          r"\b(?:reword|merge|already carried)"), flags="i"),
        },
        scaffold({f"{cm}/SKILL.md": skill_md(
            "cm", "Writes git commit messages (Conventional Commits).",
            CM_BODY), f"{cm}/LESSONS.md": CM_LESSONS}, after=edit))

# ---------------------------------------------------------------- 2


def case_fold():
    ps = "craft/skills/plan-smith"
    write_case(
        "fold-hold-and-test", "/craft:fold-lessons plan-smith",
        {
            "b1-rule-folded": g_file(
                f"{ps}/SKILL.md",
                r"reject[^\n]*(?:\n[^\n]*)?\bX\b[\s\S]{0,300}?"
                r"(?:never|not|keep)[^\n]*(?:\n[^\n]*)?\b(?:delete|row)"
                r"|\bX\b[^\n]*(?:\n[^\n]*)?reject[\s\S]{0,300}?(?:delete|row)",
                flags="i"),
            "b1-body-kept": g_file(f"{ps}/SKILL.md",
                                   r"Never paste\s+the plan back"),
            "b2-held-line": g_file(f"{ps}/LESSONS.md",
                                   r"Paste the whole plan back"),
            "b2-folded-gone": g_file(f"{ps}/LESSONS.md", r"rejected item",
                                     absent=True),
            "b3-ran-lint": g_exists("tmp/.ran-lint", True),
            "b3-ran-routine": g_exists("tmp/.ran-routine", True),
            "b3-lint-first": g_regex(
                r'"command":"' + S + r'lint-skills\.sh[\s\S]*"command":"'
                + S + r'eval-routine\.sh', "trace"),
            "b4-held-asked": g_regex(
                line_with(r"paste", r"(?:held|hold|\?|decid|recommend)"),
                flags="i"),
        },
        scaffold({f"{ps}/SKILL.md": skill_md(
            "plan-smith", "Writes and tracks an implementation plan.",
            PLAN_BODY), f"{ps}/LESSONS.md": PLAN_LESSONS,
            "dev/lint-skills.sh": STUB_LINT,
            "dev/eval-routine.sh": STUB_ROUTINE,
            "dev/eval-probe.py": STUB_PROBE,
            ".gitignore": "tmp/\n"}),
        asp=answers("Approved as proposed; keep held items held."))

# ---------------------------------------------------------------- 3


def case_nothing():
    cm = "craft/skills/cm"
    write_case(
        "nothing-to-fold", "/craft:fold-lessons",
        {
            "b1-nothing": g_regex(
                r"nothing (?:is )?(?:to fold|in scope)|no (?:LESSONS\.md|lessons)",
                flags="i"),
            "b1-one-line": g_regex(r"\S[^\n]*(?:\n\s*)+\S[^\n]*(?:\n\s*)+\S",
                                   match="not_contains"),
            "b2-no-read": g_never("Read", "agent-data/ctx42-skills/lessons/craft/cm"),
            "b2-no-shell-read": g_never("Bash", "agent-data/ctx42-skills/lessons/craft/cm"),
        },
        scaffold({f"{cm}/SKILL.md": skill_md(
            "cm", "Writes git commit messages (Conventional Commits).",
            CM_BODY), ".gitignore": ".agent-data/\n"},
            after=("mkdir -p .agent-data/ctx42-skills/lessons/craft\n"
                   "cat > .agent-data/ctx42-skills/lessons/craft/cm.md "
                   "<<'EOF_X'\n" + CM_LESSONS_FALLBACK + "EOF_X")))


if __name__ == "__main__":
    case_gate()
    case_fold()
    case_nothing()
