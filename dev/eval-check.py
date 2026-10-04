#!/usr/bin/env python3
"""Free, offline eval checks: no model calls, runs in seconds.

Checks, in order:
  contracts   every <group>/skills/<skill>/evals/contract.json rule still
              holds: each `must` regex matches its file, no `must_not` does
  probes      every evals/probes.json is well-formed: context files exist,
              regexes compile, `rule` names a contract rule
  generators  every dev/eval/gen/*/gen.py reproduces its cases byte for byte
  literals    every doc id or URL a native-case regex grader names is served
              by that case's prompt, mocks, scaffold, or the group's shared
              mocks/fixtures (catches a rename that missed one side)
  gone        with --gone STR (repeatable): STR appears nowhere under the
              skill and eval trees

Usage:
  ./dev/eval-check.py                  all checks
  ./dev/eval-check.py --only contracts (contracts|probes|generators|literals)
  ./dev/eval-check.py --gone confluence/example/
Exit status is non-zero on any failure.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GROUPS = ("go", "srd", "craft")


def norm(text):
    """Collapse whitespace so a phrase matches across hard-wrapped lines."""
    return re.sub(r"\s+", " ", text)


def rx(pattern):
    return re.compile(pattern, re.I | re.S)


def skill_dirs():
    for g in GROUPS:
        for d in sorted(glob.glob(os.path.join(ROOT, g, "skills", "*"))):
            if os.path.isfile(os.path.join(d, "SKILL.md")):
                yield g, d


def rel(p):
    return os.path.relpath(p, ROOT)


def load_json(path, errs):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        errs.append(f"{rel(path)}: {e}")
        return None


def check_contracts(errs):
    n = 0
    for g, d in skill_dirs():
        path = os.path.join(d, "evals", "contract.json")
        if not os.path.isfile(path):
            errs.append(f"{rel(d)}: no evals/contract.json")
            continue
        c = load_json(path, errs)
        if c is None:
            continue
        cache = {}
        for r in c.get("rules", []):
            n += 1
            rid = r.get("id", "?")
            f = os.path.normpath(os.path.join(d, r.get("file", "SKILL.md")))
            if f not in cache:
                try:
                    with open(f) as fh:
                        cache[f] = norm(fh.read())
                except OSError:
                    errs.append(f"{rel(path)}: rule {rid}: missing file {rel(f)}")
                    cache[f] = None
            text = cache[f]
            if text is None:
                continue
            for p in r.get("must", []):
                try:
                    if not rx(p).search(text):
                        errs.append(f"{rel(d)}: rule '{rid}' broken — {rel(f)} "
                                    f"no longer says /{p}/  ({r.get('rule', '')})")
                except re.error as e:
                    errs.append(f"{rel(path)}: rule {rid}: bad regex /{p}/: {e}")
            for p in r.get("must_not", []):
                try:
                    m = rx(p).search(text)
                except re.error as e:
                    errs.append(f"{rel(path)}: rule {rid}: bad regex /{p}/: {e}")
                    continue
                if m:
                    errs.append(f"{rel(d)}: rule '{rid}' contradicted — {rel(f)} "
                                f"says \"{m.group(0)[:80]}\"  ({r.get('rule', '')})")
    return f"contracts: {n} rule(s)"


def check_probes(errs):
    n = 0
    for g, d in skill_dirs():
        path = os.path.join(d, "evals", "probes.json")
        if not os.path.isfile(path):
            errs.append(f"{rel(d)}: no evals/probes.json")
            continue
        p = load_json(path, errs)
        if p is None:
            continue
        cpath = os.path.join(d, "evals", "contract.json")
        rules = set()
        if os.path.isfile(cpath):
            c = load_json(cpath, errs) or {}
            rules = {r.get("id") for r in c.get("rules", [])}
        ids = set()
        for pr in p.get("probes", []):
            n += 1
            pid = pr.get("id", "?")
            if pid in ids:
                errs.append(f"{rel(path)}: duplicate probe id {pid}")
            ids.add(pid)
            for k in ("id", "prompt", "pass"):
                if not pr.get(k):
                    errs.append(f"{rel(path)}: probe {pid}: missing '{k}'")
            if pr.get("rule") and pr["rule"] not in rules:
                errs.append(f"{rel(path)}: probe {pid}: rule '{pr['rule']}' "
                            "is not in contract.json")
            for cf in pr.get("context", ["SKILL.md"]):
                if not os.path.isfile(os.path.normpath(os.path.join(d, cf))):
                    errs.append(f"{rel(path)}: probe {pid}: no context file {cf}")
            for k in ("pass", "fail"):
                if pr.get(k):
                    try:
                        rx(pr[k])
                    except re.error as e:
                        errs.append(f"{rel(path)}: probe {pid}: bad '{k}' regex: {e}")
    return f"probes: {n} well-formed check(s)"


def tree_hash(paths):
    h = {}
    for top in paths:
        for dp, _, fs in os.walk(top):
            for f in fs:
                p = os.path.join(dp, f)
                with open(p, "rb") as fh:
                    h[p] = hashlib.sha256(fh.read()).hexdigest()
    return h


def check_generators(errs):
    gens = sorted(glob.glob(os.path.join(ROOT, "dev/eval/gen/*/gen.py")))
    tops = [os.path.join(ROOT, g, "evals") for g in GROUPS]
    before = tree_hash(tops)
    for gen in gens:
        r = subprocess.run([sys.executable, "gen.py"], cwd=os.path.dirname(gen),
                           capture_output=True, text=True)
        if r.returncode:
            errs.append(f"{rel(gen)}: exit {r.returncode}: {r.stderr.strip()[-200:]}")
    after = tree_hash(tops)
    changed = sorted({os.path.dirname(rel(p)) for p in set(before) | set(after)
                      if before.get(p) != after.get(p)})
    for c in changed:
        errs.append(f"{c}: differs from its generator's output (now rewritten — "
                    "edit the generator, not the case)")
    return f"generators: {len(gens)} reproduced"


LIT_URL = re.compile(r"https?://[A-Za-z0-9.-]+\.[a-z]{2,}(?:/[A-Za-z0-9._~%/-]*)?")
LIT_ID = re.compile(r"\b[a-z0-9_-]+(?:/[A-Za-z0-9_.-]+)+\.md\b")


def grader_pattern(text):
    parts = text.split("---")
    if len(parts) < 3:
        return None, None
    fm, body = parts[1], "---".join(parts[2:])
    m = re.search(r"^input_match:\s*'(.*)'\s*$", fm, re.M)
    if m:
        return fm, m.group(1)
    return fm, body.strip()


def check_literals(errs):
    n = 0
    for g in GROUPS:
        edir = os.path.join(ROOT, g, "evals")
        shared = ""
        for sub in ("mocks", "fixtures"):
            for p in glob.glob(os.path.join(edir, sub, "**", "*"), recursive=True):
                if os.path.isfile(p):
                    with open(p, errors="replace") as f:
                        shared += f.read()
        # Doc-id roots the group's mocks serve, so output paths (kb/, specs/)
        # are not mistaken for corpus ids.
        roots = set(re.findall(r'"(?:doc_)?id"\s*:\s*"([a-z0-9_-]+)/', shared))
        for case in sorted(glob.glob(os.path.join(edir, "*", "graders"))):
            cdir = os.path.dirname(case)
            served = shared
            for p in glob.glob(os.path.join(cdir, "**", "*"), recursive=True):
                if os.path.isfile(p) and "/graders/" not in p:
                    with open(p, errors="replace") as f:
                        served += f.read()
            for gp in sorted(glob.glob(os.path.join(case, "*.md"))):
                with open(gp) as f:
                    fm, pat = grader_pattern(f.read())
                if not fm or "type: regex" not in fm and "input_match" not in fm:
                    continue
                lit = pat.replace("\\.", ".").replace("\\/", "/")
                found = set(LIT_URL.findall(lit))
                found |= {i for i in LIT_ID.findall(lit) if i.split("/")[0] in roots}
                for t in sorted(found):
                    n += 1
                    t = t.rstrip("/.")
                    if t not in served:
                        errs.append(f"{rel(gp)}: names '{t}', which nothing in "
                                    "the case serves")
    return f"literals: {n} checked"


def check_gone(strings, errs):
    tops = [os.path.join(ROOT, g) for g in GROUPS] + [os.path.join(ROOT, "dev/eval")]
    for s in strings:
        for top in tops:
            r = subprocess.run(["grep", "-rnIF", "--", s, top], capture_output=True,
                               text=True)
            for line in r.stdout.splitlines()[:20]:
                errs.append(f"gone '{s}' still present: {rel(line.split(':')[0])}:"
                            f"{line.split(':')[1]}")
    return f"gone: {len(strings)} string(s)"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--only", choices=["contracts", "probes", "generators", "literals"])
    ap.add_argument("--gone", action="append", default=[])
    a = ap.parse_args()
    checks = {
        "contracts": check_contracts,
        "probes": check_probes,
        "generators": check_generators,
        "literals": check_literals,
    }
    errs, summary = [], []
    for name, fn in checks.items():
        if a.only and a.only != name:
            continue
        summary.append(fn(errs))
    if a.gone:
        summary.append(check_gone(a.gone, errs))
    for e in errs:
        print("ERR ", e)
    print("eval-check: " + "; ".join(summary) + f" — {len(errs)} error(s)")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
