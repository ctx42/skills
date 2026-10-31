#!/usr/bin/env python3
"""Tests for eval-regrade.py.

Run: python3 -B -m unittest eval_regrade_test (from scripts/).
"""
import importlib.util
import json
import os
import sys
import tempfile
import unittest

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


if __name__ == "__main__":
    unittest.main()
