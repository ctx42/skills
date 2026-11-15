#!/usr/bin/env python3
"""Generate craft/evals/work-all--* native eval cases. Re-runnable; owns only work-all--*."""
import glob
import os
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
EVALS = os.path.join(ROOT, "craft/evals")

ENGLISH = "The user writes English; reply in English.\n"

# JSON-string body of a Bash command in the trace / tool input.
S = r'(?:[^"\\]|\\.)*'
GIT_COMMIT = r"(?:\b|\\n)git\s+commit\b"
GIT_PUSH = r"(?:\b|\\n)git\s+push\b"
# One reflog line per commit that landed; the scaffold's `commit (initial)`
# does not match.
LANDED_COMMIT = r"\tcommit: "


def heredocs(files):
    out = []
    for i, (path, body) in enumerate(files.items()):
        d = os.path.dirname(path)
        if d:
            out.append(f"mkdir -p {d}")
        if not body.endswith("\n"):
            body += "\n"
        out.append(f"cat > {path} <<'EOF_{i}'\n{body}EOF_{i}")
    return "\n".join(out) + "\n"


def repo(path, files, go=False):
    """A git repo at path holding files, tmp/ ignored, committed clean."""
    files = dict(files)
    files[".gitignore"] = "tmp/\n"
    check = "go vet ./... && go test ./... >/dev/null\n" if go else ""
    return (f"mkdir -p {path}\n(\ncd {path}\ngit init -q\n"
            "git config user.email eval@example.com\ngit config user.name Eval\n"
            "git config commit.gpgsign false\n" + heredocs(files) + check
            + "git add -A\ngit commit -qm 'initial'\n)\n")


def scaffold(*parts):
    return "#!/usr/bin/env bash\nset -euo pipefail\n" + "".join(parts)


def yq(s):
    return "'" + s.replace("'", "''") + "'"


def g_regex(pattern, target="last_message", flags=None, match=None):
    fm = ["type: regex"]
    if isinstance(target, dict):
        fm += ["target:", "  source: file", f"  path: {target['path']}"]
    else:
        fm.append(f"target: {target}")
    if flags:
        fm.append(f'flags: "{flags}"')
    if match:
        fm.append(f"match: {match}")
    return "---\n" + "\n".join(fm) + "\n---\n" + pattern + "\n"


def g_tool(tool, input_match=None, min_=1, max_=None):
    fm = ["type: tool_used", f"tool: {tool}"]
    if input_match:
        fm.append(f"input_match: {yq(input_match)}")
    fm.append(f"min: {min_}")
    if max_ is not None:
        fm.append(f"max: {max_}")
        fm.append("arm: both")
    return "---\n" + "\n".join(fm) + "\n---\n"


def g_exists(path, exists=True):
    return ("---\ntype: file_exists\n" f"path: {path}\n"
            f"exists: {'true' if exists else 'false'}\n---\n")


def file_has(path, pattern, absent=False, flags=None):
    return g_regex(pattern, target={"path": path}, flags=flags,
                   match="not_contains" if absent else None)


# Nothing but the run file is written, nothing committed, no agent started.
BEFORE_ANSWER = {
    "no-edit": g_tool("Edit", r'"file_path":"(?![^"]*agent-run-)', 0, 0),
    "no-write": g_tool("Write", r'"file_path":"(?![^"]*agent-run-)', 0, 0),
    "no-commit": g_tool("Bash", GIT_COMMIT, 0, 0),
    "no-agent": g_tool("Agent", None, 0, 0),
}

SCRIPTED = """
Automated eval: the user is absent. Whenever the skill would stop and wait
for the user, take the next scripted answer below as the reply and continue
in this same run; never end the run to wait. If none fits, give the most
plausible answer and continue.

1. Skip nothing; run every unit and item as you propose.
2. For any other question, take your own recommendation.
"""

TOOLS = ("[Read, Glob, Grep, Skill, Edit, Write, Agent, SendMessage, Bash(git:*), "
         "Bash(go:*), Bash(gofmt:*), Bash(find:*), Bash(ls:*), Bash(mkdir:*), Bash(rm:*), "
         "Bash(nproc:*), Bash(uptime:*), Bash(free:*), Bash(systemd-run:*), "
         "Bash(command:*), Bash(date:*), Bash(exit:*)]")

TAGS = ["skill:work-all", "needs-shell", "sec:work-all:usage", "sec:work-all:work-files",
        "sec:work-all:1-discover", "sec:work-all:2-plan-and-ask-before-any-dispatch"]
RUN_TAGS = TAGS + ["fan-out", "long", "sec:work-all:3-dispatch",
                   "sec:work-all:4-while-workers-run", "sec:work-all:5-run-file",
                   "sec:work-all:6-report", "ref:work-all/worker"]

CASES = []


def case(name, scaffold_, graders, system=ENGLISH, tags=TAGS, long=False):
    CASES.append(dict(name=name, scaffold=scaffold_, graders=graders, system=system,
                      tags=tags, long=long))


def plan(title, items):
    """A plan-smith plan with every item N and the closing item last."""
    rows = items + [("Remove this plan", "When every other item is `Y` or `X`, ask "
                     "the user whether to delete this file.")]
    w = max(len("Item"), *(len(n) for n, _ in rows))
    head = [f"# {title}", "", "## Summary", "",
            f"| #  | {'Item'.ljust(w)} | Status |", f"|----|{'-' * (w + 2)}|--------|"]
    head += [f"| {str(i).ljust(2)} | {n.ljust(w)} | N      |" for i, (n, _) in enumerate(rows, 1)]
    head += ["", "Legend: Y implemented · N not yet · X rejected", ""]
    for i, (n, body) in enumerate(rows, 1):
        head += [f"## {i}. {n} — [ ]", "", body, ""]
    return "\n".join(head)


# 1 ------------------------------------------------------------------

UPFRONT = scaffold(
    heredocs({
        "CLAUDE.md": "# Local rules\n\n`mirror/` holds read-only clones kept for "
                     "reference: read them, never edit or work in them.\n",
        "notes/agent-feature-index.md": "# Feature: index\n\nWrite `index.md` in this "
                                        "folder listing every other `.md` file here.\n",
    }),
    repo("lib", {
        "go.mod": "module example.com/lib\n\ngo 1.22\n",
        "lib.go": "// Package lib holds shared helpers.\npackage lib\n",
        "tmp/agent/agent-plan-retry.md": plan("Retry helper", [
            ("Add Retry", "Add `Retry(n int, f func() error) error` that calls `f` up to "
             "`n` times until it returns nil.\n\nDone when: `TestRetry` passes.")]),
    }),
    repo("app", {
        "go.mod": "module example.com/app\n\ngo 1.22\n\nrequire example.com/lib v1.0.0\n",
        "app.go": "// Package app fetches documents.\npackage app\n",
        "tmp/agent/agent-handoff-retry.md": "# Handoff: retry in app\n\nGoal: wrap `fetch` "
            "in `lib.Retry`.\n\nIn progress: none.\n\nOpen items:\n\n- Wrap `fetch` in "
            "`lib.Retry` once `example.com/lib` ships `Retry`.\n\nVerify: `go test ./...`\n",
    }),
    repo("tools", {
        "go.mod": "module example.com/tools\n\ngo 1.22\n",
        "tools.go": "// Package tools holds small helpers.\npackage tools\n",
        "tmp/agent/agent-todo.md": "# Parked work\n\n- `Wait`: a test failed once on a loaded "
            "machine and passed on rerun. Waits for a second failure.\n- `Join` should "
            "drop empty parts. Waits for nothing; ready now.\n",
        "tmp/agent/agent-dept-docs.md": "# Docs debt\n\n## Open\n\nNone.\n",
        "tmp/agent/agent-readme-tools.md": "# README notes\n\n- Mention the install "
                                           "command.\n",
        "tmp/agent/agent-check-x.ts": "console.log('probe');\n",
    }),
    repo("mirror/old", {
        "README.md": "# old\n",
        "tmp/agent/agent-plan-old.md": plan("Old plan", [
            ("Rename Old", "Rename `Old` to `New`.\n\nDone when: `New` exists.")]),
    }),
)

NEAR = r"[^\n]{0,200}"
case("work-all--upfront-round-before-work", UPFRONT, {
    "b1-units-listed": g_regex(r"^(?=[\s\S]*\blib\b)(?=[\s\S]*\bapp\b)(?=[\s\S]*\btools\b)"),
    "b2-lib-before-app": g_regex(r"^(?:(?!\bapp\b)[\s\S])*\blib\b"),
    "b3-mirror-skipped": g_regex(r"mirror" + NEAR + r"(?:skip|read-only|forbid)|"
                                 r"(?:skip|read-only|forbid)" + NEAR + r"mirror", flags="i"),
    "b4-non-work-listed": g_regex(r"^(?=[\s\S]*agent-readme-tools)(?=[\s\S]*agent-check-x)"),
    "b5-second-failure-waiting": g_regex(r"second failure" + NEAR + r"wait|wait" + NEAR
                                         + r"second failure", flags="i"),
    "b6-notes-no-repo": g_regex(r"notes" + NEAR + r"(?:no[- ]repo|not a (?:git )?repo|"
                                r"outside|without (?:a )?(?:git )?repo|no commit|uncommitted)|"
                                r"(?:no[- ]repo|outside any|without (?:a )?(?:git )?repo)"
                                + NEAR + r"notes", flags="i"),
    **{f"b7-{k}": v for k, v in BEFORE_ANSWER.items()},
})


# 2 ------------------------------------------------------------------

CALC = """// Package calc does integer arithmetic.
package calc

// Div returns a divided by b.
func Div(a, b int) int {
	return a / b
}
"""

CALC_TEST = """package calc

import "testing"

func TestDiv(t *testing.T) {
	if have := Div(6, 3); have != 2 {
		t.Fatalf("have %d, want 2", have)
	}
}
"""

TEXT = """// Package text holds string helpers.
package text

import "strings"

// Trim removes leading and trailing spaces.
func Trim(s string) string {
	return strings.TrimSpace(s)
}
"""

TEXT_TEST = """package text

import "testing"

func TestTrim(t *testing.T) {
	if have := Trim("  a  "); have != "a" {
		t.Fatalf("have %q, want %q", have, "a")
	}
}
"""

TEXT_PLAN = plan("Text helpers", [
    ("Add Trim", "Add `Trim(s string) string` that removes leading and trailing "
     "spaces.\n\nDone when: `TestTrim` passes."),
    ("Add Upper", "Add `Upper(s string) string` returning `strings.ToUpper(s)`.\n\n"
     "Done when: `TestUpper` passes."),
])

CALC_REPO = repo("calc", {
    "go.mod": "module example.com/calc\n\ngo 1.22\n",
    "calc.go": CALC, "calc_test.go": CALC_TEST,
    "tmp/agent/agent-bug-div-zero.md": "# Bug: Div panics on zero\n\n`Div(1, 0)` panics "
        "with \"integer divide by zero\". Change `Div` to `func Div(a, b int) (int, error)` "
        "and return the exported `ErrDivZero` when `b` is 0. No other code calls `Div`.\n",
}, go=True)


def text_repo(plan_text):
    return repo("text", {
        "go.mod": "module example.com/text\n\ngo 1.22\n",
        "text.go": TEXT, "text_test.go": TEXT_TEST,
        "README.md": "# text\n\nHelpers to recieve and clean strings.\n",
        "tmp/agent/agent-plan-text.md": plan_text,
        "tmp/agent/agent-dept-docs.md": "# Docs debt\n\n## Open\n\n- `README.md` misspells "
            "\"receive\" as \"recieve\".\n\n## Notes, not debt\n\nNone.\n",
    }, go=True)


case("work-all--full-run-commits-and-reports",
     scaffold("mkdir -p tmp\ntouch tmp/.gitkeep\n", CALC_REPO, text_repo(TEXT_PLAN)), {
         "b1-calc-committed": g_regex(LANDED_COMMIT, target={"path": "calc/.git/logs/HEAD"}),
         "b1-calc-errdivzero": file_has("calc/calc.go", r"ErrDivZero"),
         "b2-calc-zero-test": file_has("calc/calc_test.go", r"ErrDivZero|Div\(\s*\w+\s*,\s*0\s*\)"),
         "b3-no-trim-commit": g_regex(LANDED_COMMIT + r"[^\n]*\btrim\b",
                                      target={"path": "text/.git/logs/HEAD"}, flags="i",
                                      match="not_contains"),
         "b4-upper": file_has("text/text.go", r"func Upper\("),
         "b5-readme-typo": file_has("text/README.md", r"recieve", absent=True),
         "b6-run-file": g_exists("tmp/agent/agent-run-cwd.md"),
         "b6-run-file-report": file_has("tmp/agent/agent-run-cwd.md", r"^## Report", flags="m"),
         "b6-run-file-no-shell": g_tool("Bash", r"agent-run-", 0, 0),
         "b7-count-line": g_regex(r"^\W*worked \d+ of \d+ items in \d+ commits? across 2 units"),
         "b8-no-push": g_tool("Bash", GIT_PUSH, 0, 0),
         "b9-bug-deleted": g_exists("calc/tmp/agent/agent-bug-div-zero.md", exists=False),
         "b9-dept-deleted": g_exists("text/tmp/agent/agent-dept-docs.md", exists=False),
         "b10-no-trailer-brief": g_tool("Agent", r"[Cc]o-[Aa]uthored", 0, 0),
         "b10-no-trailer-report": g_regex(r"co-authored", flags="i", match="not_contains"),
     }, system=ENGLISH + SCRIPTED, tags=RUN_TAGS, long=True)


# 3 ------------------------------------------------------------------

RESUME_PLAN = TEXT_PLAN.replace("| 1  | Add Trim         | N      |",
                                "| 1  | Add Trim         | Y      |"
                                ).replace("## 1. Add Trim — [ ]", "## 1. Add Trim — [x]")
assert RESUME_PLAN != TEXT_PLAN and "## 1. Add Trim — [x]" in RESUME_PLAN

RUN_FILE = """# work-all run: cwd

## Selection

- text: `tmp/agent/agent-plan-text.md` #1, #2; `tmp/agent/agent-dept-docs.md`
- calc: skipped by the user

## Answers

- Skip unit calc: yes.

## Order

1. text

## Status

| Unit | Item                     | Status | Commits |
|------|--------------------------|--------|---------|
| text | agent-plan-text.md #1    | done   | none    |
| text | agent-plan-text.md #2    | open   |         |
| text | agent-dept-docs.md       | open   |         |

## Budget

- 2026-11-01 10:00: 12 cores, load 0.5, 11 GB available; text cap 4 GB.
"""

case("work-all--resume-offered-from-run-file",
     scaffold(heredocs({"tmp/agent/agent-run-cwd.md": RUN_FILE}), CALC_REPO,
              text_repo(RESUME_PLAN)), {
         "b1-offers-resume": g_regex(r"^(?=[\s\S]*resum)(?=[\s\S]*agent-run-cwd)", flags="i"),
         "b2-no-calc-question": g_regex(r"\bcalc\b[^\n?]{0,160}\?", match="not_contains"),
         **{f"b3-{k}": v for k, v in BEFORE_ANSWER.items()},
     })


# ------------------------------------------------------------- write


def main():
    for d in glob.glob(os.path.join(EVALS, "work-all--*")):
        shutil.rmtree(d)
    for c in CASES:
        d = os.path.join(EVALS, c["name"])
        os.makedirs(os.path.join(d, "graders"))
        tags = [f"case:{c['name']}"] + list(dict.fromkeys(c["tags"]))
        sysp = "".join("  " + l + "\n" if l else "\n" for l in c["system"].rstrip("\n").split("\n"))
        limits = ("max_turns: 80\ntimeout_seconds: 600\n" if c["long"]
                  else "max_turns: 40\ntimeout_seconds: 300\n")
        with open(os.path.join(d, "prompt.md"), "w") as f:
            f.write("---\n"
                    f"tags: [{', '.join(tags)}]\n"
                    "runs: 1\n" + limits +
                    f"allowed_tools: {TOOLS}\n"
                    "append_system_prompt: |\n" + sysp +
                    "---\n\n/craft:work-all\n")
        with open(os.path.join(d, "case.yaml"), "w") as f:
            f.write(f'schema_version: "1.1"\nname: {c["name"]}\ncontext:\n'
                    "  scaffold_script: scaffold.sh\n")
        p = os.path.join(d, "scaffold.sh")
        with open(p, "w") as f:
            f.write(c["scaffold"])
        os.chmod(p, 0o755)
        for gname, body in c["graders"].items():
            with open(os.path.join(d, "graders", gname + ".md"), "w") as f:
                f.write(body)
    print(f"wrote {len(CASES)} cases")


main()
