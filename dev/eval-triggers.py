#!/usr/bin/env python3
"""Trigger routing: does each request pick the right skill from descriptions?

The model sees every shipped skill's frontmatter description, plus the
distractor skills a real session also lists (dev/eval/triggers.json), and
routes each request to one skill or `none`. All requests go in a few batched
calls on haiku without thinking; a miss is re-asked alone three times with
thinking and reported as FAIL (0/3) or SPLIT. Answers are cached by input in
tmp/probe-cache/, so only a description or case edit costs anything (about
$0.01 per changed batch).

Usage:
  ./dev/eval-triggers.py           every case
  ./dev/eval-triggers.py --show    print every routing, not only misses
  --model M, -j N, --no-cache as in eval-probe.py
Exit status is non-zero on any FAIL or SPLIT.
"""
import argparse
import concurrent.futures as cf
import glob
import importlib.util
import json
import os
import re
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.dont_write_bytecode = True  # loading eval-probe.py must not leave dev/__pycache__
SPEC = importlib.util.spec_from_file_location("eval_probe", os.path.join(ROOT, "dev", "eval-probe.py"))
ep = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ep)
CHUNK = 32


def descriptions():
    out = {}
    for g in ep.GROUPS:
        for f in sorted(glob.glob(os.path.join(ROOT, g, "skills", "*", "SKILL.md"))):
            with open(f) as fh:
                fm = fh.read().split("---")[1]
            m = re.search(r"^description:\s*[>|]?-?\s*\n?(.*?)(?=\n[a-z_-]+:|\Z)", fm, re.S | re.M)
            out[f"{g}:{os.path.basename(os.path.dirname(f))}"] = re.sub(r"\s+", " ", m.group(1)).strip()
    return out


def load():
    with open(os.path.join(ROOT, "dev", "eval", "triggers.json")) as f:
        return json.load(f)


def system(skills):
    lines = [f"- {n}: {d}" for n, d in skills.items()]
    return ("You route a user's request to the one skill that should handle it, "
            "or to none. Available skills (name: description):\n\n" + "\n".join(lines))


def parse(text):
    return {int(m.group(1)): m.group(2).strip().strip("`*").lower()
            for m in re.finditer(r"^\W*(\d+)\s*[:.)]\s*(\S+)", text, re.M)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--model", default="haiku")
    ap.add_argument("-j", type=int, default=8)
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()
    data = load()
    skills = {**descriptions(), **data["distractors"]}
    sysp = system(skills)
    cases = data["cases"]
    use_cache, spend, t0 = not a.no_cache, ep.Spend(), time.time()

    def batch(k):
        part = cases[k:k + CHUNK]
        q = ("Route each numbered request. Answer one line per request, "
             "`<n>: <skill name>` or `<n>: none`, and nothing else.\n\n" +
             "\n".join(f"{i + 1}: {c['say']}" for i, c in enumerate(part)))
        d = ep.call(a.model, sysp, q, 0, use_cache, think=False)
        spend.add(d)
        got = parse(d.get("answer", ""))
        return [got.get(i + 1, "?") for i in range(len(part))]

    with cf.ThreadPoolExecutor(max_workers=max(1, a.j)) as ex:
        first = [x for part in ex.map(batch, range(0, len(cases), CHUNK)) for x in part]

    def settle(i):
        c, ans = cases[i], first[i]
        if ans == c["want"]:
            return i, "PASS", [ans]
        q = (f"Request: {c['say']}\n\nAnswer with the one skill name that should "
             "handle it, or none, and nothing else.")
        with cf.ThreadPoolExecutor(max_workers=3) as ex:
            ds = list(ex.map(lambda t: ep.call(a.model, sysp, q, t, use_cache, think=True),
                             range(3)))
        got = []
        for d in ds:
            spend.add(d)
            got.append(re.sub(r"[`*\s].*", "", d.get("answer", "?").strip().lower(), flags=re.S))
        ok = sum(g == c["want"] for g in got)
        return i, ("PASS" if ok == 3 else "FAIL" if ok == 0 else "SPLIT"), got

    bad = 0
    with cf.ThreadPoolExecutor(max_workers=max(1, a.j)) as ex:
        for i, verdict, got in ex.map(settle, range(len(cases))):
            c = cases[i]
            if verdict != "PASS":
                bad += 1
                print(f"   {verdict:<6} \"{c['say']}\" -> want {c['want']}, got {', '.join(got)}")
            elif a.show:
                print(f"   PASS   \"{c['say']}\" -> {got[0]}")
    print(f"eval-triggers: {len(cases)} case(s), {len(cases) - bad} pass, {bad} not; "
          f"{spend.calls} model call(s), ${spend.cost:.2f}, {time.time() - t0:.0f}s ({a.model})")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
