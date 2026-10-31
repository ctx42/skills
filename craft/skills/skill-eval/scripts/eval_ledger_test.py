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
    """Return a plugin-eval result JSON for (case, passed, error) runs."""
    return {"cases": [{"name": c, "arms": {"with": [{"passed": p, "error": e}]}} for c, p, e in runs]}


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.join(self.tmp.name, "repo")
        fake.make_repo(self.root, [("a", False), ("b", False)])
        self.env = dict(os.environ, SKILL_EVAL_ROOT=self.root, PYTHONDONTWRITEBYTECODE="1")

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
