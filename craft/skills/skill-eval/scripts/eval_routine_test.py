"""Tests for eval-routine.py with fake tools; no model calls.

Run: python3 -B -m unittest eval_routine_test (from scripts/).
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
NAME = os.environ.get("EVAL_ROUTINE", "eval-routine.py")  # another implementation to check against

TOOL = """#!/usr/bin/env python3
import os, sys, time
time.sleep(1)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "calls.log"), "a") as f:
    f.write("{name} " + " ".join(sys.argv[1:]) + "\\n")
print({out!r}, end="")
sys.exit({code})
"""


class EvalRoutineTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)
        shutil.copy(os.path.join(HERE, NAME), self.dir)
        shutil.copy(os.path.join(HERE, "evalroot.py"), self.dir)
        self.tool("lint-skills.py", "----\n0 error(s), 0 warning(s).\n")
        self.tool("eval-probe.py", "   PASS  p1\n   FAIL  p2\neval-probe: 2 probe(s); $0.04, 3s (haiku)\n")
        self.tool("eval-triggers.py", "eval-triggers: 1 case(s); $0.00, 0s (haiku)\n")
        self.tool("eval-hunt.py", "eval-hunt: 1 skill(s); $0.15, 9s (hunter sonnet)\n")

    def tool(self, name, out, code=0):
        path = os.path.join(self.dir, name)
        with open(path, "w") as f:
            f.write(TOOL.format(name=name, out=out, code=code))
        os.chmod(path, 0o755)

    def run_routine(self, *args):
        env = dict(os.environ, SKILL_EVAL_ROOT=self.dir)
        cmd = [os.path.join(self.dir, NAME), *args]
        if NAME.endswith(".py"):
            cmd = [sys.executable, "-B", *cmd]
        t0 = time.time()
        r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=60)
        return r.returncode, r.stdout, time.time() - t0

    def calls(self):
        path = os.path.join(self.dir, "calls.log")
        if not os.path.exists(path):
            return []
        with open(path) as f:
            return sorted(f.read().splitlines())

    def test_runs_the_tools_in_parallel_and_sums_the_cost(self):
        code, out, took = self.run_routine()

        self.assertEqual(0, code, out)
        lines = out.splitlines()
        self.assertEqual(["   FAIL  p2", "eval-probe: 2 probe(s); $0.04, 3s (haiku)",
                          "eval-triggers: 1 case(s); $0.00, 0s (haiku)",
                          "eval-hunt: 1 skill(s); $0.15, 9s (hunter sonnet)"], lines[:4])
        self.assertRegex(lines[4], r"^eval-routine: lint ok; \$0\.19; \d+s wall$")
        self.assertLess(took, 3.5)  # lint, then three one-second tools at once

    def test_passes_the_base_to_the_hunt(self):
        self.run_routine("--base", "HEAD~2")

        self.assertIn("eval-hunt.py --base HEAD~2", self.calls())
        self.assertIn("eval-probe.py ", self.calls())

    def test_default_base_is_head(self):
        self.run_routine()

        self.assertIn("eval-hunt.py --base HEAD", self.calls())

    def test_lint_error_stops_before_any_model_call(self):
        self.tool("lint-skills.py", "ERROR  g/skills/s: broken\n----\n1 error(s), 0 warning(s).\n", 1)

        code, out, _ = self.run_routine()

        self.assertEqual(1, code)
        self.assertEqual("ERROR  g/skills/s: broken\neval-routine: lint failed\n", out)
        self.assertEqual(["lint-skills.py ", "lint-skills.py "], self.calls())

    def test_failing_tool_fails_the_routine(self):
        self.tool("eval-triggers.py", "eval-triggers: 1 miss; $0.01, 1s\n", 1)

        code, out, _ = self.run_routine()

        self.assertEqual(1, code, out)
        self.assertIn("$0.20;", out)


if __name__ == "__main__":
    unittest.main()
