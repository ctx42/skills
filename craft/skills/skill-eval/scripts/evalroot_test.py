#!/usr/bin/env python3
"""Tests for evalroot.py. Run: python3 -B -m unittest evalroot_test (from scripts/)."""
import os
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import evalroot  # noqa: E402


def mkfile(root, rel):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").close()


class Root(unittest.TestCase):
    def setUp(self):
        self.env = os.environ.pop("SKILL_EVAL_ROOT", None)
        self.cwd = os.getcwd()

    def tearDown(self):
        os.chdir(self.cwd)
        os.environ.pop("SKILL_EVAL_ROOT", None)
        if self.env is not None:
            os.environ["SKILL_EVAL_ROOT"] = self.env

    def test_env_wins(self):
        with tempfile.TemporaryDirectory() as d:
            os.environ["SKILL_EVAL_ROOT"] = d
            self.assertEqual(os.path.realpath(d), evalroot.find_root())

    def test_git_toplevel(self):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["git", "init", "-q", d], check=True)
            os.makedirs(os.path.join(d, "a", "b"))
            os.chdir(os.path.join(d, "a", "b"))
            self.assertEqual(os.path.realpath(d), evalroot.find_root())

    def test_cwd_outside_git(self):
        with tempfile.TemporaryDirectory() as d:
            os.chdir(d)
            env = dict(os.environ, GIT_CEILING_DIRECTORIES=os.path.dirname(os.path.realpath(d)))
            have = subprocess.run(
                [sys.executable, "-B", "-c", "import evalroot; print(evalroot.find_root())"],
                cwd=d, env=dict(env, PYTHONPATH=os.path.dirname(os.path.abspath(__file__))),
                capture_output=True, text=True, check=True).stdout.strip()
            self.assertEqual(os.path.realpath(d), have)


class Groups(unittest.TestCase):
    def test_dirs_with_skills(self):
        with tempfile.TemporaryDirectory() as d:
            mkfile(d, "web/skills/style/SKILL.md")
            mkfile(d, "craft/skills/cm/SKILL.md")
            mkfile(d, "docs/skills/readme.md")
            mkfile(d, "tmp/skills/old/SKILL.md")
            mkfile(d, "notify/hooks/hooks.json")
            self.assertEqual(("craft", "web"), evalroot.groups(d))

    def test_none(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual((), evalroot.groups(d))


if __name__ == "__main__":
    unittest.main()
