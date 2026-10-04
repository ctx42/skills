#!/usr/bin/env python3
"""Re-grade a saved agent-run trace offline: verify a grader fix for free.

Applies a native case's `type: regex` graders that target `last_message` to
the final reply in a saved trace (failed runs keep theirs under
tmp/eval-changed/<run>/<group>/failed/<case>.trace.jsonl). Every other grader
kind needs the run's workspace or a model and is reported SKIP.

Usage:
  ./dev/eval-regrade.py <trace.jsonl>              case taken from the file name
  ./dev/eval-regrade.py <trace.jsonl> <case dir>
Exit status is non-zero when any applied grader fails.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def last_message(trace):
    text = ""
    with open(trace) as f:
        for line in f:
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            if ev.get("type") == "result" and isinstance(ev.get("result"), str):
                return ev["result"]
            if ev.get("type") == "assistant":
                parts = [c.get("text", "") for c in ev.get("message", {}).get("content", [])
                         if c.get("type") == "text"]
                if parts:
                    text = "\n".join(parts)
    return text


def frontmatter(text):
    parts = text.split("---")
    if len(parts) < 3:
        return {}, text
    fm = {}
    for line in parts[1].splitlines():
        m = re.match(r"^(\w+):\s*(.*?)\s*$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip("'\"")
    return fm, "---".join(parts[2:]).strip()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    trace = sys.argv[1]
    if len(sys.argv) > 2:
        case = sys.argv[2]
    else:
        name = os.path.basename(trace).removesuffix(".trace.jsonl")
        hits = glob.glob(os.path.join(ROOT, "*", "evals", name))
        if len(hits) != 1:
            print(f"eval-regrade: cannot find case '{name}'; pass its directory")
            return 2
        case = hits[0]
    msg = last_message(trace)
    bad = applied = 0
    for gp in sorted(glob.glob(os.path.join(case, "graders", "*.md"))):
        with open(gp) as f:
            fm, body = frontmatter(f.read())
        gid = os.path.basename(gp)[:-3]
        if fm.get("type") != "regex" or fm.get("target") != "last_message":
            print(f"   SKIP  {gid}  ({fm.get('type')} on {fm.get('target', '?')})")
            continue
        flags = re.S if "s" in fm.get("flags", "") else 0
        flags |= re.I if "i" in fm.get("flags", "") else 0
        flags |= re.M if "m" in fm.get("flags", "") else 0
        pat = re.sub(r"\(\?<([A-Za-z_]\w*)>", r"(?P<\1>", body)
        try:
            n = len(re.findall(pat, msg, flags))
        except re.error as e:
            print(f"   ERR   {gid}: regex does not compile in Python: {e}")
            bad += 1
            continue
        match = fm.get("match", "contains")
        if match == "not_contains":
            ok = n == 0
        elif match.startswith("count:"):
            ok = n == int(match.split(":")[1])
        else:
            ok = n > 0
        applied += 1
        bad += not ok
        print(f"   {'PASS' if ok else 'FAIL'}  {gid}")
    print(f"eval-regrade: {applied} applied, {bad} failed — {os.path.relpath(case, ROOT)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
