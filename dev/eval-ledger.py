#!/usr/bin/env python3
"""Pass ledger for the agent-run cases (used by dev/eval-changed.sh).

A case's key is a sha256 over everything its run depends on: the case dir,
every file of each skill its tags name (skill:, sec:, ref: — the skill dir
minus evals/), the group's shared mocks/ and fixtures/, and the model. A PASS
is recorded under that key in tmp/eval-ledger.json; while the key is
unchanged, the case need not run again.

  eval-ledger.py pending <group> <model> <case>...   print cases without a
                                                     PASS at their current key
  eval-ledger.py record <group> <model> <result.json>
        record each PASS; print `FAIL <case>` per failed run and `LIMIT <n>`
        when n runs hit the usage limit
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LEDGER = os.path.join(ROOT, "tmp", "eval-ledger.json")


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


def load():
    try:
        with open(LEDGER) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def main():
    cmd, group, model = sys.argv[1], sys.argv[2], sys.argv[3] or "default"
    led = load()
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
            if "limit" in (r.get("error") or "").lower():
                limit += 1
            elif r.get("passed") and not r.get("error"):
                led[f"{group}/{c['name']}"] = key(group, c["name"], model)
            else:
                print(f"FAIL {c['name']}")
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "w") as f:
        json.dump(led, f, indent=1, sort_keys=True)
    if limit:
        print(f"LIMIT {limit}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
