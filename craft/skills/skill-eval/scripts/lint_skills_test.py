"""Tests for lint-skills.py. Run: python3 -B -m unittest lint_skills_test (from scripts/).

Each test builds a small git repo with one clean skill, breaks one thing, and
checks the line lint-skills prints for it.
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
CMD = [sys.executable, "-B", os.path.join(HERE, "lint-skills.py")]

SKILL = """---
name: s
description: Does a thing for a test.
{extra}---

# s

## Usage

Use it.

Report tersely.

## Self-learning

Learn.
"""


class Repo:
    """A git repo with plugin g, its marketplace entry, and clean skill s."""

    def __init__(self, test):
        self.root = tempfile.mkdtemp()
        test.addCleanup(shutil.rmtree, self.root)
        subprocess.run(["git", "init", "-q", self.root], check=True)
        self.json("g/.claude-plugin/plugin.json", {"name": "g"})
        self.json(".claude-plugin/marketplace.json", {"name": "m", "plugins": [{"name": "g", "source": "./g"}]})
        self.skill()
        self.write("g/skills/s/evals/evals.json",
                   '{"evals": [\n{"id": 1, "query": "a"},\n{"id": 2, "query": "b"},\n{"id": 3, "query": "c"}\n]}\n')
        self.write("g/skills/s/evals/expectations.json",
                   '{"expectations": [\n' + ",\n".join(
                       f'{{"id": {i}, "expected_behavior": ["x"]}}' for i in (1, 2, 3)) + "\n]}\n")
        self.json("g/skills/s/evals/contract.json", {"skill_name": "s", "rules": []})
        self.json("g/skills/s/evals/probes.json", {"skill_name": "s", "probes": []})
        self.json("dev/eval/triggers.json", {"distractors": {}, "cases":
                  [{"say": f"do {i}", "want": "g:s"} for i in range(3)]
                  + [{"say": f"other {i}", "want": "none"} for i in range(5)]})
        self.write("dev/version.sh", "#!/bin/sh\nexit 0\n", 0o755)

    def path(self, rel):
        return os.path.join(self.root, rel)

    def write(self, rel, text, mode=None):
        os.makedirs(os.path.dirname(self.path(rel)), exist_ok=True)
        with open(self.path(rel), "w") as f:
            f.write(text)
        if mode:
            os.chmod(self.path(rel), mode)

    def json(self, rel, obj):
        self.write(rel, json.dumps(obj, indent=2) + "\n")

    def skill(self, text=None, extra=""):
        self.write("g/skills/s/SKILL.md", text if text is not None else SKILL.format(extra=extra))

    def lint(self):
        env = dict(os.environ, SKILL_EVAL_ROOT=self.root)
        r = subprocess.run(CMD, capture_output=True, text=True, env=env, cwd=self.root)
        return r.returncode, r.stdout


class LintSkillsTest(unittest.TestCase):
    def assert_line(self, repo, level, text):
        code, out = repo.lint()
        hits = [ln for ln in out.splitlines() if ln.startswith(level) and text in ln]
        self.assertTrue(hits, out)
        self.assertEqual(1 if level == "ERROR" else 0, code, out)

    def test_clean_repo(self):
        have, out = Repo(self).lint()

        self.assertEqual(0, have, out)
        self.assertEqual("----\n0 error(s), 0 warning(s).\n", out)

    def test_front_matter(self):
        for text, want in [
            ("---\ndescription: x.\n---\n## Usage\nReport tersely.\n## Self-learning\n", "frontmatter missing 'name:'"),
            ("---\nname: s\n---\n## Usage\nReport tersely.\n## Self-learning\n", "frontmatter missing 'description:'"),
            ("---\nname: t\ndescription: x.\n---\n## Usage\nReport tersely.\n## Self-learning\n",
             "frontmatter name 't' != directory 's'"),
        ]:
            with self.subTest(want=want):
                repo = Repo(self)
                repo.skill(text)

                self.assert_line(repo, "ERROR", want)

    def test_description_warnings(self):
        repo = Repo(self)
        repo.skill(SKILL.format(extra="").replace("Does a thing for a test.", ">\n  " + "word " * 101 + "end."))
        self.assert_line(repo, "WARN", "description is 509 chars (aim <= ~350)")

        repo = Repo(self)
        repo.skill(SKILL.format(extra="").replace("Does a thing for a test.", "Helps you do a thing."))
        self.assert_line(repo, "WARN", "description uses first/second person")

    def test_body_size_warnings(self):
        repo = Repo(self)
        repo.skill(SKILL.format(extra="") + "line\n" * 500)
        self.assert_line(repo, "WARN", "lines (aim <= ~500)")

        repo = Repo(self)
        repo.skill(SKILL.format(extra="") + ("x" * 79 + "\n") * 260)
        self.assert_line(repo, "WARN", "tokens (aim <= ~5000)")

    def test_required_body_parts(self):
        for old, new, level, want in [
            ("Report tersely.", "Be brief.", "ERROR", "lacks the output-discipline line"),
            ("## Self-learning", "## Lessons", "WARN", "has no '## Self-learning' block"),
            ("## Usage", "## Use", "ERROR", "has no '## Usage' section"),
        ]:
            with self.subTest(want=want):
                repo = Repo(self)
                repo.skill(SKILL.format(extra="").replace(old, new))

                self.assert_line(repo, level, want)

    def test_links(self):
        repo = Repo(self)
        repo.skill(SKILL.format(extra="") + "\nSee [x](references/missing.md).\n")
        self.assert_line(repo, "ERROR", "link target 'references/missing.md' does not exist")

        repo = Repo(self)
        repo.write("g/skills/s/references/a.md", "See [b](references/b.md).\n")
        repo.write("g/skills/s/references/b.md", "B.\n")
        self.assert_line(repo, "ERROR", "references/a.md: link target 'references/b.md' does not exist")

    def test_links_that_are_skipped(self):
        repo = Repo(self)
        repo.write("g/skills/s/references/a.md",
                   "```\n[x](no/where.md)\n```\n> [y](no/where.md)\n[z](https://x.y/z) [w](#top) [v](nowhere.md)\n"
                   "[u](../SKILL.md#usage)\n")

        have, out = repo.lint()

        self.assertEqual(0, have, out)

    def test_positional_placeholder(self):
        repo = Repo(self)
        repo.write("g/skills/s/references/a.md", "The first token is $1.\n")

        self.assert_line(repo, "ERROR", "positional argument placeholder ($N) in:")

    def test_argument_hint(self):
        for hint, want in [
            ("argument-hint: \"[--all]\"\n", "argument-hint uses a --flag"),
            ("argument-hint: \"[max_usd=N]\"\n", "caps with something other than max=N"),
            ("argument-hint: \"[a | b]\"\n", "lacks the unknown-token sentence"),
        ]:
            with self.subTest(hint=hint):
                repo = Repo(self)
                repo.skill(extra=hint)

                self.assert_line(repo, "ERROR", want)

    def test_argument_hint_with_the_unknown_token_sentence(self):
        repo = Repo(self)
        repo.skill(SKILL.format(extra="argument-hint: \"[a | b]\"\n") + "\nA word: say it\nwas not recognized.\n")

        have, out = repo.lint()

        self.assertEqual(0, have, out)

    def test_evals_files(self):
        repo = Repo(self)
        repo.write("g/skills/s/evals/evals.json", '{"evals": [\n{"id": 1, "query": "a"}\n]}\n')
        self.assert_line(repo, "ERROR", "evals/evals.json has 1 scenario(s) (want >= 3)")

        repo = Repo(self)
        os.remove(repo.path("g/skills/s/evals/evals.json"))
        self.assert_line(repo, "ERROR", "no evals/evals.json")

        repo = Repo(self)
        os.remove(repo.path("g/skills/s/evals/expectations.json"))
        self.assert_line(repo, "ERROR", "no evals/expectations.json")

        repo = Repo(self)
        repo.write("g/skills/s/evals/evals.json",
                   '{"evals": [\n{"id": 1, "query": "a", "expected_behavior": []},\n'
                   '{"id": 2, "query": "b"},\n{"id": 3, "query": "c"}\n]}\n')
        self.assert_line(repo, "ERROR", "carries 'expected_behavior'")

        repo = Repo(self)
        repo.write("g/skills/s/evals/expectations.json", '{"expectations": [{"id": 1}, {"id": 2}, {"id": 3}]}\n')
        self.assert_line(repo, "ERROR", "evals/expectations.json has no 'expected_behavior' checks")

        repo = Repo(self)
        repo.write("g/skills/s/evals/expectations.json",
                   '{"expectations": [{"id": 1, "expected_behavior": []}, {"id": 4, "expected_behavior": []}]}\n')
        self.assert_line(repo, "ERROR", "evals ids [1 2 3 ] != expectations ids [1 4 ]")

    def test_readme(self):
        repo = Repo(self)
        repo.write("g/skills/s/README.md", "Readme.\n")

        self.assert_line(repo, "ERROR", "has a README.md")

    def test_wrap(self):
        repo = Repo(self)
        repo.write("g/skills/s/references/a.md", ("word " * 20).strip() + "\n")
        self.assert_line(repo, "WARN", "references/a.md:1 (99 cols) exceeds 80-col wrap")

        repo = Repo(self)
        repo.write("g/skills/s/references/a.md", "→" * 80 + " é\n")
        self.assert_line(repo, "WARN", "references/a.md:1 (82 cols) exceeds 80-col wrap")

    def test_wrap_exemptions(self):
        repo = Repo(self)
        repo.write("g/skills/s/references/a.md",
                   "→" * 78 + " é\n" + "```\n" + "word " * 30 + "\n```\n| " + "cell " * 30 + "|\n"
                   + "https://example.com/" + "x" * 90 + "\n")

        have, out = repo.lint()

        self.assertEqual(0, have, out)

    def test_contents_list(self):
        repo = Repo(self)
        repo.write("g/skills/s/references/a.md", "# A\n" + "line\n" * 100)
        self.assert_line(repo, "WARN", "references/a.md: 101 lines, no Contents list")

        repo = Repo(self)
        repo.write("g/skills/s/references/a.md", "# A\n\n## Contents\n" + "line\n" * 100)
        have, out = repo.lint()
        self.assertEqual(0, have, out)

    def test_marketplace(self):
        repo = Repo(self)
        repo.json(".claude-plugin/marketplace.json", {"name": "m", "plugins": [
            {"name": "g", "source": "./g"}, {"name": "h", "source": "./h"}]})
        self.assert_line(repo, "ERROR", "marketplace: plugin 'h' source 'h' has no .claude-plugin/plugin.json")

        repo = Repo(self)
        repo.json(".claude-plugin/marketplace.json", {"name": "m", "plugins": []})
        self.assert_line(repo, "ERROR", "skill 'g/skills/s' sits under 0 plugin sources (want exactly 1)")

        repo = Repo(self)
        repo.json(".claude-plugin/marketplace.json", {"name": "m"})
        self.assert_line(repo, "ERROR", 'marketplace.json: no "plugins" array')

        repo = Repo(self)
        os.remove(repo.path(".claude-plugin/marketplace.json"))
        self.assert_line(repo, "WARN", "no .claude-plugin/marketplace.json")

    def test_version_drift(self):
        repo = Repo(self)
        repo.write("dev/version.sh", "#!/bin/sh\nexit 1\n", 0o755)
        self.assert_line(repo, "ERROR", "manifest versions drifted from VER")

        repo = Repo(self)
        os.remove(repo.path("dev/version.sh"))
        self.assert_line(repo, "WARN", "skipping version-drift check")

    def test_invalid_json(self):
        repo = Repo(self)
        repo.write("g/notes.json", "2\n}")

        self.assert_line(repo, "ERROR", "g/notes.json: not valid JSON")

    def test_case_and_eval_check_errors_count(self):
        repo = Repo(self)
        os.remove(repo.path("g/skills/s/evals/probes.json"))

        self.assert_line(repo, "ERROR", "g/skills/s: no evals/probes.json")

    def test_skips_tmp_and_assets(self):
        repo = Repo(self)
        repo.write("tmp/x/SKILL.md", "broken\n")
        repo.write("g/skills/s/assets/fixture/SKILL.md", "broken\n")

        have, out = repo.lint()

        self.assertEqual(0, have, out)


if __name__ == "__main__":
    unittest.main()
