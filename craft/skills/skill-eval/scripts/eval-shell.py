#!/usr/bin/env python3
"""Runs the needs-shell native cases without `claude plugin eval`.

`claude plugin eval` wraps every in-run command in a sandbox that nests a user
namespace inside bwrap's; stock Ubuntu refuses that, so every Bash call in a
case fails. This runner does the eval's job for those cases with a plain
`claude -p`, the way a user runs a skill: no OS sandbox, the case's
allowed_tools only, in a throwaway workspace. Called by eval-changed.

Per case: copy the plugin read-only to <tmp>/plugin, run scaffold.sh in
<tmp>/home/cwd with $HOME=<tmp>/home, then `claude -p` the prompt body there
(project setting sources only: no user hooks, CLAUDE.md, plugins, or MCP
servers; file edits under the real home refused), and grade the trace and
workspace. A case whose trace shows a file edit that reached the real home, or
a Bash call that names it, fails (eval_guard). Grader types: regex (targets
last_message, trace, {source: file, path}), tool_used, tool_order,
file_exists. Patterns are JavaScript regexes, as in `claude plugin eval`, read
through jsregex.

Usage:
  scripts/eval-shell.py <group> <case>... [--model M] [-j N]
       [--runs N] [--max-cost-usd N] [--json out.json] [--keep]

--runs runs each case N times (default 1); a case appears in the result only
once all its runs finished.

--model defaults to `default`, the CLI's default model: no --model reaches
`claude`.

EVAL_STRIP_NOTICE, when set, is a regex: a last paragraph of the reply that
matches it is dropped before grading (see eval_notice).

Writes the `claude plugin eval --json` result shape (cases[].arms.with[],
aggregates, costUsd), so eval-ledger.py records it unchanged. Exit 0 when
every case passes, 1 otherwise, 2 when --max-cost-usd stopped it.
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor

sys.dont_write_bytecode = True  # importing the helpers must not leave __pycache__ in the skill
import jsregex  # noqa: E402
from eval_guard import deny_home_edits, home_commands, home_writes  # noqa: E402
from eval_model import main_model  # noqa: E402
from eval_notice import strip_notice  # noqa: E402
from evalroot import ROOT  # noqa: E402

USAGE = ("usage: eval-shell.py <group> <case>... [--model M] [-j N] [--max-cost-usd N]"
         " [--json out] [--keep]")


def die(msg):
    print(f"eval-shell: {msg}", file=sys.stderr)
    sys.exit(1)


def parse_args(argv):
    opts = {"model": "default", "jobs": 1, "runs": 1, "max_usd": math.inf, "json": "", "keep": False}
    rest, i = [], 0
    while i < len(argv):
        a = argv[i]
        if a in ("--model", "-j", "--runs", "--max-cost-usd", "--json"):
            if i + 1 >= len(argv):
                die(USAGE)
            v = argv[i + 1]
            i += 1
            if a == "--model":
                opts["model"] = v
            elif a == "-j":
                opts["jobs"] = max(1, int(v))
            elif a == "--runs":
                opts["runs"] = max(1, int(v))
            elif a == "--max-cost-usd":
                opts["max_usd"] = float(v)
            else:
                opts["json"] = v
        elif a == "--keep":
            opts["keep"] = True
        else:
            rest.append(a)
        i += 1
    if len(rest) < 2:
        die(USAGE)
    return rest[0], rest[1:], opts


# --- Case files. ---

def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n?(.*)\Z", text, re.S)
    return (m.group(1), m.group(2)) if m else ("", text)


def scalar(v):
    """One YAML scalar: 'single' ('' escapes '), "double" (JSON escapes), or
    plain."""
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] == "'":
        return v[1:-1].replace("''", "'")
    if len(v) >= 2 and v[0] == v[-1] == '"':
        return json.loads(v)
    return v


def flow_map(v):
    """A flow map `{a: x, b: 'y, z'}`: split on commas outside quotes."""
    inner = v.strip()
    inner = inner[1:] if inner.startswith("{") else inner
    inner = inner[:-1] if inner.endswith("}") else inner
    out, key, buf, quote, in_key, i = {}, "", "", "", True, 0

    def flush():
        if key.strip():
            out[key.strip()] = scalar(buf)

    while i < len(inner):
        c = inner[i]
        if quote:
            buf += c
            if c == quote and not (quote == "'" and inner[i + 1:i + 2] == "'"):
                quote = ""
            elif c == quote or (quote == '"' and c == "\\"):
                i += 1
                buf += inner[i:i + 1]
        elif in_key and c == ":":
            in_key = False
        elif in_key:
            key += c
        elif c in "'\"":
            quote, buf = c, buf + c
        elif c == ",":
            flush()
            key, buf, in_key = "", "", True
        else:
            buf += c
        i += 1
    flush()
    return out


def fields(fm):
    """Top-level `key: value` lines of a grader or prompt front matter. A key
    with no value takes the indented `key: value` lines under it as a block
    map."""
    out, block = {}, None
    for line in fm.split("\n"):
        sub = block is not None and re.match(r"\s+([a-z_]+):\s*(.*)$", line)
        if sub:
            block[sub.group(1)] = scalar(sub.group(2))
            continue
        block = None
        m = re.match(r"([a-z_]+):\s*(.*)$", line)
        if not m:
            continue
        v = m.group(2).strip()
        if v == "":
            block = out[m.group(1)] = {}
        elif v.startswith("{"):
            out[m.group(1)] = flow_map(v)
        elif v.startswith("["):
            out[m.group(1)] = v
        else:
            out[m.group(1)] = scalar(v)
    return out


def number(v, default):
    try:
        n = float(v)
    except (TypeError, ValueError):
        return default
    return n if n else default


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_case(group, name):
    d = os.path.join(ROOT, group, "evals", name)
    pm = os.path.join(d, "prompt.md")
    if not os.path.isfile(pm):
        die(f"{group}/evals/{name}: no prompt.md")
    fm, body = frontmatter(read(pm))
    f = fields(fm)
    allowed = [t.strip() for t in str(f.get("allowed_tools") or "[]").strip("[]").split(",") if t.strip()]
    asp = re.search(r"^append_system_prompt:\s*\|[-+]?\n((?:[ \t]+.*\n?|\n)*)", fm, re.M)
    yml = os.path.join(d, "case.yaml")
    yaml = read(yml) if os.path.isfile(yml) else ""
    graders = []
    for g in sorted(x for x in os.listdir(os.path.join(d, "graders")) if x.endswith(".md")):
        gfm, gbody = frontmatter(read(os.path.join(d, "graders", g)))
        graders.append({"name": g[:-3], **fields(gfm), "pattern": gbody.strip()})
    scaffold = re.search(r"scaffold_script:\s*(\S+)", yaml)
    history = re.search(r"history_file:\s*(\S+)", yaml)
    return {
        "name": name, "dir": d, "prompt": body.strip(), "allowed": allowed, "graders": graders,
        "asp": re.sub(r"^ {2}", "", asp.group(1), flags=re.M).rstrip() if asp else "",
        "max_turns": int(number(f.get("max_turns"), 30)),
        "timeout": number(f.get("timeout_seconds"), 300),
        "scaffold": scaffold.group(1) if scaffold else None,
        "history": history.group(1) if history else None,
    }


# --- Grading. ---

def js_json(v):
    """JSON text as JavaScript's JSON.stringify writes it."""
    return json.dumps(v, separators=(",", ":"), ensure_ascii=False)


def glob_re(glob):
    out = []
    for p in re.split(r"(\*\*/?|\*|\?)", glob):
        out.append(".*" if p in ("**/", "**") else "[^/]*" if p == "*" else "[^/]" if p == "?" else re.escape(p))
    return re.compile("^" + "".join(out) + r"\Z")


def list_files(d, rel=""):
    out = []
    for e in sorted(os.scandir(os.path.join(d, rel)), key=lambda e: e.name):
        r = f"{rel}/{e.name}" if rel else e.name
        if e.is_dir(follow_symlinks=False):
            if e.name != ".git":
                out.extend(list_files(d, r))
        else:
            out.append(r)
    return out


def flags_of(g):
    return str(g.get("flags") or "").replace("g", "")


def grade(g, run):
    def ok(passed, evidence=""):
        return {"name": g["name"], "passed": passed, "evidence": evidence}

    def match_tool(spec):
        im = spec.get("input_match")
        r = jsregex.compile(im) if im else None
        return lambda u: u.get("name") == spec.get("tool") and (r is None or bool(r.search(js_json(u.get("input")))))

    try:
        t = g.get("type")
        if t == "regex":
            target = g.get("target")
            if target == "last_message":
                text = run["last_message"]
            elif target == "trace":
                text = run["trace"]
            elif isinstance(target, dict) and target.get("source") == "file":
                p = os.path.join(run["cwd"], target.get("path", ""))
                if not os.path.isfile(p):
                    return ok(False, f"file {target.get('path')} missing")
                text = read(p)
            else:
                return ok(False, f"unsupported regex target {js_json(target)}")
            n = sum(1 for _ in jsregex.compile(g["pattern"], flags_of(g)).finditer(text))
            match = g.get("match") or "contains"
            if match == "contains":
                return ok(n > 0, "" if n else "no match")
            if match == "not_contains":
                return ok(n == 0, f"{n} match(es)" if n else "")
            want = re.fullmatch(r"count:(\d+)", match)
            if want:
                return ok(n == int(want.group(1)), f"{n} match(es), want {want.group(1)}")
            return ok(False, f"unsupported match {match}")
        if t == "tool_used":
            n = sum(1 for u in run["tool_uses"] if match_tool(g)(u))
            lo = int(g["min"]) if g.get("min") is not None else 1
            hi = int(g["max"]) if g.get("max") is not None else math.inf
            hi_s = "Infinity" if hi == math.inf else hi
            return ok(lo <= n <= hi, f"{g.get('tool')} used {n} time(s), want {lo}..{hi_s}")
        if t == "tool_order":
            uses = run["tool_uses"]
            b = next((i for i, u in enumerate(uses) if match_tool(g["before"])(u)), -1)
            a = next((i for i, u in enumerate(uses) if match_tool(g["after"])(u)), -1)
            if b < 0 or a < 0:
                return ok(False, f"{'before' if b < 0 else 'after'} call missing")
            return ok(b < a, "" if b < a else "after call came first")
        if t == "file_exists":
            # Only files the run created count, never scaffold-made ones.
            r = glob_re(g.get("path", ""))
            made = [f for f in list_files(run["cwd"]) if r.search(f) and f not in run["scaffolded"]]
            want = str(g.get("exists")).lower() != "false"
            return ok(want == bool(made), ", ".join(made) if made else f"no {g.get('path')}")
        return ok(False, f"unsupported grader type {t}")
    except Exception as e:  # noqa: BLE001 - a broken grader fails its case, never the run
        return ok(False, f"grader error: {e}")


# --- Running one case. ---

CONFIG_DIR = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")
REAL_HOME = os.path.expanduser("~")  # every case runs with $HOME pointed elsewhere


def goproxy():
    if os.environ.get("GOPROXY"):
        return os.environ["GOPROXY"]
    r = subprocess.run(["go", "env", "GOMODCACHE"], capture_output=True, text=True)
    return f"file://{r.stdout.strip()}/cache/download"


def project_dir(cwd):
    return os.path.join(CONFIG_DIR, "projects", re.sub(r"[^A-Za-z0-9]", "-", cwd))


def unseal(d):
    subprocess.run(["chmod", "-R", "u+rwx", d], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def parse_trace(text):
    events, tool_uses, last, final = [], [], "", None
    for line in text.split("\n"):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if not isinstance(e, dict):
            continue
        events.append(e)
        if e.get("type") == "assistant":
            parts = []
            for b in (e.get("message") or {}).get("content") or []:
                if b.get("type") == "tool_use":
                    tool_uses.append(b)
                if b.get("type") == "text" and b.get("text"):
                    parts.append(b["text"])
            if parts and not e.get("parent_tool_use_id"):
                last = "\n".join(parts)
        elif e.get("type") == "result":
            final = e
    return events, tool_uses, last, final


def without_wire(text):
    """Return the trace without the `wire_*` fields newer CLIs add to
    assistant events: they repeat each tool input, so a trace pattern would
    count it twice."""
    lines = []
    for line in text.split("\n"):
        try:
            e = json.loads(line)
        except ValueError:
            lines.append(line)
            continue
        keys = [k for k in e if k.startswith("wire_")] if isinstance(e, dict) else []
        if not keys:
            lines.append(line)
            continue
        for k in keys:
            del e[k]
        lines.append(js_json(e))
    return "\n".join(lines)


def run_case(group, c, opts, proxy):
    started = time.time()
    tmp = tempfile.mkdtemp(prefix="claude-eval-sh-")
    home, out, plugin = os.path.join(tmp, "home"), os.path.join(tmp, "out"), os.path.join(tmp, "plugin")
    cwd = os.path.join(home, "cwd")
    os.makedirs(cwd)
    os.makedirs(out)
    # The plugin is read-only in runs: a stray edit must never reach the repo.
    src = os.path.join(ROOT, group)
    shutil.copytree(src, plugin, ignore=lambda d, names: ["evals"] if d == src else [])
    subprocess.run(["chmod", "-R", "a-w", plugin])
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE" and not k.startswith("CLAUDE_CODE_")}
    env.update(HOME=home, GOPROXY=proxy, GOTOOLCHAIN="local", GOFLAGS="", CLAUDE_CONFIG_DIR=CONFIG_DIR)

    result = {"passed": False, "error": None, "graders": [], "durationSeconds": 0, "costUsd": 0,
              "model": None, "tracePath": os.path.join(out, "trace.jsonl")}
    try:
        if c["scaffold"]:
            s = subprocess.run(["bash", os.path.join(c["dir"], c["scaffold"])], cwd=cwd, env=env,
                               capture_output=True, text=True)
            if s.returncode != 0:
                tail = " | ".join((s.stderr or s.stdout).strip().split("\n")[-3:])
                raise RuntimeError(f"scaffold failed: {tail}")
        scaffolded = set(list_files(cwd))

        args = ["claude", "-p", c["prompt"], "--plugin-dir", plugin, "--max-turns", str(c["max_turns"]),
                "--setting-sources", "project", "--strict-mcp-config",
                "--output-format", "stream-json", "--verbose"]
        if opts["model"] != "default":
            args += ["--model", opts["model"]]
        if c["allowed"]:
            args += ["--allowedTools", *c["allowed"]]
        args += deny_home_edits(REAL_HOME, tmp)
        if c["asp"]:
            args += ["--append-system-prompt", c["asp"]]
        if c["history"]:
            # Resume a recorded session: it must sit in this workspace's project dir.
            hist = read(os.path.join(c["dir"], c["history"]))
            session = json.loads(hist.split("\n")[0])["sessionId"]
            os.makedirs(project_dir(cwd), exist_ok=True)
            with open(os.path.join(project_dir(cwd), f"{session}.jsonl"), "w") as f:
                f.write(hist)
            args += ["--resume", session]
        else:
            args.append("--no-session-persistence")

        with open(result["tracePath"], "w") as trace:
            p = subprocess.Popen(args, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=trace,
                                 stderr=subprocess.PIPE, text=True)
            try:
                _, err = p.communicate(timeout=c["timeout"])
            except subprocess.TimeoutExpired:
                result["error"] = f"timeout after {c['timeout']:g}s"
                p.terminate()
                _, err = p.communicate()
        code = p.returncode
        if code and not result["error"] and err.strip():
            result["error"] = " | ".join(err.strip().split("\n")[-2:])

        text = read(result["tracePath"])
        events, tool_uses, last, final = parse_trace(text)
        if final:
            result["costUsd"] = final.get("total_cost_usd") or 0
            result["model"] = main_model(final.get("modelUsage"))
            if final.get("result"):
                last = final["result"]
            # A run cut off by the usage limit says nothing about the skill.
            if final.get("is_error") and re.search("limit", str(final.get("result") or ""), re.I):
                result["error"] = f"usage limit: {final['result']}"
        elif not result["error"]:
            result["error"] = f"claude exited {code} without a result"
        result["lastMessage"] = last

        run = {"cwd": cwd, "trace": without_wire(text), "tool_uses": tool_uses, "scaffolded": scaffolded,
               "last_message": strip_notice(last, os.environ.get("EVAL_STRIP_NOTICE"))}
        result["graders"] = [grade(g, run) for g in c["graders"]]
        leaked = home_writes(events, REAL_HOME, tmp)
        if leaked:
            result["graders"].append({"name": "no-real-home-write", "passed": False,
                                      "evidence": f"wrote into the real home: {', '.join(leaked)}"})
        named = home_commands(events, REAL_HOME)
        if named:
            result["graders"].append({"name": "no-real-home-command", "passed": False,
                                      "evidence": f"ran Bash on the real home: {' | '.join(named)}"})
        result["passed"] = not result["error"] and all(g["passed"] for g in result["graders"])
    except Exception as e:  # noqa: BLE001 - a broken case fails, the others still run
        result["error"] = result["error"] or str(e)
    finally:
        # Claude records every workspace under its config dir; drop ours.
        shutil.rmtree(project_dir(cwd), ignore_errors=True)
        result["durationSeconds"] = round(time.time() - started)
        if not opts["keep"]:
            # The trace outlives the workspace only on failure (eval-changed keeps it).
            unseal(tmp)
            for d in (home, plugin):
                shutil.rmtree(d, ignore_errors=True)
            if result["passed"]:
                shutil.rmtree(tmp, ignore_errors=True)
        else:
            unseal(plugin)
    return result


def main():
    group, names, opts = parse_args(sys.argv[1:])
    if not os.path.isfile(os.path.join(ROOT, group, ".claude-plugin", "plugin.json")):
        die(f"{group}: not a plugin group")
    loaded = [load_case(group, n) for n in names]
    proxy = goproxy()
    arms = [[] for _ in loaded]
    tasks = [i for i in range(len(loaded)) for _ in range(opts["runs"])]
    state = {"spent": 0.0, "next": 0, "capped": False}
    lock = threading.Lock()
    t0 = time.time()

    def worker():
        # A pool of -j runs, stopping launches at the cost ceiling.
        while True:
            with lock:
                if state["next"] >= len(tasks):
                    return
                if state["spent"] >= opts["max_usd"]:
                    state["capped"] = True
                    return
                i = tasks[state["next"]]
                state["next"] += 1
            c = loaded[i]
            print(f"eval-shell: {c['name']} started ({time.strftime('%H:%M')})", file=sys.stderr, flush=True)
            r = run_case(group, c, opts, proxy)
            with lock:
                state["spent"] += r["costUsd"]
                arms[i].append(r)
            verdict = "PASS" if r["passed"] else f"FAIL, trace {r['tracePath']}"
            print(f"eval-shell: {c['name']} {verdict} ({r['durationSeconds']}s, ${r['costUsd']:.2f})",
                  file=sys.stderr, flush=True)

    with ThreadPoolExecutor(max_workers=max(1, min(opts["jobs"], len(tasks)))) as pool:
        for f in [pool.submit(worker) for _ in range(min(opts["jobs"], len(tasks)))]:
            f.result()

    # A case counts only once every run of it finished.
    done = [{"name": c["name"], "arms": {"with": arms[i]}}
            for i, c in enumerate(loaded) if len(arms[i]) == opts["runs"]]
    passed = sum(1 for c in done if all(r["passed"] for r in c["arms"]["with"]))
    agg = {"cases": done, "aggregates": {"casesPassed": passed, "casesTotal": len(done)},
           "durationSeconds": round(time.time() - t0), "costUsd": state["spent"]}
    text = json.dumps(agg, indent=1, ensure_ascii=False)
    if opts["json"]:
        with open(opts["json"], "w") as f:
            f.write(text)
    else:
        print(text)
    return 2 if state["capped"] else 0 if passed == len(loaded) else 1


if __name__ == "__main__":
    sys.exit(main())
