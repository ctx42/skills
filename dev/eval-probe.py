#!/usr/bin/env python3
"""Decision probes: one cheap question per high-stakes rule, cached.

A probe loads a skill's SKILL.md (plus any listed references) as the system
prompt, gives a prepared situation and one question, and grades the short
answer by regex. No tools, one turn, a small model: about $0.01-0.02 and a few
seconds each, and an answer whose inputs have not changed is replayed from
tmp/probe-cache/ for free. Grading always re-runs, so a fixed `pass`/`fail`
regex never needs a paid re-run.

Probe file: <group>/skills/<skill>/evals/probes.json
  {"skill_name": "kb", "probes": [{
     "id": "inference-stays-out",       unique within the skill
     "rule": "attested-only",           a contract.json rule id (optional)
     "context": ["SKILL.md", "references/x.md"],   default ["SKILL.md"]
     "prompt": "Situation: ... Question: ... Answer in one line ...",
     "pass": "regex the answer must match",
     "fail": "regex the answer must not match (optional)"}]}
Regexes are Python, case-insensitive, dot matches newline.

Usage:
  ./dev/eval-probe.py                  every probe (unchanged ones are free)
  ./dev/eval-probe.py --skill srd/kb   one skill (repeatable)
  ./dev/eval-probe.py --probe srd/kb:inference-stays-out
  --model M   default haiku; sonnet for a probe haiku cannot judge
  -j N        concurrent calls (default 8)
  --no-cache  ignore cached answers (still writes them)
  --show      print every answer, not only failures

A failing probe is re-asked twice more (cached separately) and reported as
FAIL (0/3) or SPLIT (1/3, 2/3) — a split is a measured ambiguity in the skill
text. Exit status is non-zero on any FAIL or SPLIT.
"""
import argparse
import concurrent.futures as cf
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CACHE = os.path.join(ROOT, "tmp", "probe-cache")
GROUPS = ("go", "srd", "craft")

FRAME = """You are an AI coding agent with the skill below loaded: its SKILL.md \
and the reference files it uses follow. A user is in a session with you. Answer \
the user's question exactly as this skill directs you to act. You have no tools \
in this conversation: answer from the skill text alone, in the form the question \
asks for, briefly. Do not hedge between options; commit to what the skill says \
you do."""


def discover(skills, probes):
    out = []
    for g in GROUPS:
        for path in sorted(glob.glob(os.path.join(ROOT, g, "skills", "*", "evals",
                                                  "probes.json"))):
            sdir = os.path.dirname(os.path.dirname(path))
            key = f"{g}/{os.path.basename(sdir)}"
            if skills and key not in skills:
                continue
            with open(path) as f:
                data = json.load(f)
            for p in data.get("probes", []):
                pk = f"{key}:{p['id']}"
                if probes and pk not in probes:
                    continue
                out.append((pk, sdir, p))
    return out


def system_prompt(sdir, context):
    parts = [FRAME]
    for cf_ in context:
        path = os.path.normpath(os.path.join(sdir, cf_))
        with open(path) as f:
            parts.append(f"=== {os.path.relpath(path, os.path.dirname(sdir))} ===\n"
                         + f.read())
    return "\n\n".join(parts)


def ask(model, system, prompt, trial, use_cache):
    key = hashlib.sha256("\0".join([model, system, prompt, str(trial)])
                         .encode()).hexdigest()
    path = os.path.join(CACHE, key + ".json")
    if use_cache and os.path.isfile(path):
        with open(path) as f:
            d = json.load(f)
        d["cached"] = True
        return d
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as sf:
        sf.write(system)
    try:
        t0 = time.time()
        r = subprocess.run(
            ["claude", "-p", "--model", model, "--tools", "", "--setting-sources", "",
             "--strict-mcp-config", "--disable-slash-commands",
             "--no-session-persistence", "--output-format", "json",
             "--system-prompt-file", sf.name],
            input=prompt, capture_output=True, text=True, timeout=180)
        wall = time.time() - t0
    finally:
        os.unlink(sf.name)
    try:
        j = json.loads(r.stdout)
    except ValueError:
        return {"error": (r.stderr or r.stdout).strip()[-300:], "cost": 0, "wall": 0}
    if j.get("is_error"):
        return {"error": str(j.get("result"))[-300:], "cost": 0, "wall": wall}
    d = {"answer": j.get("result", ""), "cost": j.get("total_cost_usd", 0),
         "wall": wall}
    os.makedirs(CACHE, exist_ok=True)
    with open(path, "w") as f:
        json.dump(d, f)
    d["cached"] = False
    return d


def grade(p, answer):
    flags = re.I | re.S
    if not re.search(p["pass"], answer, flags):
        return False
    if p.get("fail") and re.search(p["fail"], answer, flags):
        return False
    return True


def run_probe(item, model, use_cache):
    pk, sdir, p = item
    system = system_prompt(sdir, p.get("context", ["SKILL.md"]))
    results = []
    for trial in range(3):
        d = ask(model, system, p["prompt"], trial, use_cache)
        if "error" in d:
            return pk, "ERROR", [d], p
        d["ok"] = grade(p, d["answer"])
        results.append(d)
        if trial == 0 and d["ok"]:
            break
    ok = sum(r["ok"] for r in results)
    if len(results) == 1:
        verdict = "PASS"
    else:
        verdict = "FAIL" if ok == 0 else "SPLIT"
    return pk, verdict, results, p


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skill", action="append", default=[])
    ap.add_argument("--probe", action="append", default=[])
    ap.add_argument("--model", default="haiku")
    ap.add_argument("-j", type=int, default=8)
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()
    items = discover(set(a.skill), set(a.probe))
    if not items:
        print("eval-probe: no probes selected")
        return 0
    t0 = time.time()
    cost, fresh, bad = 0.0, 0, 0
    with cf.ThreadPoolExecutor(max_workers=max(1, a.j)) as ex:
        futs = [ex.submit(run_probe, it, a.model, not a.no_cache) for it in items]
        for fut in cf.as_completed(futs):
            pk, verdict, results, p = fut.result()
            cost += sum(r.get("cost", 0) for r in results if not r.get("cached"))
            fresh += sum(1 for r in results if r.get("cached") is False)
            ok = sum(r.get("ok", False) for r in results)
            tag = verdict if verdict in ("PASS", "ERROR") else f"{verdict} ({ok}/3)"
            print(f"   {tag:<12} {pk}")
            if verdict != "PASS":
                bad += 1
                if verdict == "ERROR":
                    print(f"      {results[0]['error']}")
                else:
                    print(f"      pass: /{p['pass']}/" +
                          (f"  fail: /{p['fail']}/" if p.get("fail") else ""))
                    for r in results:
                        print("      | " + r["answer"].strip().replace("\n", "\n      | ")[:600])
            elif a.show:
                print("      | " + results[0]["answer"].strip().replace("\n", "\n      | ")[:600])
    print(f"eval-probe: {len(items)} probe(s), {len(items) - bad} pass, {bad} not; "
          f"{fresh} model call(s), ${cost:.2f}, {time.time() - t0:.0f}s ({a.model})")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
