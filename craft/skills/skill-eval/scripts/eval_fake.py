"""Test fixtures for the agent-run eval scripts: a throwaway skills repo, a
fake `claude`, and a copy of the scripts with lint stubbed out.

Used by eval_ledger_test.py and eval_changed_test.py; nothing here runs a
real model or needs a network.

The fake `claude` answers `claude plugin eval` with the result JSON
eval-changed.sh reads, and `claude -p` (as eval-shell.mjs calls it) with a
stream-json trace. Each case's outcome comes from a JSON plan file named by
$FAKE_CLAUDE_PLAN: {"<case>": {"result": "pass"|"fail"|"limit", "cost": N}},
or "results": [...] for one outcome per run (the last repeats); a
`claude -p` case with "write": "<path>" first plays a Write call to that path,
refused when "write_error" is true, and one with "bash": "<command>" plays a
Bash call that succeeds.
Every run reports its --model, else $FAKE_CLAUDE_DEFAULT_MODEL (default
claude-default-1), as the costliest model of its modelUsage; a case run
reports $FAKE_CLAUDE_RUN_MODEL instead when that is set (a model fallback).
`claude -p --output-format json` without a case is the model probe: one
result object, or a usage-limit error when $FAKE_CLAUDE_PROBE is "limit";
a case not in the plan passes at $0.50. Like the real one, a `plugin eval`
call checks its --max-cost-usd before each case, leaves out the cases it
did not start, and exits 2 once its spend passes the ceiling. Every call's argv is appended, one JSON list per line, to
$FAKE_CLAUDE_LOG.
"""
import json
import os
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
GROUP = "grp"
SKILL = "s1"

FAKE_CLAUDE = r'''#!/usr/bin/env python3
import json, os, sys, tempfile

args = sys.argv[1:]
with open(os.environ["FAKE_CLAUDE_LOG"], "a") as f:
    f.write(json.dumps(args) + "\n")
plan_path = os.environ.get("FAKE_CLAUDE_PLAN", "")
plan = json.load(open(plan_path)) if plan_path and os.path.exists(plan_path) else {}


def used_model():
    if "--model" in args:
        return args[args.index("--model") + 1]
    return os.environ.get("FAKE_CLAUDE_DEFAULT_MODEL", "claude-default-1")


def outcome(case, run=0):
    o = plan.get(case, {})
    seq = o.get("results") or [o.get("result", "pass")]
    return seq[min(run, len(seq) - 1)], o.get("cost", 0.5)


if args[:2] == ["plugin", "eval"]:
    cases = [args[i + 1].split(":", 1)[1] for i, a in enumerate(args) if a == "--tag"]
    model = os.environ.get("FAKE_CLAUDE_RUN_MODEL") or used_model()
    out = args[args.index("--json") + 1]
    cap = float(args[args.index("--max-cost-usd") + 1]) if "--max-cost-usd" in args else None
    runs = int(args[args.index("--runs") + 1]) if "--runs" in args else 1
    res, spent, bad, capped = [], 0.0, 0, False
    for c in cases:
        if cap is not None and spent >= cap:
            capped = True
            continue
        arm = []
        for i in range(runs):
            kind, cost = outcome(c, i)
            tmp = tempfile.mkdtemp(prefix="claude-eval-fake-")
            os.makedirs(os.path.join(tmp, "out"))
            trace = os.path.join(tmp, "out", "trace.jsonl")
            reply = "OK" if kind == "pass" else "NO"
            with open(trace, "w") as f:
                f.write(json.dumps({"type": "result", "result": reply,
                                    "modelUsage": {model: {"costUSD": cost}}}) + "\n")
            passed = kind == "pass"
            spent += cost
            arm.append({
                "passed": passed,
                "error": "usage limit reached" if kind == "limit" else None,
                "graders": [] if passed else [{"name": "g1", "passed": False, "evidence": "no match"}],
                "durationSeconds": 1, "costUsd": cost, "tracePath": trace, "lastMessage": reply})
        bad += not all(r["passed"] for r in arm)
        res.append({"name": c, "arms": {"with": arm}})
    with open(out, "w") as f:
        json.dump({"cases": res, "aggregates": {"casesPassed": len(res) - bad, "casesTotal": len(res)},
                   "durationSeconds": 1, "costUsd": spent}, f)
    if capped or (cap is not None and spent > cap):
        sys.exit(2)
    sys.exit(1 if bad else 0)

if "-p" in args:
    prompt = args[args.index("-p") + 1]
    case = prompt.split("CASE:", 1)[1].split()[0] if "CASE:" in prompt else ""
    # This call is already in the log: earlier calls for the case set its run.
    with open(os.environ["FAKE_CLAUDE_LOG"]) as f:
        seen = sum(1 for line in f if case and f"CASE:{case}" in line)
    kind, cost = outcome(case, max(seen - 1, 0))
    model = used_model()
    if case and os.environ.get("FAKE_CLAUDE_RUN_MODEL"):
        model = os.environ["FAKE_CLAUDE_RUN_MODEL"]
    usage = {model: {"costUSD": cost}, "claude-helper-1": {"costUSD": 0.001}}
    if "--output-format" in args and args[args.index("--output-format") + 1] == "json":
        if os.environ.get("FAKE_CLAUDE_PROBE") == "limit":
            print(json.dumps({"type": "result", "is_error": True, "result": "You've hit your usage limit"}))
        else:
            print(json.dumps({"type": "result", "result": "OK", "total_cost_usd": 0.02, "modelUsage": usage}))
        sys.exit(0)
    if kind == "limit":
        print(json.dumps({"type": "result", "is_error": True,
                          "result": "You've hit your usage limit", "total_cost_usd": 0}))
    else:
        reply = "OK" if kind == "pass" else "NO"
        if plan.get(case, {}).get("write"):
            print(json.dumps({"type": "assistant", "message": {"model": model, "content": [
                {"type": "tool_use", "id": "w1", "name": "Write",
                 "input": {"file_path": plan[case]["write"], "content": "x"}}]}}))
            print(json.dumps({"type": "user", "message": {"content": [
                {"type": "tool_result", "tool_use_id": "w1",
                 "is_error": bool(plan[case].get("write_error"))}]}}))
        if plan.get(case, {}).get("bash"):
            print(json.dumps({"type": "assistant", "message": {"model": model, "content": [
                {"type": "tool_use", "id": "b1", "name": "Bash",
                 "input": {"command": plan[case]["bash"]}}]}}))
            print(json.dumps({"type": "user", "message": {"content": [
                {"type": "tool_result", "tool_use_id": "b1", "is_error": False}]}}))
        print(json.dumps({"type": "assistant", "message": {"model": model,
                          "content": [{"type": "text", "text": reply}]}}))
        print(json.dumps({"type": "result", "result": reply, "total_cost_usd": cost, "modelUsage": usage}))
    sys.exit(0)

sys.exit(2)
'''


def write(path, text, mode=None):
    """Write text to path, creating parent directories; chmod when mode is set."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)
    if mode is not None:
        os.chmod(path, mode)


def make_repo(root, cases):
    """Build a git repo at root with one group, one skill, and the given cases.

    cases is a list of (name, shell) or (name, shell, fanout) tuples; a shell
    case is tagged needs-shell, a fan-out case fan-out. Every case tags the
    skill and its Alpha section, and has one grader that wants the reply to
    start with OK.
    """
    write(os.path.join(root, GROUP, ".claude-plugin", "plugin.json"), '{"name": "grp"}\n')
    write(os.path.join(root, GROUP, "skills", SKILL, "SKILL.md"),
          "---\nname: s1\ndescription: Test skill.\n---\n\n# s1\n\n## Usage\n\nUse it.\n\n"
          "## Alpha\n\nFirst.\n\n## Beta\n\nSecond.\n")
    for c in cases:
        add_case(root, *c)
    write(os.path.join(root, ".gitignore"), "/tmp/\n")
    git = ["git", "-C", root, "-c", "user.name=t", "-c", "user.email=t@example.com"]
    subprocess.run(["git", "init", "-q", root], check=True)
    subprocess.run(git + ["add", "-A"], check=True)
    subprocess.run(git + ["commit", "-q", "-m", "init"], check=True)


def add_case(root, name, shell=False, fanout=False):
    """Write one case directory: prompt.md with tags, and a reply grader."""
    tags = (f"case:{name}, skill:{SKILL}, sec:{SKILL}:alpha" + (", needs-shell" if shell else "")
            + (", fan-out" if fanout else ""))
    allowed = "[Read, Bash(git:*)]" if shell else "[Read]"
    write(os.path.join(root, GROUP, "evals", name, "prompt.md"),
          f"---\ntags: [{tags}]\nallowed_tools: {allowed}\nmax_turns: 5\n---\n\nCASE:{name}\n")
    write(os.path.join(root, GROUP, "evals", name, "graders", "g1.md"),
          "---\ntype: regex\ntarget: last_message\n---\n^OK\n")


def make_bin(bindir, modcache):
    """Install the fake `claude`, plus `go` and `gofmt` stubs, in bindir.

    `go env GOMODCACHE` prints modcache; everything else exits 0.
    """
    write(os.path.join(bindir, "claude"), FAKE_CLAUDE, 0o755)
    write(os.path.join(bindir, "go"),
          f'#!/bin/sh\n[ "$1 $2" = "env GOMODCACHE" ] && echo "{modcache}"\nexit 0\n', 0o755)
    write(os.path.join(bindir, "gofmt"), "#!/bin/sh\nexit 0\n", 0o755)


def copy_scripts(dst):
    """Copy the eval scripts to dst with lint-skills.sh stubbed to pass.

    eval-changed.sh lints the repo under test first; the fake repo is not a
    lint-clean skills repo, and lint has its own checks.
    """
    shutil.copytree(HERE, dst, ignore=shutil.ignore_patterns("__pycache__", "*_test.py", "*.test.mjs"))
    write(os.path.join(dst, "lint-skills.sh"), "#!/bin/sh\nexit 0\n", 0o755)
    return dst


def env_for(base, root, bindir, plan, log):
    """Return the environment for one scripted run against the fake repo.

    Workspaces, the Claude config dir, and the fake's log all stay under base.
    """
    env = dict(os.environ)
    for k in list(env):
        if k == "CLAUDECODE" or k.startswith("CLAUDE_CODE_"):
            del env[k]
    tmpdir = os.path.join(base, "t")
    os.makedirs(tmpdir, exist_ok=True)
    env.update({
        "PATH": bindir + os.pathsep + env.get("PATH", ""),
        "SKILL_EVAL_ROOT": root,
        "TMPDIR": tmpdir,
        "CLAUDE_CONFIG_DIR": os.path.join(base, "config"),
        "FAKE_CLAUDE_PLAN": plan,
        "FAKE_CLAUDE_LOG": log,
        "PYTHONDONTWRITEBYTECODE": "1",
    })
    return env


def calls(log):
    """Return the fake `claude` calls logged so far, as argv lists."""
    if not os.path.exists(log):
        return []
    with open(log) as f:
        return [json.loads(line) for line in f if line.strip()]
