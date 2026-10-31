#!/usr/bin/env python3
"""Tests for eval-ledger.py. Run: python3 -B -m unittest eval_ledger_test (from scripts/)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eval_fake as fake  # noqa: E402

LEDGER = os.path.join(HERE, "eval-ledger.py")


def result(*runs):
    """Return a plugin-eval result JSON for (case, passed, error[, model[,
    trace]]) runs."""
    cases = []
    for c, p, e, *rest in runs:
        run = {"passed": p, "error": e}
        if rest and rest[0]:
            run["model"] = rest[0]
        if len(rest) > 1:
            run["tracePath"] = rest[1]
        cases.append({"name": c, "arms": {"with": [run]}})
    return {"cases": cases}


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = self.tmp.name
        self.root = os.path.join(base, "repo")
        fake.make_repo(self.root, [("a", False), ("b", False)])
        bindir = os.path.join(base, "bin")
        fake.make_bin(bindir, os.path.join(base, "modcache"))
        self.log = os.path.join(base, "claude.log")
        self.env = fake.env_for(base, self.root, bindir, os.path.join(base, "plan.json"), self.log)

    def model(self, *args):
        """Run `eval-ledger.py model`; return (exit code, stdout)."""
        r = subprocess.run([sys.executable, LEDGER, "model", *args], env=self.env,
                           capture_output=True, text=True)
        return r.returncode, r.stdout.strip()

    def test_model_probe_resolves_the_default_model(self):
        code, have = self.model("default")

        self.assertEqual(0, code)
        self.assertEqual("claude-default-1", have)
        self.assertNotIn("--model", fake.calls(self.log)[0])

    def test_model_probe_passes_a_named_model(self):
        code, have = self.model("sonnet")

        self.assertEqual(0, code)
        self.assertEqual("sonnet", have)
        argv = fake.calls(self.log)[0]
        self.assertEqual("sonnet", argv[argv.index("--model") + 1])

    def test_model_cached_reads_the_last_probe_without_a_call(self):
        self.model("default")

        code, have = self.model("default", "--cached")

        self.assertEqual(0, code)
        self.assertEqual("claude-default-1", have)
        self.assertEqual(1, len(fake.calls(self.log)))

    def test_model_cached_without_a_probe_prints_nothing(self):
        code, have = self.model("default", "--cached")

        self.assertEqual(0, code)
        self.assertEqual("", have)
        self.assertEqual([], fake.calls(self.log))

    def test_model_probe_cut_off_by_the_usage_limit_exits_3(self):
        self.env["FAKE_CLAUDE_PROBE"] = "limit"

        code, have = self.model("default")

        self.assertEqual(3, code)
        self.assertEqual("", have)

    def test_record_skips_a_run_on_another_model(self):
        self.record("m1", ("a", True, None))

        have = self.record("m1", ("a", False, None, "m2"), ("b", True, None, "m2"))

        self.assertEqual(["MODEL", "a", "m2", "MODEL", "b", "m2"], have)
        self.assertEqual(["b"], self.pending("m1"))

    def test_record_reads_the_model_from_the_trace(self):
        trace = os.path.join(self.tmp.name, "trace.jsonl")
        with open(trace, "w") as f:
            f.write(json.dumps({"type": "result", "modelUsage": {"m2": {"costUSD": 1}}}) + "\n")

        have = self.record("m1", ("a", True, None, None, trace))

        self.assertEqual(["MODEL", "a", "m2"], have)
        self.assertEqual(["a", "b"], self.pending("m1"))

    def tearDown(self):
        self.tmp.cleanup()

    def ledger(self, *args):
        """Run eval-ledger.py against the fake repo; return its stdout lines."""
        r = subprocess.run([sys.executable, LEDGER, *args], env=self.env,
                           capture_output=True, text=True, check=True)
        return r.stdout.split()

    def record(self, model, *runs):
        """Record a result for the given runs; return eval-ledger.py's output."""
        path = os.path.join(self.tmp.name, "result.json")
        with open(path, "w") as f:
            json.dump(result(*runs), f)
        return self.ledger("record", fake.GROUP, model, path)

    def pending(self, model="sonnet"):
        return self.ledger("pending", fake.GROUP, model, "a", "b")

    def test_pending_lists_cases_without_a_pass(self):
        have = self.pending()

        self.assertEqual(["a", "b"], have)

    def test_record_stores_a_pass(self):
        self.record("sonnet", ("a", True, None))

        have = self.pending()

        self.assertEqual(["b"], have)

    def test_record_prints_a_fail_and_keeps_it_pending(self):
        have = self.record("sonnet", ("a", False, None))

        self.assertEqual(["FAIL", "a"], have)
        self.assertEqual(["a", "b"], self.pending())

    def test_record_counts_usage_limits_without_storing_them(self):
        have = self.record("sonnet", ("a", False, "usage limit reached"), ("b", True, None))

        self.assertEqual(["LIMIT", "1"], have)
        self.assertEqual(["a"], self.pending())

    def test_failed_run_clears_the_pass(self):
        self.record("sonnet", ("a", True, None))

        self.record("sonnet", ("a", False, None))

        self.assertEqual(["a", "b"], self.pending())

    def test_runner_error_clears_the_pass(self):
        self.record("sonnet", ("a", True, None))

        self.record("sonnet", ("a", False, "timeout after 300s"))

        self.assertEqual(["a", "b"], self.pending())

    def test_usage_limit_keeps_the_pass(self):
        self.record("sonnet", ("a", True, None))

        self.record("sonnet", ("a", False, "usage limit reached"))

        self.assertEqual(["b"], self.pending())

    def test_pass_is_per_model(self):
        self.record("sonnet", ("a", True, None))

        have = self.pending("default")

        self.assertEqual(["a", "b"], have)

    def test_case_edit_makes_a_pass_pending(self):
        self.record("sonnet", ("a", True, None))
        fake.write(os.path.join(self.root, fake.GROUP, "evals", "a", "graders", "g1.md"),
                   "---\ntype: regex\ntarget: last_message\n---\n^YES\n")

        have = self.pending()

        self.assertEqual(["a", "b"], have)

    def test_tagged_skill_edit_makes_a_pass_pending(self):
        self.record("sonnet", ("a", True, None))
        with open(os.path.join(self.root, fake.GROUP, "skills", fake.SKILL, "SKILL.md"), "a") as f:
            f.write("\nMore.\n")

        have = self.pending()

        self.assertEqual(["a", "b"], have)

    def test_edit_outside_the_key_keeps_the_pass(self):
        self.record("sonnet", ("a", True, None))
        fake.write(os.path.join(self.root, fake.GROUP, "skills", "other", "SKILL.md"), "# other\n")
        fake.write(os.path.join(self.root, fake.GROUP, "skills", fake.SKILL, "evals", "x.json"), "{}\n")

        have = self.pending()

        self.assertEqual(["b"], have)


if __name__ == "__main__":
    unittest.main()
