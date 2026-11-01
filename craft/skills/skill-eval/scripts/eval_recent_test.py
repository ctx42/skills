#!/usr/bin/env python3
"""Tests for eval-recent.py.

Run: python3 -B -m unittest eval_recent_test (from scripts/).
"""
import importlib.util
import os
import subprocess
import sys
import tempfile
import time
import unittest

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "eval-recent.py")
_spec = importlib.util.spec_from_file_location("eval_recent", SCRIPT)
recent = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(recent)


class RecentTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = os.path.join(self.tmp.name, "out")
        self.work = os.path.join(self.tmp.name, "work")
        os.makedirs(self.out)
        os.makedirs(self.work)

    def age(self, path, seconds):
        t = time.time() - seconds
        os.utime(path, (t, t))

    def file(self, *parts, age=0):
        path = os.path.join(*parts)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write("x")
        self.age(path, age)
        return path

    def test_fresh_write_in_out_counts(self):
        self.file(self.out, "a.log")

        have = recent.recent(60, self.out, self.work)

        self.assertTrue(have)

    def test_fresh_write_in_a_workspace_counts(self):
        self.age(self.out, 600)
        ws = os.path.join(self.work, "claude-eval-abc")
        self.file(ws, "home", "trace.jsonl")
        self.age(ws, 600)

        have = recent.recent(60, self.out, self.work)

        self.assertTrue(have)

    def test_only_old_writes_is_a_stall(self):
        self.file(self.out, "a.log", age=600)
        self.age(self.out, 600)
        ws = os.path.join(self.work, "claude-eval-abc")
        self.file(ws, "t.jsonl", age=600)
        self.age(ws, 600)

        have = recent.recent(60, self.out, self.work)

        self.assertFalse(have)

    def test_other_dirs_in_tmp_are_ignored(self):
        self.age(self.out, 600)
        self.file(self.work, "unrelated", "x", age=0)

        have = recent.recent(60, self.out, self.work)

        self.assertFalse(have)

    def test_exit_status(self):
        self.file(self.out, "a.log")

        r = subprocess.run([sys.executable, SCRIPT, "60", self.out, self.work])

        self.assertEqual(0, r.returncode)

    def test_exit_status_on_a_stall(self):
        self.age(self.out, 600)

        r = subprocess.run([sys.executable, SCRIPT, "60", self.out, self.work])

        self.assertEqual(1, r.returncode)


if __name__ == "__main__":
    unittest.main()
