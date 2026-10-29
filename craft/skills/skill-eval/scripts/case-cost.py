#!/usr/bin/env python3
"""Per-case cost of an agent-run round: dollars and turns from its results
JSON, tokens from each case's trace when it was kept.

eval-changed.sh deletes the trace of a passing case unless run with --keep, so
a plain round has tokens for its failures only.

Usage:
  scripts/case-cost.py tmp/eval-changed/<run>/          every results file in a run
  scripts/case-cost.py <results.json>...                named results files
"""
import glob
import json
import os
import sys

KEYS = {"input": "input_tokens", "cache_read": "cache_read_input_tokens",
        "cache_write": "cache_creation_input_tokens", "output": "output_tokens"}


def tokens(trace):
    """Token totals from the trace's last `result` line, or None."""
    found = None
    try:
        with open(trace) as f:
            for line in f:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if isinstance(d, dict) and d.get("type") == "result" and d.get("usage"):
                    found = {k: d["usage"].get(v, 0) for k, v in KEYS.items()}
    except OSError:
        return None
    return found


def rows(paths):
    """One row per case arm across the results files (or run dirs) given."""
    files = []
    for p in paths:
        files += sorted(glob.glob(os.path.join(p, "*.json"))) if os.path.isdir(p) else [p]
    out = []
    for f in files:
        with open(f) as fh:
            data = json.load(fh)
        # A failed case's workspace is deleted, but its trace is saved as
        # <run>/<group>/failed/<case>.trace.jsonl; the results file is
        # <run>/<group>-<kind>-<n>.json.
        group = os.path.basename(f).split("-")[0]
        for case in data.get("cases", []):
            saved = os.path.join(os.path.dirname(f), group, "failed", case["name"] + ".trace.jsonl")
            for arm in case.get("arms", {}).get("with", []):
                out.append({"case": case["name"], "passed": bool(arm.get("passed")),
                            "usd": arm.get("costUsd", 0), "turns": arm.get("turns", 0),
                            "tokens": tokens(arm.get("tracePath") or "") or tokens(saved)})
    return out


def render(rows):
    width = max((len(r["case"]) for r in rows), default=0)
    lines = []
    for r in rows:
        t = r["tokens"]
        tok = f"{sum(t.values())} tokens (out {t['output']})" if t else "no trace"
        lines.append(f"{'PASS' if r['passed'] else 'FAIL'}  {r['case']:<{width}}  "
                     f"${r['usd']:.2f}  {r['turns']} turns  {tok}")
    usd = sum(r["usd"] for r in rows)
    known = sum(1 for r in rows if r["tokens"])
    lines.append(f"case-cost: {len(rows)} case(s), ${usd:.2f}; tokens for {known} "
                 "(keep traces with --keep)")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    print(render(rows(sys.argv[1:])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
