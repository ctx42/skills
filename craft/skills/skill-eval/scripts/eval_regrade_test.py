#!/usr/bin/env python3
"""Tests for eval-regrade.py.

Run: python3 -B -m unittest eval_regrade_test (from scripts/).
"""
import contextlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_spec = importlib.util.spec_from_file_location("eval_regrade", os.path.join(HERE, "eval-regrade.py"))
regrade = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(regrade)


def text(t):
    return {"type": "assistant", "message": {"content": [{"type": "text", "text": t}]}}


class LastMessageTest(unittest.TestCase):
    def trace(self, *events):
        f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
        self.addCleanup(os.unlink, f.name)
        with f:
            for e in events:
                f.write((e if isinstance(e, str) else json.dumps(e)) + "\n")
        return f.name

    def test_last_result_wins(self):
        path = self.trace(text("worker"), {"type": "result", "result": "first"},
                          text("final"), {"type": "result", "result": "last"})

        have = regrade.last_message(path)

        self.assertEqual("last", have)

    def test_last_text_without_a_result(self):
        path = self.trace(text("one"), "not json", text("two"))

        have = regrade.last_message(path)

        self.assertEqual("two", have)


class MainTest(unittest.TestCase):
    def regrade(self, pattern, reply):
        case = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, case)
        os.mkdir(os.path.join(case, "graders"))
        with open(os.path.join(case, "graders", "b1.md"), "w") as f:
            f.write(f"---\ntype: regex\ntarget: last_message\n---\n{pattern}\n")
        trace = os.path.join(case, "x.trace.jsonl")
        with open(trace, "w") as f:
            f.write(json.dumps({"type": "result", "result": reply}) + "\n")
        out = io.StringIO()
        with mock.patch.object(sys, "argv", ["eval-regrade.py", trace, case]), \
                contextlib.redirect_stdout(out):
            code = regrade.main()
        return code, out.getvalue()

    def test_reads_the_pattern_as_javascript(self):
        # JavaScript's \b is ASCII-only, so é before "cat" is a word boundary.
        have, out = self.regrade("\\bcat\\b", "écat")

        self.assertEqual(0, have, out)
        self.assertIn("PASS  b1", out)

    def test_pattern_outside_the_subset_is_an_error(self):
        have, out = self.regrade("a++", "aaa")

        self.assertEqual(1, have)
        self.assertIn("ERR   b1", out)
        self.assertIn("possessive", out)


if __name__ == "__main__":
    unittest.main()
