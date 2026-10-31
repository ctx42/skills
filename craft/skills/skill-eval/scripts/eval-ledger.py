#!/usr/bin/env python3
"""Pass ledger for the agent-run cases (used by eval-changed.sh).

A case's key is a sha256 over everything its run depends on: the case dir,
every file of each skill its tags name (skill:, sec:, ref: — the skill dir
minus evals/), the group's shared mocks/ and fixtures/, and the model. A PASS
is recorded under that key in tmp/eval-ledger.json; while the key is
unchanged, the case need not run again.

  eval-ledger.py pending <group> <model> <case>...   print cases without a
                                                     PASS at their current key
  eval-ledger.py record <group> <model> <result.json>
        record each PASS; print `FAIL <case>` per failed run, `MODEL <case>
        <id>` per run on another model than <model> (neither recorded nor
        cleared), and `LIMIT <n>` when n runs hit the usage limit
  eval-ledger.py model <word> [--cached]
        print the model ID that `--model <word>` resolves to (`default`: the
        CLI's default model) from one short `claude -p` probe, and cache it in
        tmp/eval-model.json; with --cached, print the cached ID or nothing.
        Exit 3 when the usage limit cut the probe off.

<model> is a resolved model ID, so a pass is a pass on that model.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True  # importing evalroot must not leave __pycache__ in the skill
from evalroot import ROOT  # noqa: E402
LEDGER = os.path.join(ROOT, "tmp", "eval-ledger.json")
MODELS = os.path.join(ROOT, "tmp", "eval-model.json")


def main_model(usage):
    """Return the model ID that cost the most in a result event's modelUsage
    (the session's model, not a helper model), or None when there is none."""
    best, cost = None, -1.0
    for mid, u in (usage or {}).items():
        c = (u or {}).get("costUSD") or 0
        if c > cost:
            best, cost = mid, c
    return best


def run_model(run):
    """Return the model ID one run reports: its result's `model`, else the
    main model of the last result event in its trace, else None."""
    if run.get("model"):
        return run["model"]
    found = None
    try:
        with open(run.get("tracePath") or "") as f:
            for line in f:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if isinstance(e, dict) and e.get("type") == "result":
                    found = main_model(e.get("modelUsage")) or found
    except OSError:
        pass
    return found


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=1, sort_keys=True)


def resolve(word, cached):
    """Return (exit code, model ID) for `--model <word>`; see the docstring."""
    cache = load_json(MODELS)
    if cached:
        return 0, cache.get(word, "")
    cmd = ["claude", "-p", "Reply with the single word OK.", "--output-format", "json",
           "--max-turns", "1", "--tools", "", "--setting-sources", "project",
           "--no-session-persistence"]
    if word != "default":
        cmd += ["--model", word]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    try:
        j = json.loads(r.stdout)
    except ValueError:
        print(f"eval-ledger: model probe failed: {(r.stderr or r.stdout).strip()[-300:]}", file=sys.stderr)
        return 1, ""
    if j.get("is_error"):
        msg = str(j.get("result"))
        print(f"eval-ledger: model probe failed: {msg[-300:]}", file=sys.stderr)
        return (3 if "limit" in msg.lower() else 1), ""
    mid = main_model(j.get("modelUsage"))
    if not mid:
        print("eval-ledger: model probe reported no model", file=sys.stderr)
        return 1, ""
    cache[word] = mid
    save_json(MODELS, cache)
    return 0, mid


def files_under(top, skip=()):
    out = []
    for dp, dns, fs in os.walk(top):
        dns[:] = sorted(d for d in dns if d not in skip)
        out += [os.path.join(dp, f) for f in sorted(fs)]
    return out


def key(group, case, model):
    cdir = os.path.join(ROOT, group, "evals", case)
    with open(os.path.join(cdir, "prompt.md")) as f:
        m = re.search(r"^tags:\s*\[([^\]]*)\]", f.read(), re.M)
    skills = set()
    for t in (m.group(1).split(",") if m else []):
        t = t.strip()
        mm = re.match(r"^(?:skill:|sec:|ref:)([a-z0-9-]+)", t)
        if mm:
            skills.add(mm.group(1))
    paths = files_under(cdir)
    for s in sorted(skills):
        paths += files_under(os.path.join(ROOT, group, "skills", s), skip=("evals",))
    for sub in ("mocks", "fixtures"):
        paths += files_under(os.path.join(ROOT, group, "evals", sub))
    h = hashlib.sha256(f"model={model}\n".encode())
    for p in paths:
        h.update(os.path.relpath(p, ROOT).encode() + b"\0")
        with open(p, "rb") as f:
            h.update(f.read())
    return h.hexdigest()


def main():
    if sys.argv[1] == "model":
        code, mid = resolve(sys.argv[2], "--cached" in sys.argv[3:])
        if mid:
            print(mid)
        return code
    cmd, group, model = sys.argv[1], sys.argv[2], sys.argv[3] or "default"
    led = load_json(LEDGER)
    if cmd == "pending":
        for c in sys.argv[4:]:
            if led.get(f"{group}/{c}") != key(group, c, model):
                print(c)
        return 0
    with open(sys.argv[4]) as f:
        d = json.load(f)
    limit = 0
    for c in d.get("cases", []):
        for r in c["arms"]["with"]:
            ran_on = run_model(r)
            if "limit" in (r.get("error") or "").lower():
                limit += 1
            elif ran_on and ran_on != model:
                # A verdict on another model says nothing about this key.
                print(f"MODEL {c['name']} {ran_on}")
            elif r.get("passed") and not r.get("error"):
                led[f"{group}/{c['name']}"] = key(group, c["name"], model)
            else:
                # A finished run that did not pass is a verdict on this key:
                # drop the old pass so the next run does not skip the case.
                led.pop(f"{group}/{c['name']}", None)
                print(f"FAIL {c['name']}")
    save_json(LEDGER, led)
    if limit:
        print(f"LIMIT {limit}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
