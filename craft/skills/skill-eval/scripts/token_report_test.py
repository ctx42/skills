"""Tests for token-report.py. Run: python3 -B -m unittest token_report_test (from scripts/)."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
CMD = [sys.executable, "-B", os.path.join(HERE, "token-report.py")]
if os.environ.get("TOKEN_REPORT"):  # another implementation to check the tests against
    CMD = os.environ["TOKEN_REPORT"].split()


def write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


class TokenReportTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root)

    def report(self):
        env = dict(os.environ, SKILL_EVAL_ROOT=self.root)
        r = subprocess.run(CMD, capture_output=True, text=True, env=env)
        self.assertEqual(0, r.returncode, r.stderr)
        return r.stdout

    def test_counts_description_and_body(self):
        write(self.root, "g/skills/a/SKILL.md", "---\nname: a\ndescription: >\n  Twelve chars\n---\none two three\n")
        write(self.root, "g/skills/b/SKILL.md", "---\nname: b\ndescription: Short.\n---\n" + "w " * 30 + "\n")

        have = self.report()

        self.assertEqual(
            "skill                    desc  body-w  ~body-t\n"
            "-----                    ----  ------  -------\n"
            "g:a                        12      11       14\n"
            "g:b                         6      36       48\n"
            "-----                    ----  ------  -------\n"
            "total                      18      47       62\n"
            "\n"
            "On-demand references (loaded only when a workflow step reads them):\n", have)

    def test_lists_references_and_assets(self):
        write(self.root, "g/skills/a/SKILL.md", "---\nname: a\ndescription: A.\n---\nbody\n")
        write(self.root, "g/skills/a/references/r.md", "one two\n")
        write(self.root, "g/skills/a/assets/sub/x.md", "one two three\n")
        write(self.root, "tmp/g/skills/z/SKILL.md", "---\nname: z\ndescription: Z.\n---\n")

        have = self.report()

        self.assertNotIn("g:z", have)
        self.assertTrue(have.endswith(
            "       3 words  g/skills/a/assets/sub/x.md\n"
            "       2 words  g/skills/a/references/r.md\n"), have)

    def test_skill_outside_a_skills_dir(self):
        write(self.root, ".claude/local/SKILL.md", "---\nname: local\n---\n")

        have = self.report()

        self.assertIn("\n.claude:local               0       4        5\n", have)


if __name__ == "__main__":
    unittest.main()
