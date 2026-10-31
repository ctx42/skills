#!/usr/bin/env python3
"""Tests for eval-changed.sh against a fake repo and a fake `claude`.

Run: python3 -B -m unittest eval_changed_test (from scripts/). Needs bash,
git, and node; no network, no logged-in `claude`, no model spend.
"""
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


class EvalChangedTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = self.tmp.name
        self.root = os.path.join(base, "repo")
        self.scripts = fake.copy_scripts(os.path.join(base, "scripts"))
        bindir = os.path.join(base, "bin")
        fake.make_bin(bindir, os.path.join(base, "modcache"))
        self.plan = os.path.join(base, "plan.json")
        self.log = os.path.join(base, "claude.log")
        self.env = fake.env_for(base, self.root, bindir, self.plan, self.log)

    def tearDown(self):
        # Runs leave read-only copies of the plugin; unseal before deleting.
        subprocess.run(["chmod", "-R", "u+rwx", self.tmp.name], stderr=subprocess.DEVNULL)
        self.tmp.cleanup()

    def repo(self, *cases, plan=None):
        """Build the fake repo from (name, shell) pairs and write the plan."""
        fake.make_repo(self.root, list(cases))
        with open(self.plan, "w") as f:
            json.dump(plan or {}, f)

    def run_changed(self, *args):
        """Run eval-changed.sh in the fake repo; return (exit code, output)."""
        r = subprocess.run(["bash", os.path.join(self.scripts, "eval-changed.sh"), *args],
                           cwd=self.root, env=self.env, capture_output=True, text=True, timeout=120)
        return r.returncode, r.stdout + r.stderr

    def ledger(self):
        path = os.path.join(self.root, "tmp", "eval-ledger.json")
        if not os.path.exists(path):
            return {}
        with open(path) as f:
            return json.load(f)

    def plugin_eval_tags(self):
        """Return the case tags of each `claude plugin eval` call, in order."""
        return [[a[i + 1] for i, x in enumerate(a) if x == "--tag"]
                for a in fake.calls(self.log) if a[:2] == ["plugin", "eval"]]

    def test_dry_run_lists_cases_and_runs_nothing(self):
        self.repo(("a", False), ("b", True))

        code, out = self.run_changed("--all", fake.GROUP, "--dry-run")

        self.assertEqual(0, code, out)
        self.assertIn("== grp: 2 case(s), 0 PASS in the ledger, 2 to run", out)
        self.assertIn("   a\n", out)
        self.assertIn("   b\n", out)
        self.assertEqual([], fake.calls(self.log))

    def test_dry_run_lists_fan_out_cases_last(self):
        self.repo(("a", True, True), ("b", True), ("c", False), ("d", False, True))

        code, out = self.run_changed("--all", fake.GROUP, "--dry-run")

        self.assertEqual(0, code, out)
        have = [ln.strip() for ln in out.splitlines() if ln.startswith("   ")]
        self.assertEqual(["c", "b", "d", "a"], have)

    def test_fan_out_cases_run_last(self):
        self.repo(("a", True, True), ("b", True), ("c", False), ("d", False, True))

        code, out = self.run_changed("--all", fake.GROUP)

        self.assertEqual(0, code, out)
        have = []
        for argv in fake.calls(self.log):
            if argv[:2] == ["plugin", "eval"]:
                have += [t.split(":", 1)[1] for i, t in enumerate(argv) if argv[i - 1] == "--tag"]
            else:
                have.append(argv[argv.index("-p") + 1].split("CASE:", 1)[1].strip())
        self.assertEqual(["c", "b", "d", "a"], have)

    def test_plain_cases_run_in_chunks_of_twice_j(self):
        self.repo(("a", False), ("b", False), ("c", False))

        code, out = self.run_changed("--all", fake.GROUP, "-j", "1")

        self.assertEqual(0, code, out)
        want = [["case:a", "case:b"], ["case:c"]]
        self.assertEqual(want, self.plugin_eval_tags())
        self.assertEqual({"grp/a", "grp/b", "grp/c"}, set(self.ledger()))

    def test_shell_case_runs_through_eval_shell(self):
        self.repo(("a", True))

        code, out = self.run_changed("--all", fake.GROUP)

        self.assertEqual(0, code, out)
        self.assertIn("PASS  a", out)
        have = [a for a in fake.calls(self.log) if "-p" in a]
        self.assertEqual(1, len(have))
        self.assertIn("CASE:a", have[0][have[0].index("-p") + 1])
        self.assertEqual([], self.plugin_eval_tags())
        self.assertEqual({"grp/a"}, set(self.ledger()))

    def test_ledger_skips_a_case_that_passed(self):
        self.repo(("a", False), ("b", True))
        self.run_changed("--all", fake.GROUP)
        n = len(fake.calls(self.log))

        code, out = self.run_changed("--all", fake.GROUP)

        self.assertEqual(0, code, out)
        self.assertIn("== grp: 2 case(s), 2 PASS in the ledger, 0 to run", out)
        self.assertEqual(n, len(fake.calls(self.log)))

    def test_fresh_ignores_the_ledger(self):
        self.repo(("a", False))
        self.run_changed("--all", fake.GROUP)

        code, out = self.run_changed("--all", fake.GROUP, "--fresh")

        self.assertEqual(0, code, out)
        self.assertEqual([["case:a"], ["case:a"]], self.plugin_eval_tags())

    def test_default_run_passes_no_model_to_either_runner(self):
        self.repo(("a", False), ("b", True))

        code, out = self.run_changed("--all", fake.GROUP)

        self.assertEqual(0, code, out)
        have = fake.calls(self.log)
        self.assertEqual(2, len(have))
        for argv in have:
            self.assertNotIn("--model", argv)

    def test_explicit_model_reaches_both_runners(self):
        self.repo(("a", False), ("b", True))

        code, out = self.run_changed("--all", fake.GROUP, "--model", "sonnet")

        self.assertEqual(0, code, out)
        for argv in fake.calls(self.log):
            self.assertEqual("sonnet", argv[argv.index("--model") + 1])

    def test_sonnet_run_does_not_rerun_its_fails(self):
        self.repo(("a", False), plan={"a": {"result": "fail"}})

        code, out = self.run_changed("--all", fake.GROUP, "--model", "sonnet")

        self.assertEqual(1, code, out)
        self.assertEqual([["case:a"]], self.plugin_eval_tags())
        self.assertNotIn("confirming", out)

    def test_estimate_uses_the_labeled_opus_bands(self):
        self.repo(("a", False), ("b", True, True))

        code, out = self.run_changed("--all", fake.GROUP, "--dry-run")

        self.assertEqual(0, code, out)
        self.assertIn("2 to run, ~$3-10 (Opus, measured 2026-10-04)", out)

    def test_capped_plugin_eval_chunk_records_no_pass(self):
        self.repo(("a", False))

        code, out = self.run_changed("--all", fake.GROUP, "--max-usd", "0.1")

        self.assertEqual(1, code, out)
        self.assertEqual({}, self.ledger())

    def test_capped_plugin_eval_chunk_clears_no_pass(self):
        self.repo(("a", False))
        self.run_changed("--all", fake.GROUP)
        with open(self.plan, "w") as f:
            json.dump({"a": {"result": "fail"}}, f)

        code, out = self.run_changed("--all", fake.GROUP, "--fresh", "--max-usd", "0.1")

        self.assertEqual(1, code, out)
        self.assertEqual({"grp/a"}, set(self.ledger()))

    def test_cap_before_a_chunk_names_every_unstarted_case(self):
        self.repo(("a", False), ("b", False), ("c", False), ("d", False), ("e", True))

        code, out = self.run_changed("--all", fake.GROUP, "-j", "1", "--max-usd", "1.0")

        self.assertEqual(1, code, out)
        self.assertIn("not started (--max-usd 1.0 spent): c d e", out)
        self.assertEqual(1, out.count("not started"), out)
        self.assertEqual([["case:a", "case:b"]], self.plugin_eval_tags())

    def test_cap_inside_a_plain_chunk_names_its_unstarted_cases(self):
        self.repo(("a", False), ("b", False), ("c", False))

        code, out = self.run_changed("--all", fake.GROUP, "--max-usd", "0.6")

        self.assertEqual(1, code, out)
        self.assertIn("not started (--max-usd 0.6 spent): c", out)
        self.assertEqual({}, self.ledger())

    def test_cap_inside_a_shell_chunk_records_its_finished_passes(self):
        self.repo(("a", True), ("b", True))

        code, out = self.run_changed("--all", fake.GROUP, "-j", "1", "--max-usd", "0.1")

        self.assertEqual(1, code, out)
        self.assertIn("not started (--max-usd 0.1 spent): b", out)
        self.assertEqual({"grp/a"}, set(self.ledger()))

    def test_usage_limit_stops_the_run_with_exit_3(self):
        self.repo(("a", False), ("b", False), ("c", False), plan={"b": {"result": "limit"}})

        code, out = self.run_changed("--all", fake.GROUP, "-j", "1")

        self.assertEqual(3, code, out)
        self.assertIn("LIMIT: the usage limit cut off 1 run(s); 1 case(s) not started.", out)
        self.assertEqual([["case:a", "case:b"]], self.plugin_eval_tags())
        self.assertEqual({"grp/a"}, set(self.ledger()))


if __name__ == "__main__":
    unittest.main()
