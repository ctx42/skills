#!/usr/bin/env python3
"""Tests for eval-changed.sh against a fake repo and a fake `claude`.

Run: python3 -B -m unittest eval_changed_test (from scripts/). Needs bash,
git, and node; no network, no logged-in `claude`, no model spend.
"""
import glob
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
        """Return the cases with a pass in the ledger, as `<group>/<case>`."""
        path = os.path.join(self.root, "tmp", "eval-ledger.json")
        if not os.path.exists(path):
            return set()
        with open(path) as f:
            return {k.split("@")[0] for k, e in json.load(f).items() if isinstance(e, dict) and e.get("key")}

    def case_calls(self):
        """Return the fake `claude` calls that ran cases, leaving out the probe."""
        return [a for a in fake.calls(self.log)
                if a[:2] == ["plugin", "eval"] or ("-p" in a and "CASE:" in a[a.index("-p") + 1])]

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
        for argv in self.case_calls():
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
        self.assertEqual({"grp/a", "grp/b", "grp/c"}, self.ledger())

    def test_shell_case_runs_through_eval_shell(self):
        self.repo(("a", True))

        code, out = self.run_changed("--all", fake.GROUP)

        self.assertEqual(0, code, out)
        self.assertIn("PASS  a", out)
        have = [a for a in self.case_calls() if "-p" in a]
        self.assertEqual(1, len(have))
        self.assertIn("CASE:a", have[0][have[0].index("-p") + 1])
        self.assertEqual([], self.plugin_eval_tags())
        self.assertEqual({"grp/a"}, self.ledger())

    def test_ledger_skips_a_case_that_passed(self):
        self.repo(("a", False), ("b", True))
        self.run_changed("--all", fake.GROUP)
        n = len(self.case_calls())

        code, out = self.run_changed("--all", fake.GROUP)

        self.assertEqual(0, code, out)
        self.assertIn("== grp: 2 case(s), 2 PASS in the ledger, 0 to run", out)
        self.assertEqual(n, len(self.case_calls()))

    def test_fresh_ignores_the_ledger(self):
        self.repo(("a", False))
        self.run_changed("--all", fake.GROUP)

        code, out = self.run_changed("--all", fake.GROUP, "--fresh")

        self.assertEqual(0, code, out)
        self.assertEqual([["case:a"], ["case:a"]], self.plugin_eval_tags())

    def test_default_run_resolves_the_model_for_both_runners(self):
        self.repo(("a", False), ("b", True))

        code, out = self.run_changed("--all", fake.GROUP)

        self.assertEqual(0, code, out)
        probe = fake.calls(self.log)[0]
        self.assertIn("-p", probe)
        self.assertNotIn("--model", probe)
        have = self.case_calls()
        self.assertEqual(2, len(have))
        for argv in have:
            self.assertEqual("claude-default-1", argv[argv.index("--model") + 1])
        self.assertIn("model claude-default-1", out)

    def test_new_default_model_reruns_passed_cases(self):
        self.repo(("a", False))
        self.run_changed("--all", fake.GROUP)
        self.env["FAKE_CLAUDE_DEFAULT_MODEL"] = "claude-default-2"

        code, out = self.run_changed("--all", fake.GROUP)

        self.assertEqual(0, code, out)
        self.assertEqual([["case:a"], ["case:a"]], self.plugin_eval_tags())

    def test_dry_run_reads_the_cached_model(self):
        self.repo(("a", False))
        self.run_changed("--all", fake.GROUP)
        n = len(fake.calls(self.log))

        code, out = self.run_changed("--all", fake.GROUP, "--dry-run")

        self.assertEqual(0, code, out)
        self.assertIn("1 PASS in the ledger, 0 to run", out)
        self.assertIn("model claude-default-1", out)
        self.assertEqual(n, len(fake.calls(self.log)))

    def test_run_on_a_fallback_model_records_no_pass(self):
        self.repo(("a", False), ("b", True))
        self.env["FAKE_CLAUDE_RUN_MODEL"] = "claude-fallback-1"

        code, out = self.run_changed("--all", fake.GROUP)

        self.assertIn("ran on claude-fallback-1, not claude-default-1", out)
        self.assertEqual(set(), self.ledger())

    def test_probe_cut_off_by_the_usage_limit_exits_3(self):
        self.repo(("a", False))
        self.env["FAKE_CLAUDE_PROBE"] = "limit"

        code, out = self.run_changed("--all", fake.GROUP)

        self.assertEqual(3, code, out)
        self.assertEqual([], self.case_calls())

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
        self.assertIn("2 to run, ~$3.25-9.80 (Opus, measured 2026-10-04)", out)

    def test_estimate_uses_the_cost_of_the_last_run(self):
        self.repo(("a", False))
        self.run_changed("--all", fake.GROUP)
        fake.write(os.path.join(self.root, fake.GROUP, "evals", "a", "graders", "g2.md"),
                   "---\ntype: regex\ntarget: last_message\n---\nO\n")

        code, out = self.run_changed("--all", fake.GROUP, "--dry-run")

        self.assertEqual(0, code, out)
        # The edited case runs twice, at its stored cost each time.
        self.assertIn("1 to run, ~$1.00 (measured on claude-default-1)", out)
        self.assertIn("   a (2 runs)\n", out)

    def test_capped_plugin_eval_chunk_records_no_pass(self):
        self.repo(("a", False))

        code, out = self.run_changed("--all", fake.GROUP, "--max-usd", "0.1")

        self.assertEqual(1, code, out)
        self.assertEqual(set(), self.ledger())

    def test_capped_plugin_eval_chunk_clears_no_pass(self):
        self.repo(("a", False))
        self.run_changed("--all", fake.GROUP)
        with open(self.plan, "w") as f:
            json.dump({"a": {"result": "fail"}}, f)

        code, out = self.run_changed("--all", fake.GROUP, "--fresh", "--max-usd", "0.1")

        self.assertEqual(1, code, out)
        self.assertEqual({"grp/a"}, self.ledger())

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
        self.assertEqual(set(), self.ledger())

    def test_cap_inside_a_shell_chunk_records_its_finished_passes(self):
        self.repo(("a", True), ("b", True))

        code, out = self.run_changed("--all", fake.GROUP, "-j", "1", "--max-usd", "0.1")

        self.assertEqual(1, code, out)
        self.assertIn("not started (--max-usd 0.1 spent): b", out)
        self.assertEqual({"grp/a"}, self.ledger())

    def shell_results(self):
        """Return {case: run} from every eval-shell result JSON of the runs."""
        out = {}
        for path in glob.glob(os.path.join(self.root, "tmp", "eval-changed", "*", "grp-shell*.json")):
            with open(path) as f:
                for c in json.load(f)["cases"]:
                    out[c["name"]] = c["arms"]["with"][0]
        return out

    def test_shell_result_names_the_model_that_ran(self):
        self.repo(("a", True))

        code, out = self.run_changed("--all", fake.GROUP)

        self.assertEqual(0, code, out)
        self.assertEqual("claude-default-1", self.shell_results()["a"]["model"])

    def home(self):
        """Point $HOME at a fresh dir under the test's temp dir; return it."""
        home = os.path.join(self.tmp.name, "home")
        os.makedirs(home, exist_ok=True)
        self.env["HOME"] = home
        return home

    def test_shell_case_that_writes_into_the_real_home_fails(self):
        path = os.path.join(self.home(), ".agent-data", "lessons", "x.md")
        self.repo(("a", True), plan={"a": {"write": path}})

        code, out = self.run_changed("--all", fake.GROUP)

        self.assertEqual(1, code, out)
        self.assertIn("FAIL  a", out)
        self.assertIn(f"wrote into the real home: {path}", out)
        self.assertEqual(set(), self.ledger())

    def test_shell_case_that_runs_bash_on_the_real_home_fails(self):
        cmd = f"wc -l {self.home()}/.agent-data/lessons/x.md"
        self.repo(("a", True), plan={"a": {"bash": cmd}})

        code, out = self.run_changed("--all", fake.GROUP)

        self.assertEqual(1, code, out)
        self.assertIn(f"ran Bash on the real home: {cmd}", out)
        self.assertEqual(set(), self.ledger())

    def test_shell_case_whose_home_write_was_refused_passes(self):
        path = os.path.join(self.home(), ".agent-data", "lessons", "x.md")
        self.repo(("a", True), plan={"a": {"write": path, "write_error": True}})

        code, out = self.run_changed("--all", fake.GROUP)

        self.assertEqual(0, code, out)
        self.assertEqual({"grp/a"}, self.ledger())

    def test_shell_run_denies_edits_in_the_real_home(self):
        home = self.home()
        self.repo(("a", True))

        code, out = self.run_changed("--all", fake.GROUP)

        self.assertEqual(0, code, out)
        have = [a for a in self.case_calls() if "-p" in a][0]
        i = have.index("--disallowedTools")
        self.assertEqual(f"Edit(/{home}/**)", have[i + 1])

    def commit(self):
        git = ["git", "-C", self.root, "-c", "user.name=t", "-c", "user.email=t@example.com"]
        subprocess.run(git + ["add", "-A"], check=True)
        subprocess.run(git + ["commit", "-q", "-m", "edit"], check=True)

    def runs_per_case(self):
        """Return {case: --runs} over the plugin-eval calls."""
        out = {}
        for argv in fake.calls(self.log):
            if argv[:2] == ["plugin", "eval"]:
                n = int(argv[argv.index("--runs") + 1])
                for i, t in enumerate(argv):
                    if argv[i - 1] == "--tag":
                        out[t.split(":", 1)[1]] = n
        return out

    def test_committed_case_without_an_entry_runs_once(self):
        self.repo(("a", False))

        code, out = self.run_changed("--all", fake.GROUP)

        self.assertEqual(0, code, out)
        self.assertEqual({"a": 1}, self.runs_per_case())

    def test_new_uncommitted_case_runs_twice(self):
        self.repo(("a", False))
        fake.add_case(self.root, "n")

        code, out = self.run_changed("--all", fake.GROUP)

        self.assertEqual(0, code, out)
        self.assertEqual({"a": 1, "n": 2}, self.runs_per_case())
        self.assertEqual({"grp/a", "grp/n"}, self.ledger())

    def test_case_edited_since_its_verdict_runs_twice(self):
        self.repo(("a", False))
        self.run_changed("--all", fake.GROUP)
        fake.write(os.path.join(self.root, fake.GROUP, "evals", "a", "graders", "g2.md"),
                   "---\ntype: regex\ntarget: last_message\n---\nO\n")
        self.commit()
        os.remove(self.log)

        code, out = self.run_changed("--all", fake.GROUP)

        self.assertEqual(0, code, out)
        self.assertEqual({"a": 2}, self.runs_per_case())

    def test_split_twice_run_records_no_pass(self):
        self.repo(("a", False), plan={"n": {"results": ["pass", "fail"]}})
        fake.add_case(self.root, "n")

        code, out = self.run_changed("--all", fake.GROUP)

        self.assertEqual(1, code, out)
        self.assertEqual({"grp/a"}, self.ledger())

    def test_new_shell_case_runs_twice(self):
        self.repo(("a", True))
        fake.add_case(self.root, "n", True)

        code, out = self.run_changed("--all", fake.GROUP)

        self.assertEqual(0, code, out)
        have = [a[a.index("-p") + 1] for a in self.case_calls() if "-p" in a]
        self.assertEqual(1, sum("CASE:a" in p for p in have))
        self.assertEqual(2, sum("CASE:n" in p for p in have))
        self.assertEqual({"grp/a", "grp/n"}, self.ledger())

    def test_usage_limit_stops_the_run_with_exit_3(self):
        self.repo(("a", False), ("b", False), ("c", False), plan={"b": {"result": "limit"}})

        code, out = self.run_changed("--all", fake.GROUP, "-j", "1")

        self.assertEqual(3, code, out)
        self.assertIn("LIMIT: the usage limit cut off 1 run(s); 1 case(s) not started.", out)
        self.assertEqual([["case:a", "case:b"]], self.plugin_eval_tags())
        self.assertEqual({"grp/a"}, self.ledger())


if __name__ == "__main__":
    unittest.main()
