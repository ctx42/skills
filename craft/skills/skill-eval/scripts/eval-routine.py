#!/usr/bin/env python3
"""eval-routine.py: the routine check after a skill edit, in one command.

Lint first (free; a lint error stops here), then in parallel: every probe
(cached by input, so only changed skills cost anything), the trigger test
(free while no description changed), and the ambiguity hunt on the skills
whose text changed against --base (default HEAD, working tree). Wall time is
the slowest of the three, not their sum. Outputs print in order once all
finish. Agent-run cases and blind rounds are never part of it.

Usage:
  scripts/eval-routine.py                 against HEAD (uncommitted changes)
  scripts/eval-routine.py --base REF      against REF
Exit: non-zero when lint fails or any tool reports a FAIL, SPLIT, or split.
"""
import os
import re
import subprocess
import sys
import time

sys.dont_write_bytecode = True  # importing evalroot must not leave __pycache__ in the skill
from evalroot import ROOT  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def tool(name, *args):
    return [sys.executable, "-B", os.path.join(HERE, name), *args]


def main():
    os.environ["SKILL_EVAL_ROOT"] = ROOT
    args = sys.argv[1:]
    base = args[1] if args[:1] == ["--base"] and len(args) > 1 else "HEAD"
    t0 = time.time()
    if subprocess.run(tool("lint-skills.py"), capture_output=True).returncode != 0:
        out = subprocess.run(tool("lint-skills.py"), capture_output=True, text=True).stdout
        for line in out.splitlines():
            if line.startswith("ERR"):
                print(line)
        print("eval-routine: lint failed")
        return 1
    procs = [subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
             for cmd in (tool("eval-probe.py"), tool("eval-triggers.py"), tool("eval-hunt.py", "--base", base))]
    outs = [p.communicate()[0] for p in procs]
    rc = 1 if any(p.returncode for p in procs) else 0
    # Probes print one PASS line each; show only what is not a pass.
    probe, triggers, hunt = outs
    sys.stdout.write("".join(ln for ln in probe.splitlines(True) if not ln.startswith("   PASS ")))
    sys.stdout.write(triggers + hunt)
    cost = sum(float(m) for m in re.findall(r"\$([0-9]+\.[0-9]+), [0-9]+s", "".join(outs)))
    print(f"eval-routine: lint ok; ${cost:.2f}; {round(time.time() - t0)}s wall")
    return rc


if __name__ == "__main__":
    sys.exit(main())
