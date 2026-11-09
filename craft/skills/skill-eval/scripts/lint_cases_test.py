"""Tests for lint-cases.py. Run: python3 -B -m unittest lint_cases_test (from scripts/).

Each test builds a small repo whose one case is valid, breaks one thing, and
checks the line lint-cases prints for it.
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
CMD = [sys.executable, "-B", os.path.join(HERE, "lint-cases.py")]
ENGLISH = "The user writes English; reply in English."

PROMPT = """---
tags: [{tags}]
allowed_tools: [{tools}]
append_system_prompt: |
  {english}
max_turns: {turns}
timeout_seconds: {timeout}
---
Do the thing.
"""


class Repo:
    """A repo with group g, skill s, scenario "Basic", and its case."""

    def __init__(self, test):
        self.root = tempfile.mkdtemp()
        test.addCleanup(shutil.rmtree, self.root)
        self.write("g/.claude-plugin/plugin.json", "{}")
        self.write("g/skills/s/SKILL.md", "---\nname: s\n---\n\n## Usage\n\nText.\n")
        self.json("g/skills/s/evals/evals.json", {"evals": [{"name": "Basic"}]})
        self.json("g/skills/s/evals/expectations.json",
                  {"expectations": [{"name": "Basic", "expected_behavior": ["does it"]}]})
        self.prompt()
        self.grader("b1-done.md", "---\ntype: regex\ntarget: last_message\n---\ndone\n")

    def path(self, rel):
        return os.path.join(self.root, rel)

    def write(self, rel, text):
        os.makedirs(os.path.dirname(self.path(rel)), exist_ok=True)
        with open(self.path(rel), "w") as f:
            f.write(text)

    def json(self, rel, obj):
        self.write(rel, json.dumps(obj))

    def prompt(self, case="s--basic", tags=None, tools="Read", english=ENGLISH,
               turns="20", timeout="300"):
        tags = f"case:{case}, skill:s" if tags is None else tags
        self.write(f"g/evals/{case}/prompt.md", PROMPT.format(
            tags=tags, tools=tools, english=english, turns=turns, timeout=timeout))

    def grader(self, name, text, case="s--basic"):
        self.write(f"g/evals/{case}/graders/{name}", text)

    def lint(self):
        env = dict(os.environ, SKILL_EVAL_ROOT=self.root)
        r = subprocess.run(CMD, capture_output=True, text=True, env=env)
        return r.returncode, r.stdout


class LintCasesTest(unittest.TestCase):
    def lint(self, repo):
        code, out = repo.lint()
        return code, out.splitlines()

    def assert_line(self, repo, level, text):
        code, lines = self.lint(repo)
        hits = [ln for ln in lines if ln.startswith(level) and text in ln]
        self.assertTrue(hits, "\n".join(lines))
        if level == "ERROR":
            self.assertEqual(1, code)
        return lines

    def test_valid_repo(self):
        have, lines = self.lint(Repo(self))

        self.assertEqual(0, have, lines)
        self.assertEqual(["cases: 0 error(s), 0 warning(s)"], lines)

    def test_tags(self):
        for tags, want in [
            ("skill:s", "tags lack case:s--basic"),
            ("case:s--basic, case:s--other, skill:s", "foreign case tag case:s--other"),
            ("case:s--basic, skill:nope", "tag skill:nope names no skill"),
            ("case:s--basic, sec:s:missing", "tag sec:s:missing names no skill"),
            ("case:s--basic, ref:s/missing", "tag ref:s/missing names no skill"),
            ("case:s--basic, odd", "unknown tag odd"),
        ]:
            with self.subTest(tags=tags):
                repo = Repo(self)
                repo.prompt(tags=tags)

                self.assert_line(repo, "ERROR", want)

    def test_known_tags_pass(self):
        repo = Repo(self)
        repo.write("g/skills/s/references/guide.md", "x\n")
        repo.prompt(tags="case:s--basic, skill:s, sec:s:usage, ref:s/guide, long")

        have, lines = self.lint(repo)

        self.assertEqual(0, have, lines)

    def test_bash_and_needs_shell_go_together(self):
        repo = Repo(self)
        repo.prompt(tools="Read, Bash(git:*)")
        self.assert_line(repo, "ERROR", "allowed_tools has Bash but tags lack needs-shell")

        repo = Repo(self)
        repo.prompt(tags="case:s--basic, skill:s, needs-shell")
        self.assert_line(repo, "ERROR", "tagged needs-shell but allowed_tools has no Bash")

    def test_skill_that_injects_shell_output_needs_shell(self):
        repo = Repo(self)
        repo.write("g/skills/s/SKILL.md", "## Usage\n\nNow: !`date`\n")

        self.assert_line(repo, "ERROR", "skill s injects shell output")

    def test_append_system_prompt(self):
        repo = Repo(self)
        repo.write("g/evals/s--basic/prompt.md",
                   "---\ntags: [case:s--basic]\nmax_turns: 20\ntimeout_seconds: 300\n---\n")
        self.assert_line(repo, "ERROR", "no append_system_prompt")

        repo = Repo(self)
        repo.prompt(english="Reply in French.")
        self.assert_line(repo, "ERROR", "append_system_prompt does not open with")

    def test_limits(self):
        for kw, want in [
            ({"turns": "0"}, "max_turns missing"),
            ({"turns": "81"}, "max_turns 81 > 80"),
            ({"timeout": "x"}, "timeout_seconds missing"),
            ({"timeout": "301"}, "timeout_seconds 301 > 300"),
            ({"timeout": "601", "tags": "case:s--basic, fan-out"}, "timeout_seconds 601 > 600"),
        ]:
            with self.subTest(**kw):
                repo = Repo(self)
                repo.prompt(**kw)

                self.assert_line(repo, "ERROR", want)

    def test_fan_out_allows_600(self):
        repo = Repo(self)
        repo.prompt(tags="case:s--basic, fan-out", timeout="600")

        have, lines = self.lint(repo)

        self.assertEqual(0, have, lines)

    def test_needs_shell_case_limits(self):
        shell = "case:s--basic, skill:s, needs-shell"
        repo = Repo(self)
        repo.prompt(tags=shell, tools="Read, Bash(git:*)")
        repo.write("g/evals/s--basic/mocks/x.json", "{}")
        self.assert_line(repo, "ERROR", "which serves no mocks")

        repo = Repo(self)
        repo.prompt(tags=shell, tools="Read, Bash(git:*)")
        repo.grader("b1-judge.md", "---\ntype: llm\n---\nJudge it.\n")
        self.assert_line(repo, "ERROR", "which grades only")

        repo = Repo(self)
        repo.prompt(tags=shell, tools="Read, Bash(git:*)")
        repo.grader("b1-mock.md", "---\ntype: regex\ntarget: mock_calls\n---\nx\n")
        self.assert_line(repo, "ERROR", "no mock_calls target")

    def test_graders(self):
        for name, text, want in [
            ("b1-x.md", "---\ntarget: trace\n---\nx\n", "no type"),
            ("b1-x.md", "---\ntype: regex\n---\n", "empty pattern"),
            ("b1-x.md", "---\ntype: tool_used\ntool: Bash\nmax: 0\n---\n", "max: 0 on Bash"),
            ("b1-x.md", "---\ntype: regex\n---\n(\n", "b1-x.md"),
            ("b1-x.md", "---\ntype: regex\n---\nfoo\\Z\n", "b1-x.md"),
            ("b1-x.md", "---\ntype: tool_used\ntool: Read\ninput_match: '('\n---\n", "input_match"),
        ]:
            with self.subTest(text=text):
                repo = Repo(self)
                repo.grader(name, text)

                self.assert_line(repo, "ERROR", want)

    def test_no_positive_grader(self):
        repo = Repo(self)
        repo.grader("b1-done.md", "---\ntype: regex\nmatch: not_contains\n---\nerror\n")

        self.assert_line(repo, "ERROR", "no grader asserts that something happened")

    def test_no_graders_dir(self):
        repo = Repo(self)
        shutil.rmtree(repo.path("g/evals/s--basic/graders"))

        self.assert_line(repo, "ERROR", "no graders/")

    def test_scenarios_and_cases_match(self):
        repo = Repo(self)
        repo.prompt(case="s--stray", tags="case:s--stray, skill:s")
        repo.grader("b1-done.md", "---\ntype: regex\n---\ndone\n", case="s--stray")
        self.assert_line(repo, "ERROR", "no evals.json scenario s--stray")

        repo = Repo(self)
        repo.json("g/skills/s/evals/evals.json", {"evals": [{"name": "Basic"}, {"name": "Other"}]})
        self.assert_line(repo, "ERROR", "scenario other has no native case")

    def test_scenario_that_requires_a_service_needs_no_case(self):
        repo = Repo(self)
        repo.json("g/skills/s/evals/evals.json",
                  {"evals": [{"name": "Basic"}, {"name": "Live", "requires": "a server"}]})

        have, lines = self.lint(repo)

        self.assertEqual(0, have, lines)

    def test_fixture_copy_differs(self):
        repo = Repo(self)
        repo.write("g/evals/mocks/fixtures/a.md", "suite\n")
        repo.write("g/evals/s--basic/mocks/fixtures/a.md", "case\n")

        self.assert_line(repo, "ERROR", "differs from the suite copy")

    def test_traceability(self):
        repo = Repo(self)
        repo.json("g/skills/s/evals/expectations.json",
                  {"expectations": [{"name": "Basic", "expected_behavior": ["a", "b"]}]})
        self.assert_line(repo, "ERROR", "Basic b2 has no grader, probe, or blind_only entry")

        repo = Repo(self)
        repo.json("g/skills/s/evals/probes.json", {"probes": [{"id": "p1", "bullets": ["basic#b9"]}]})
        self.assert_line(repo, "ERROR", 'bullet "basic#b9" names no expectations bullet')

        repo = Repo(self)
        repo.json("g/skills/s/evals/expectations.json",
                  {"expectations": [{"name": "Basic", "expected_behavior": ["a"], "blind_only": [1]}]})
        self.assert_line(repo, "ERROR", "b1 is blind_only but is also checked")

        repo = Repo(self)
        repo.json("g/skills/s/evals/expectations.json",
                  {"expectations": [{"name": "Basic", "expected_behavior": ["a"], "blind_only": [3]}]})
        self.assert_line(repo, "ERROR", "blind_only 3 names no bullet")

    def test_probe_covers_a_bullet(self):
        repo = Repo(self)
        repo.json("g/skills/s/evals/expectations.json",
                  {"expectations": [{"name": "Basic", "expected_behavior": ["a", "b"]}]})
        repo.json("g/skills/s/evals/probes.json", {"probes": [{"id": "p1", "bullets": ["basic#b2"]}]})

        have, lines = self.lint(repo)

        self.assertEqual(0, have, lines)


@unittest.skipIf(os.environ.get("LINT_CASES"), "Python-only behavior")
class SubsetTest(unittest.TestCase):
    """Grader patterns stay inside the JavaScript subset Python reads alike."""

    def test_outside_the_subset_is_an_error(self):
        repo = Repo(self)
        repo.grader("b1-x.md", "---\ntype: regex\n---\na++\n")

        code, out = repo.lint()

        self.assertEqual(1, code, out)
        self.assertIn("possessive", out)

    def test_varying_lookbehind_warns_in_a_plain_case(self):
        repo = Repo(self)
        repo.grader("b2-x.md", "---\ntype: regex\nmatch: not_contains\n---\n(?<=a+)b\n")

        code, out = repo.lint()

        self.assertEqual(0, code, out)
        self.assertIn("WARN   g/evals/s--basic/graders/b2-x.md", out)
        self.assertIn("cases: 0 error(s), 1 warning(s)", out)

    def test_varying_lookbehind_is_an_error_in_a_shell_case(self):
        repo = Repo(self)
        repo.prompt(tags="case:s--basic, skill:s, needs-shell", tools="Read, Bash(git:*)")
        repo.grader("b2-x.md", "---\ntype: regex\nmatch: not_contains\n---\n(?<=a+)b\n")

        code, out = repo.lint()

        self.assertEqual(1, code, out)
        self.assertIn("ERROR  g/evals/s--basic/graders/b2-x.md", out)


if os.environ.get("LINT_CASES"):  # another implementation to check the tests against
    CMD = os.environ["LINT_CASES"].split()

if __name__ == "__main__":
    unittest.main()
