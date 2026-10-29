#!/usr/bin/env python3
"""Tests for case-cost.py. Run: python3 -B -m unittest case_cost_test (from scripts/)."""
import importlib.util
import json
import os
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("case_cost", os.path.join(HERE, "case-cost.py"))
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)

RESULT = {"type": "result", "subtype": "success", "total_cost_usd": 0.28,
          "usage": {"input_tokens": 16, "cache_read_input_tokens": 160610,
                    "cache_creation_input_tokens": 24732, "output_tokens": 2285}}


def results(trace):
    return {"costUsd": 0.5, "cases": [
        {"name": "cm--kept", "arms": {"with": [{"passed": True, "costUsd": 0.28, "turns": 7,
                                                 "tracePath": trace}]}},
        {"name": "cm--gone", "arms": {"with": [{"passed": False, "costUsd": 0.22, "turns": 4,
                                                 "tracePath": "/nonexistent/trace.jsonl"}]}},
    ]}


class Tokens(unittest.TestCase):
    def test_from_result_line(self):
        with tempfile.TemporaryDirectory() as d:
            t = os.path.join(d, "trace.jsonl")
            with open(t, "w") as f:
                f.write(json.dumps({"type": "system", "subtype": "init"}) + "\n")
                f.write("not json\n")
                f.write(json.dumps(RESULT) + "\n")
            want = {"input": 16, "cache_read": 160610, "cache_write": 24732, "output": 2285}
            self.assertEqual(want, cc.tokens(t))

    def test_missing_trace(self):
        self.assertIsNone(cc.tokens("/nonexistent/trace.jsonl"))

    def test_no_result_line(self):
        with tempfile.TemporaryDirectory() as d:
            t = os.path.join(d, "trace.jsonl")
            with open(t, "w") as f:
                f.write(json.dumps({"type": "assistant"}) + "\n")
            self.assertIsNone(cc.tokens(t))


class Rows(unittest.TestCase):
    def test_rows_per_case(self):
        with tempfile.TemporaryDirectory() as d:
            t = os.path.join(d, "trace.jsonl")
            with open(t, "w") as f:
                f.write(json.dumps(RESULT) + "\n")
            p = os.path.join(d, "craft-plain-0.json")
            with open(p, "w") as f:
                json.dump(results(t), f)
            have = cc.rows([p])
        self.assertEqual(["cm--kept", "cm--gone"], [r["case"] for r in have])
        self.assertEqual([True, False], [r["passed"] for r in have])
        self.assertEqual([0.28, 0.22], [r["usd"] for r in have])
        self.assertEqual(187643, have[0]["tokens"]["input"] + have[0]["tokens"]["cache_read"]
                         + have[0]["tokens"]["cache_write"] + have[0]["tokens"]["output"])
        self.assertIsNone(have[1]["tokens"])

    def test_dir_finds_result_files(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "craft"))
            with open(os.path.join(d, "craft-plain-0.json"), "w") as f:
                json.dump(results("/nonexistent"), f)
            with open(os.path.join(d, "craft", "notes.txt"), "w") as f:
                f.write("x")
            self.assertEqual(2, len(cc.rows([d])))

    def test_saved_failed_trace(self):
        # A failed case's workspace is gone, but eval-changed.sh saved its
        # trace as <run>/<group>/failed/<case>.trace.jsonl.
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "craft", "failed"))
            with open(os.path.join(d, "craft", "failed", "cm--gone.trace.jsonl"), "w") as f:
                f.write(json.dumps(RESULT) + "\n")
            with open(os.path.join(d, "craft-plain-0.json"), "w") as f:
                json.dump(results("/nonexistent"), f)
            have = cc.rows([d])
        self.assertIsNone(have[0]["tokens"])
        self.assertEqual(2285, have[1]["tokens"]["output"])


class Render(unittest.TestCase):
    def test_lines_and_total(self):
        rows = [{"case": "a", "passed": True, "usd": 0.25, "turns": 3,
                 "tokens": {"input": 1, "cache_read": 2, "cache_write": 3, "output": 4}},
                {"case": "bb", "passed": False, "usd": 0.5, "turns": 9, "tokens": None}]
        have = cc.render(rows).splitlines()
        self.assertEqual(3, len(have))
        self.assertRegex(have[0], r"^PASS +a +\$0\.25 +3 turns +10 tokens \(out 4\)$")
        self.assertRegex(have[1], r"^FAIL +bb +\$0\.50 +9 turns +no trace$")
        self.assertEqual("case-cost: 2 case(s), $0.75; tokens for 1 (keep traces with --keep)", have[2])


if __name__ == "__main__":
    unittest.main()
