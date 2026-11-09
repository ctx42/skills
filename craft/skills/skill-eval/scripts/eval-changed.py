#!/usr/bin/env python3
"""eval-changed.py: manual audit, runs the agent-run native eval cases.

Not the routine check. After a skill edit run scripts/eval-check.py (free,
seconds) and scripts/eval-probe.py (cents, under a minute). Each case here is
a full agent session, up to minutes (Opus, measured 2026-10-04: $0.25-0.80 a
case, $3-9 a fan-out case); run them only when asked.
Without --audit, --skill, --case, or --all the script only lists what a
change reaches and runs nothing.

Maps the working-tree diff (or --base REF..) to tags and runs
`claude plugin eval` once per plugin group with those tags (tags OR):

  <group>/skills/<skill>/SKILL.md  changed line under `## X` -> sec:<skill>:<x>
                                   changed line above the first `## ` -> skill:<skill>
  <group>/skills/<skill>/references/<r>.md                    -> ref:<skill>/<r>
  <group>/skills/<skill>/{LESSONS.md,assets/*,evals/*}         -> skill:<skill>
  <group>/evals/<case>/**                                     -> case:<case>
  <group>/evals/mocks/**                                      -> every case of the group

A case lists every tag it exercises in its prompt.md front matter
(`--list-tags <group>/<skill>` prints the section and reference tags).
Native cases live in <group>/evals/<case>/; see references/native-cases.md.

Usage:
  scripts/eval-changed.py                 list cases reached by uncommitted changes
  scripts/eval-changed.py --audit         ... and run them
  scripts/eval-changed.py --base HEAD~3   ... by changes since HEAD~3
  scripts/eval-changed.py --path srd/skills/edit   ... only changes under a path
  scripts/eval-changed.py --skill srd/edit [--skill go/review]   whole skills
  scripts/eval-changed.py --case srd 'edit--*' [--case srd 'review--x']  case globs
  scripts/eval-changed.py --all srd       every case of a group
  scripts/eval-changed.py --list-tags srd/edit
  scripts/eval-changed.py --clean        delete leftover /tmp/claude-eval-* workspaces
  -j N   concurrent runs (1-8, default 2: more burns the 5-hour usage
         window faster); --dry-run prints, runs nothing
  --max-usd N  stop once this invocation has spent N dollars (default: no
         ceiling), naming each case it did not start
  --model M  run the cases on model M (default: the CLI's default model,
         also spelled `default`). Sonnet runs only when passed here, and its
         verdicts are recorded as they are, never re-run on another model.
         A run resolves M to a model ID first, with one short `claude -p`
         probe (cents); the ID keys the ledger and goes to both runners. A
         run that reports another model records nothing
  --keep keeps every run's workspace and trace (paths in the JSON); without
         it the workspaces are deleted after the run
  --fresh  ignore the pass ledger: a case whose inputs (case dir, the skills
         it tags, the group's mocks and fixtures, the model) are unchanged
         since it last passed is otherwise skipped (tmp/eval-ledger.json)

A case whose dir changed since its last verdict, or that has none and is new
or changed against the base, runs twice and passes only when both runs pass.

Cases run in chunks of 2 x -j, one `claude plugin eval` call each; passes
reach the ledger after every chunk. The first usage-limit cut-off stops the
run with exit 3: re-run the same command after the reset to resume.

Each failed case leaves its trace in <results>/<group>/failed/<case>.trace.jsonl
and its last message is printed, so a failure needs no re-run to diagnose.

Every run first checks the machine (git, node, go, gofmt) and stops with the
fix if one is missing. Only cases tagged needs-shell get Bash; they run
through eval-shell.py (plain `claude -p`, no OS sandbox), the rest through
`claude plugin eval`.

Each group line is followed by `flaky: <case> (<f> of <n> failed), ...` when
a selected case's last runs at its current inputs both passed and failed.

A run whose results dir and every claude-eval-* workspace have had no write
for $EVAL_STALL_SECONDS (default 600) is stopped: the process tree goes to
<results>/stall-ps.txt, the runner is killed, and the run exits 1.

Private settings of this clone go in the git-ignored tmp/eval.env, read at
start as `KEY=value` lines (shell quoting, `export`, and # comments allowed):
e.g. EVAL_STRIP_NOTICE='<regex>' for an account notice.

Exit: 0 all selected cases pass, 1 a case failed or nothing could run,
3 the usage limit stopped the run.
"""
import glob
import importlib.util
import json
import math
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True  # importing the helpers must not leave __pycache__ in the skill
from evalroot import ROOT  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("eval_recent", os.path.join(HERE, "eval-recent.py"))
eval_recent = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(eval_recent)

KINDS = ("plain", "plain2", "shell", "shell2", "plainfan", "plainfan2", "shellfan", "shellfan2")
UUID_JSONL = re.compile(r"/[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}\.jsonl$")


def die(msg):
    print(f"eval-changed: {msg}", file=sys.stderr, flush=True)
    sys.exit(1)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def git(*args):
    """Return the stdout lines of a git command run in the repo."""
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.stdout.splitlines()


def load_env_file(path):
    """Export the KEY=value lines of a private settings file."""
    if not os.path.isfile(path):
        return
    with open(path) as f:
        for line in f:
            words = shlex.split(line, comments=True)
            if words[:1] == ["export"]:
                words = words[1:]
            for w in words:
                k, sep, v = w.partition("=")
                if sep and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", k):
                    os.environ[k] = v


def list_tags(target):
    group, _, skill_rel = target.partition("/")
    d = os.path.join(ROOT, group, "skills", skill_rel)
    skill = os.path.basename(d.rstrip("/"))
    md = os.path.join(d, "SKILL.md")
    if not os.path.isfile(md):
        die(f"no SKILL.md in {d}")
    print(f"skill:{skill}")
    with open(md) as f:
        for line in f:
            if line.startswith("## "):
                print(f"sec:{skill}:{slug(line[3:].strip())}")
    for r in sorted(glob.glob(os.path.join(d, "references", "*.md"))):
        print(f"ref:{skill}/{os.path.basename(r)[:-3]}")


def clean():
    """Delete leftover workspaces; runs seal parts of them read-only."""
    for d in glob.glob(os.path.join(os.environ.get("TMPDIR", "/tmp"), "claude-eval-*/")):
        subprocess.run(["chmod", "-R", "u+rwx", d], stderr=subprocess.DEVNULL)
        shutil.rmtree(d, ignore_errors=True)


def parse_args(argv):
    o = {"base": "", "paths": [], "skills": [], "all": [], "cases": [], "jobs": "2", "max_usd": "",
         "model": "", "dry": False, "audit": False, "keep": False, "fresh": False}
    i = 0
    while i < len(argv):
        a = argv[i]
        need = {"--base": 1, "--path": 1, "--skill": 1, "--all": 1, "--case": 2, "--list-tags": 1,
                "-j": 1, "--max-usd": 1, "--model": 1}.get(a, 0)
        if i + need >= len(argv) and need:
            die(f"{a} needs {need} value(s) (see --help)")
        v = argv[i + 1:i + 1 + need]
        if a == "--base":
            o["base"] = v[0]
        elif a == "--path":
            o["paths"].append(v[0])
        elif a == "--skill":
            o["skills"].append(v[0])
        elif a == "--all":
            o["all"].append(v[0])
        elif a == "--case":
            o["cases"].append((v[0], v[1]))
        elif a == "--list-tags":
            list_tags(v[0])
            sys.exit(0)
        elif a == "--clean":
            clean()
            sys.exit(0)
        elif a == "-j":
            o["jobs"] = v[0]
        elif a == "--max-usd":
            o["max_usd"] = v[0]
        elif a == "--model":
            o["model"] = "" if v[0] == "default" else v[0]
        elif a == "--dry-run":
            o["dry"] = True
        elif a == "--audit":
            o["audit"] = True
        elif a == "--keep":
            o["keep"] = True
        elif a == "--fresh":
            o["fresh"] = True
        elif a in ("-h", "--help"):
            print(__doc__.split("\n\nUsage:")[0] + "\n\nUsage:" + __doc__.split("\n\nUsage:")[1])
            sys.exit(0)
        else:
            die(f"unknown argument: {a} (see --help)")
        i += 1 + need
    return o


def preflight():
    """Check that the machine can run what the cases need, every run: a case
    whose tools fail can still pass on what it reads, hiding the gap."""
    missing = [t for t in ("git", "node", "go", "gofmt") if not shutil.which(t)]
    if missing:
        die(f"preflight: not on PATH: {' '.join(missing)}")
    # Runs get a fresh $HOME and no network, so Go fixtures resolve their
    # dependencies from this machine's module cache (served as GOPROXY);
    # every module a fixture pins in its go.sum must already be there.
    cache = subprocess.run(["go", "env", "GOMODCACHE"], capture_output=True, text=True).stdout.strip()
    pins = set()
    for f in glob.glob(os.path.join(ROOT, "*", "evals", "*", "scaffold.sh")):
        with open(f, errors="replace") as fh:
            for line in fh:
                m = re.match(r"\s*([a-z0-9.-]+\.[a-z]+/[^ ]+) (v[^ /]+) h1:", line)
                if m:
                    pins.add((m.group(1), m.group(2)))
    absent = []
    for mod, ver in sorted(pins):
        esc = re.sub(r"[A-Z]", lambda m: "!" + m.group(0).lower(), mod)
        if not os.path.isfile(os.path.join(cache, "cache", "download", esc, "@v", f"{ver}.zip")):
            absent.append(f"{mod}@{ver}")
    if absent:
        die(f"preflight: modules missing from {cache} (fixtures need them; runs have no network):"
            f" go mod download {' '.join(absent)}")
    return cache


def changed_files(o):
    paths = o["paths"]
    if o["base"]:
        return git("diff", "--name-only", o["base"], "--", *paths)
    return git("diff", "--name-only", "HEAD", "--", *paths) + git("ls-files", "-o", "--exclude-standard", "--", *paths)


def changed_lines(o, f):
    """Return the changed line numbers of f in its current version."""
    rng = o["base"] or "HEAD"
    if subprocess.run(["git", "cat-file", "-e", f"{rng}:{f}"], stderr=subprocess.DEVNULL).returncode != 0:
        with open(f, "rb") as fh:
            return list(range(1, fh.read().count(b"\n") + 1))
    out = []
    for line in git("diff", "-U0", rng, "--", f):
        m = re.match(r"@@ -[0-9,]+ \+([0-9]+)(,([0-9]+))? @@", line)
        if m:
            start, n = int(m.group(1)), int(m.group(3) or 1)
            out += range(start, start + max(n, 1))  # a pure deletion: the line after it
    return out


def collect(o):
    """Return {group: tags} and the groups whose every case runs."""
    tags, whole = {}, set()

    def add(g, t):
        tags.setdefault(g, []).append(t)

    if not (o["skills"] or o["all"] or o["cases"]):
        for f in sorted(set(changed_files(o))):
            parts = f.split("/", 4)
            g, p1, p2, p3, p4 = (parts + [""] * 5)[:5]
            if not os.path.isfile(os.path.join(g, ".claude-plugin", "plugin.json")):
                continue
            if p1 == "skills" and p2:
                if p3 == "SKILL.md" and os.path.isfile(f):
                    with open(f) as fh:
                        lines = fh.read().split("\n")
                    for n in changed_lines(o, f):
                        heads = [ln[3:] for ln in lines[:n] if ln.startswith("## ")]
                        add(g, f"sec:{p2}:{slug(heads[-1])}" if heads else f"skill:{p2}")
                elif p3 == "references" and p4:
                    add(g, f"ref:{p2}/{p4[:-3] if p4.endswith('.md') else p4}")
                else:
                    add(g, f"skill:{p2}")
            elif p1 == "evals" and p2 in ("mocks", "fixtures"):
                whole.add(g)
            elif p1 == "evals" and p2 and p2 != "results":
                add(g, f"case:{p2}")
    for s in o["skills"]:
        g, _, name = s.partition("/")
        add(g, f"skill:{name}")
    whole.update(o["all"])
    # Case globs expand here to case:<name> tags; every case carries its own (lint).
    for g, pattern in o["cases"]:
        hits = [d for d in sorted(glob.glob(os.path.join(g, "evals", pattern, "")))
                if os.path.isfile(os.path.join(d, "prompt.md"))]
        if not hits:
            die(f"no case in {g}/evals matches '{pattern}'")
        for d in hits:
            add(g, f"case:{os.path.basename(d.rstrip('/'))}")
    return tags, whole


def ledger(*args, ok=(0,)):
    """Run an eval-ledger.py command; return its stdout and exit code."""
    r = subprocess.run([sys.executable, "-B", os.path.join(HERE, "eval-ledger.py"), *args],
                       stdout=subprocess.PIPE, text=True)
    if r.returncode not in ok:
        sys.exit(r.returncode)
    return r.stdout, r.returncode


def watched(cmd, out, stdout, stderr, stall_s):
    """Run cmd in its own process group and wait for it. When the run's
    results dir and every claude-eval-* workspace have had no write for
    stall_s seconds, save the process tree to out/stall-ps.txt, kill the
    group, and return 124."""
    with open(stdout, "a") as so, open(stderr, "a") as se:
        p = subprocess.Popen(cmd, stdout=so, stderr=se, start_new_session=True)
    poll, n = (1 if stall_s < 60 else 30), 0
    tmpdir = os.environ.get("TMPDIR", "/tmp")
    while p.poll() is None:
        time.sleep(1)
        n += 1
        if p.poll() is not None or n % poll:
            continue
        if not eval_recent.recent(stall_s, out, tmpdir):
            with open(os.path.join(out, "stall-ps.txt"), "w") as f:
                if subprocess.run(["ps", "-ef", "--forest"], stdout=f, stderr=f).returncode:
                    subprocess.run(["ps", "-ef"], stdout=f, stderr=f)
            for sig in (signal.SIGTERM, signal.SIGKILL):
                try:
                    os.killpg(p.pid, sig)
                except ProcessLookupError:
                    pass
                if sig == signal.SIGTERM:
                    time.sleep(2)
            p.wait()
            return 124
    return p.returncode


def last_message(trace):
    text = ""
    with open(trace) as f:
        for line in f:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("type") == "result" and e.get("result"):
                text = e["result"]
            elif e.get("type") == "assistant":
                parts = [b.get("text", "") for b in e["message"].get("content", []) if b.get("type") == "text"]
                if any(parts):
                    text = "\n".join(parts)
    return text


def report(path, failed_dir, keep):
    """Print each run's verdict, keep the traces of failed runs, delete the
    workspaces unless kept; return whether every run passed."""
    with open(path) as f:
        d = json.load(f)
    bad = 0
    for c in d["cases"]:
        for r in c["arms"]["with"]:
            ok = r.get("passed") and not r.get("error")
            bad += not ok
            # A run cut off by the account's usage limit says nothing about the
            # skill: label it so it is re-run, never triaged as a defect.
            limit = "limit" in (r.get("error") or "").lower()
            verdict = "PASS" if ok else ("LIMIT" if limit else "FAIL")
            print(f"   {verdict}  {c['name']}  ({r.get('durationSeconds', '?')}s)")
            if limit:
                print(f"         {r['error']} — re-run; graders not meaningful")
                continue
            if r.get("error"):
                print(f"         error: {r['error']}")
            for gr in r.get("graders", []):
                if not gr.get("passed"):
                    why = (gr.get("evidence") or gr.get("explanation") or "").replace("\n", " ")
                    print(f"         {gr['name']}: {why[:200]}")
            trace = r.get("tracePath") or ""
            if not ok and os.path.isfile(trace):
                os.makedirs(failed_dir, exist_ok=True)
                kept = os.path.join(failed_dir, f"{c['name']}.trace.jsonl")
                shutil.copyfile(trace, kept)
                msg = last_message(trace).strip().replace("\n", "\n         | ")
                print(f"         last message:\n         | {msg[:1500]}")
                print(f"         trace: {kept}")
            tmp = os.path.dirname(os.path.dirname(trace))
            if not keep and os.path.basename(tmp).startswith("claude-eval-"):
                # The run seals parts of its workspace read-only; unseal, then delete.
                subprocess.run(["chmod", "-R", "u+rwx", tmp], stderr=subprocess.DEVNULL)
                shutil.rmtree(tmp, ignore_errors=True)
    a = d["aggregates"]
    print(f"   {a['casesPassed']}/{a['casesTotal']} passed, {d['durationSeconds']}s, ${d['costUsd']:.2f}")
    return not bad


def selected(g, tags, whole):
    """Return the cases of group g the tags reach, in name order."""
    want = sorted(set(tags.get(g, [])))
    out = []
    for pm in sorted(glob.glob(os.path.join(g, "evals", "*", "prompt.md"))):
        c = os.path.basename(os.path.dirname(pm))
        if g in whole:
            out.append(c)
            continue
        with open(pm) as f:
            line = next((ln.rstrip("\n") for ln in f if ln.startswith("tags:")), "")
        if any(f"[{t}," in line or f" {t}," in line or f" {t}]" in line or f"[{t}]" in line for t in want):
            out.append(c)
    return out


def tagged(path, tag):
    with open(path) as f:
        return any(re.match(rf"tags:.*[\[ ,]{tag}[\],]", ln) for ln in f)


def main():
    sys.stdout.reconfigure(line_buffering=True)
    os.chdir(ROOT)
    os.environ["SKILL_EVAL_ROOT"] = ROOT
    # Private run settings of this clone reach both runners.
    load_env_file(os.path.join(ROOT, "tmp", "eval.env"))
    stall_s = int(os.environ.get("EVAL_STALL_SECONDS") or 600)
    o = parse_args(sys.argv[1:])
    if not shutil.which("claude"):
        die("claude CLI not found")
    listed_only = False
    if not (o["audit"] or o["skills"] or o["all"] or o["cases"] or o["dry"]):
        o["dry"], listed_only = True, True

    cache = preflight()
    # Fixture Go modules: a case's scaffold (which runs outside the sandbox)
    # fills the run's own module cache with `go mod download`, fetching from
    # this machine's cache served as a file proxy.
    os.environ["GOPROXY"] = f"file://{cache}/cache/download"

    # Tier 0: lint first; a lint error stops the run.
    lint = [sys.executable, "-B", os.path.join(HERE, "lint-skills.py")]
    if subprocess.run(lint, capture_output=True).returncode != 0:
        out = subprocess.run(lint, capture_output=True, text=True).stdout
        print("\n".join(ln for ln in out.splitlines() if ln.startswith("ERR")))
        die("lint failed; fix it before running evals")

    tags, whole = collect(o)
    groups = sorted(set(tags) | whole)
    if not groups:
        print("eval-changed: no skill change found; lint is clean.")
        return 0

    # A chunk is one runner call over 2 x -j cases. Passes go to the ledger
    # after every chunk, so a run cut off by the usage limit keeps what it
    # earned, and the first limit stops the run (exit 3).
    rc, spent = 0, 0.0
    out = os.path.join(ROOT, "tmp", "eval-changed", f"{time.strftime('%Y%m%dT%H%M%S')}-{os.getpid()}")
    os.makedirs(out, exist_ok=True)
    # Resolve the model word to its ID once: the ID keys the ledger and goes to
    # both runners, so they run, and record, the same model. A dry run reads
    # the last resolved ID and makes no paid call.
    word = o["model"] or "default"
    if o["dry"]:
        model_name = ledger("model", word, "--cached", ok=(0, 1))[0].strip()
    else:
        text, code = ledger("model", word, ok=(0, 1, 3))
        if code == 3:
            print("eval-changed: the usage limit cut off the model probe; re-run after the reset")
            return 3
        model_name = text.strip()
        if not model_name:
            die(f"cannot resolve --model {word} (see above)")
    jobs = o["jobs"]
    chunk = int(jobs) * 2

    for g in groups:
        if not os.path.isdir(os.path.join(g, "evals")):
            print(f"== {g}: no native cases (lint only)")
            continue
        sel = selected(g, tags, whole)
        total = len(sel)
        if o["fresh"] or not total or not model_name:
            todo = list(sel)
        else:
            todo = ledger("pending", g, model_name, *sel)[0].split()
        # A case whose dir changed since its last verdict on this model, or
        # that has no verdict and is new or changed against the base, runs
        # twice and passes only when both runs pass: new graders are where
        # false verdicts come from.
        twice = set()
        if model_name and todo:
            changed = sorted({m.group(1) for f in changed_files(o)
                              if (m := re.match(rf"{re.escape(g)}/evals/([^/]+)/", f))})
            twice = set(ledger("twice", g, model_name, *todo, "--changed", *changed)[0].split())
        # needs-shell cases run through eval-shell.py: `claude plugin eval`
        # wraps each in-run command in a sandbox that nests a user namespace
        # inside bwrap's, which stock Ubuntu refuses. Fan-out cases ($3-9 each)
        # run after every other case, so a --max-usd cap finishes and records
        # the cheap ones first; within each, once-run cases come first.
        batches = {k: [] for k in KINDS}
        for c in todo:
            pm = os.path.join(g, "evals", c, "prompt.md")
            kind = ("shell" if tagged(pm, "needs-shell") else "plain") + ("fan" if tagged(pm, "fan-out") else "")
            batches[kind + ("2" if c in twice else "")].append(c)
        listing, priced = [], []
        for kind in KINDS:
            for c in batches[kind]:
                listing.append(f"{c} (2 runs)" if kind.endswith("2") else c)
                priced += [c, c] if kind.endswith("2") else [c]
        n = len(todo)
        # Each case's last stored cost on this model, else the Opus bands.
        est = ledger("estimate", g, model_name, *priced)[0].strip()
        print(f"== {g}: {total} case(s), {total - n} PASS in the ledger, {n} to run, {est};"
              f" model {model_name or 'unresolved'}")
        # A case whose last runs at its current inputs both passed and failed
        # is flaky: name it even when its last run passed and it will not run.
        if model_name and total:
            rows = [ln.split() for ln in ledger("flaky", g, model_name, *sel)[0].splitlines() if ln.strip()]
            if rows:
                print("   flaky: " + ", ".join(f"{r[0]} ({r[1]} of {r[2]} failed)" for r in rows))
        if o["dry"]:
            for item in listing if n else []:
                print(f"   {item}")
            continue
        done_n, stop = 0, False
        for ki, kind in enumerate(KINDS):
            runs = 2 if kind.endswith("2") else 1
            batch = batches[kind]
            nb = len(batch)
            for k in range(0, nb, chunk):
                part = batch[k:k + chunk]
                path = os.path.join(out, f"{g}-{kind}-{k}.json")
                cap = []
                if o["max_usd"]:
                    left = round(float(o["max_usd"]) - spent, 2)
                    if left <= 0:
                        # Name every case of the group this stop leaves unrun.
                        rest = batch[k:] + [c for later in KINDS[ki + 1:] for c in batches[later]]
                        print(f"   not started (--max-usd {o['max_usd']} spent): {' '.join(rest)}")
                        rc, stop = 1, True
                        break
                    cap = ["--max-cost-usd", str(left)]
                print(f"   {kind} chunk {k // chunk + 1}/{math.ceil(nb / chunk)}: {' '.join(part)}"
                      f" ({time.strftime('%H:%M')})")
                if kind.startswith("shell"):
                    cmd = [sys.executable, "-B", os.path.join(HERE, "eval-shell.py"), g, *part,
                           "--model", model_name, "--runs", str(runs), "-j", jobs, "--keep", *cap, "--json", path]
                else:
                    sel_tags = [x for c in part for x in ("--tag", f"case:{c}")]
                    cmd = ["claude", "plugin", "eval", f"./{g}", *sel_tags, "--runs", str(runs),
                           "--ablation", "none", "--scaffold", "--trust-plugin", "--no-publish", "-j", jobs,
                           "--keep-temp", "--model", model_name, *cap, "--allow-tools", "Write", "Edit", "LSP",
                           "--output-dir", os.path.join(out, g, f"{kind}-{k}"), "--json", path]
                r = watched(cmd, out, os.path.join(out, f"{g}.out"), os.path.join(out, f"{g}.err"), stall_s)
                if r == 124:
                    print(f"   STALL: no write for {stall_s}s; killed the run"
                          f" (process tree: {out}/stall-ps.txt)")
                    rc, stop = 1, True
                    break
                has_json = os.path.isfile(path) and os.path.getsize(path) > 0
                if has_json:
                    with open(path) as f:
                        spent += json.load(f).get("costUsd", 0)
                if r == 2:
                    print(f"   stopped at the --max-usd {o['max_usd']} ceiling (partial results)")
                done_n += len(part)
                if not has_json:
                    with open(os.path.join(out, f"{g}.err")) as f:
                        errs = [ln.rstrip("\n") for ln in f if not ln.startswith("Note:")]
                    for ln in errs[-5:]:
                        print(ln)
                    print(f"   no cases ran (see {out}/{g}.err)")
                    rc = 1
                    continue
                if r == 2:
                    # The runner left out the cases it did not start.
                    with open(path) as f:
                        got = {c["name"] for c in json.load(f)["cases"]}
                    miss = " ".join(c for c in part if c not in got)
                    if miss:
                        print(f"   not started (--max-usd {o['max_usd']} spent): {miss}")
                if r != 0:
                    rc = 1
                # At the ceiling `claude plugin eval` still scores the free
                # graders of the run that crossed it and skips the paid ones,
                # so no verdict of that chunk reaches the ledger. Record while
                # every run's trace still exists: the report deletes passing
                # workspaces and their traces.
                rec = ""
                if kind.startswith("plain") and r == 2:
                    print("   ledger unchanged for this chunk: it stopped at the ceiling")
                else:
                    rec = ledger("record", g, model_name, path)[0]
                if not report(path, os.path.join(out, g, "failed"), o["keep"]):
                    rc = 1
                for ln in rec.splitlines():
                    if ln.startswith("MODEL"):
                        _, c, mid = (ln.split() + ["", "", ""])[:3]
                        if c:
                            print(f"   {c} ran on {mid}, not {model_name}: not recorded")
                lim = next((ln for ln in rec.splitlines() if ln.startswith("LIMIT")), "")
                if lim:
                    print(f"   LIMIT: the usage limit cut off {lim[len('LIMIT '):]} run(s);"
                          f" {n - done_n} case(s) not started.")
                    print("   Passes are in the ledger: re-run the same command after the reset.")
                    print(f"results: {out}")
                    return 3
            if stop:
                break
    # A history_file run leaves a session file (UUID name) beside the history;
    # it holds the runner's full system prompt, so it must not linger.
    for f in git("ls-files", "-o", "-i", "--exclude-standard", "--", "*/evals/*"):
        if UUID_JSONL.search(f):
            try:
                os.remove(f)
            except OSError:
                pass
    if o["dry"]:
        try:
            os.rmdir(out)
        except OSError:
            pass
        if listed_only:
            print("listed only: agent-run cases are a manual audit (--audit runs them)."
                  " Routine check: scripts/eval-check.py && scripts/eval-probe.py")
        return 0
    print(f"results: {out}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
