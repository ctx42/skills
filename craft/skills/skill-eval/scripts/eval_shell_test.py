"""Tests for eval-shell.py against a fake `claude`; no model calls.

Run: python3 -B -m unittest eval_shell_test (from scripts/).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eval_fake as fake  # noqa: E402

CMD = [sys.executable, "-B", os.path.join(HERE, "eval-shell.py")]


class EvalShellTest(unittest.TestCase):
    def setUp(self):
        self.base = tempfile.mkdtemp()
        self.addCleanup(self.cleanup)
        self.root = os.path.join(self.base, "repo")
        self.bindir = os.path.join(self.base, "bin")
        self.plan = os.path.join(self.base, "plan.json")
        self.log = os.path.join(self.base, "claude.log")
        self.out = os.path.join(self.base, "out.json")
        fake.make_bin(self.bindir, os.path.join(self.base, "modcache"))

    def cleanup(self):
        subprocess.run(["chmod", "-R", "u+rwx", self.base], check=False)
        shutil.rmtree(self.base, ignore_errors=True)

    def repo(self, *names, plan=None):
        fake.make_repo(self.root, [(n, True) for n in names])
        with open(self.plan, "w") as f:
            json.dump(plan or {}, f)

    def grader(self, case, name, text):
        fake.write(os.path.join(self.root, fake.GROUP, "evals", case, "graders", name), text)

    def run_shell(self, *args, env=None):
        e = fake.env_for(self.base, self.root, self.bindir, self.plan, self.log)
        e.update(env or {})
        r = subprocess.run(CMD + [fake.GROUP, *args, "--json", self.out],
                           capture_output=True, text=True, env=e, timeout=60)
        with open(self.out) as f:
            return r.returncode, json.load(f), r.stderr

    def run_of(self, result, case):
        return next(c for c in result["cases"] if c["name"] == case)["arms"]["with"]

    def test_passing_case(self):
        self.repo("a")

        code, have, _ = self.run_shell("a")

        self.assertEqual(0, code)
        self.assertEqual({"casesPassed": 1, "casesTotal": 1}, have["aggregates"])
        run = self.run_of(have, "a")[0]
        self.assertTrue(run["passed"])
        self.assertEqual("claude-default-1", run["model"])
        self.assertEqual(0.5, run["costUsd"])
        self.assertEqual("OK", run["lastMessage"])
        self.assertEqual(0.5, have["costUsd"])

    def test_failing_case_keeps_its_trace(self):
        self.repo("a", plan={"a": {"result": "fail"}})

        code, have, _ = self.run_shell("a")

        self.assertEqual(1, code)
        run = self.run_of(have, "a")[0]
        self.assertFalse(run["passed"])
        self.assertEqual([{"name": "g1", "passed": False, "evidence": "no match"}], run["graders"])
        self.assertTrue(os.path.isfile(run["tracePath"]))

    def test_runs_and_jobs(self):
        self.repo("a", "b", plan={"b": {"results": ["pass", "fail"]}})

        code, have, _ = self.run_shell("a", "b", "--runs", "2", "-j", "2")

        self.assertEqual(1, code)
        self.assertEqual([True, True], [r["passed"] for r in self.run_of(have, "a")])
        self.assertEqual([True, False], [r["passed"] for r in self.run_of(have, "b")])
        self.assertEqual({"casesPassed": 1, "casesTotal": 2}, have["aggregates"])

    def test_cost_cap_stops_launches(self):
        self.repo("a", "b")

        code, have, _ = self.run_shell("a", "b", "--max-cost-usd", "0.4")

        self.assertEqual(2, code)
        self.assertEqual(["a"], [c["name"] for c in have["cases"]])

    def test_zero_cost_cap_runs_nothing(self):
        self.repo("a")

        code, have, _ = self.run_shell("a", "--max-cost-usd", "0")

        self.assertEqual(2, code)
        self.assertEqual([], have["cases"])
        self.assertEqual([], fake.calls(self.log))

    def test_explicit_model_reaches_claude(self):
        self.repo("a")

        self.run_shell("a", "--model", "claude-x-1")

        argv = fake.calls(self.log)[0]
        self.assertEqual("claude-x-1", argv[argv.index("--model") + 1])

    def test_default_model_passes_no_flag(self):
        self.repo("a")

        self.run_shell("a")

        self.assertNotIn("--model", fake.calls(self.log)[0])

    def test_usage_limit_is_an_error(self):
        self.repo("a", plan={"a": {"result": "limit"}})

        code, have, _ = self.run_shell("a")

        self.assertEqual(1, code)
        self.assertIn("usage limit", self.run_of(have, "a")[0]["error"])

    def test_timeout_is_an_error(self):
        self.repo("a", plan={"a": {"result": "hang"}})
        prompt = os.path.join(self.root, fake.GROUP, "evals", "a", "prompt.md")
        with open(prompt) as f:
            text = f.read()
        with open(prompt, "w") as f:
            f.write(text.replace("max_turns: 5\n", "max_turns: 5\ntimeout_seconds: 1\n"))

        code, have, _ = self.run_shell("a")

        self.assertEqual(1, code)
        self.assertEqual("timeout after 1s", self.run_of(have, "a")[0]["error"])

    def test_write_into_the_real_home_fails(self):
        home = os.path.join(self.base, "realhome")
        os.makedirs(home)
        self.repo("a", plan={"a": {"write": os.path.join(home, "x.md")}})

        code, have, _ = self.run_shell("a", env={"HOME": home})

        self.assertEqual(1, code)
        names = [g["name"] for g in self.run_of(have, "a")[0]["graders"] if not g["passed"]]
        self.assertEqual(["no-real-home-write"], names)

    def test_notice_is_stripped_before_grading(self):
        self.repo("a")
        self.grader("a", "g1.md", "---\ntype: regex\ntarget: last_message\n---\n^OK$\n")

        code, have, _ = self.run_shell("a", env={"EVAL_STRIP_NOTICE": "never-there"})

        self.assertEqual(0, code)

    def test_grader_types(self):
        self.repo("a", plan={"a": {"bash": "git status --short"}})
        for name, text in [
            ("g2.md", "---\ntype: regex\ntarget: trace\nmatch: count:1\n---\n\"name\": ?\"Bash\"\n"),
            ("g3.md", "---\ntype: tool_used\ntool: Bash\ninput_match: 'git\\s+status'\nmin: 1\nmax: 1\n---\n"),
            ("g4.md", "---\ntype: tool_used\ntool: Write\nmin: 0\nmax: 0\n---\n"),
            ("g5.md", "---\ntype: file_exists\npath: notes/*.md\nexists: false\n---\n"),
            ("g6.md", "---\ntype: regex\ntarget: last_message\nmatch: not_contains\nflags: \"i\"\n---\n^no$\n"),
        ]:
            self.grader("a", name, text)

        code, have, _ = self.run_shell("a")

        graders = self.run_of(have, "a")[0]["graders"]
        self.assertEqual(0, code, graders)
        self.assertEqual(["g1", "g2", "g3", "g4", "g5", "g6"], [g["name"] for g in graders])

    def test_file_target_that_is_missing_fails(self):
        self.repo("a")
        self.grader("a", "g2.md", "---\ntype: regex\ntarget: {source: file, path: out.md}\n---\nx\n")

        code, have, _ = self.run_shell("a")

        self.assertEqual(1, code)
        g2 = self.run_of(have, "a")[0]["graders"][1]
        self.assertEqual({"name": "g2", "passed": False, "evidence": "file out.md missing"}, g2)

    def test_scaffold_files_do_not_count_as_made(self):
        self.repo("a")
        case = os.path.join(self.root, fake.GROUP, "evals", "a")
        fake.write(os.path.join(case, "case.yaml"), "context:\n  scaffold_script: scaffold.sh\n")
        fake.write(os.path.join(case, "scaffold.sh"), "mkdir -p notes && echo x > notes/a.md\n")
        self.grader("a", "g2.md", "---\ntype: file_exists\npath: notes/*.md\n---\n")

        code, have, _ = self.run_shell("a")

        self.assertEqual(1, code)
        self.assertEqual("no notes/*.md", self.run_of(have, "a")[0]["graders"][1]["evidence"])

    def test_unknown_group_exits_1(self):
        self.repo("a")
        e = fake.env_for(self.base, self.root, self.bindir, self.plan, self.log)

        r = subprocess.run(CMD + ["nope", "a"], capture_output=True, text=True, env=e)

        self.assertEqual(1, r.returncode)
        self.assertIn("nope: not a plugin group", r.stderr)


if __name__ == "__main__":
    unittest.main()
