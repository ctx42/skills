"""Tests for eval_graders.py. Run: python3 -B -m unittest eval_graders_test (from scripts/)."""
import os
import sys
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_graders import asserts, can_use  # noqa: E402


class AssertsTest(unittest.TestCase):
    def test_regex_that_must_match(self):
        self.assertTrue(asserts({"type": "regex"}))
        self.assertTrue(asserts({"type": "regex", "match": "contains"}))
        self.assertTrue(asserts({"type": "regex", "match": "count:2"}))

    def test_regex_that_must_not_match(self):
        self.assertFalse(asserts({"type": "regex", "match": "not_contains"}))
        self.assertFalse(asserts({"type": "regex", "match": "count:0"}))

    def test_tool_used_asserts_only_a_use(self):
        self.assertTrue(asserts({"type": "tool_used"}))
        self.assertTrue(asserts({"type": "tool_used", "min": "2"}))
        self.assertFalse(asserts({"type": "tool_used", "max": "0"}))
        self.assertFalse(asserts({"type": "tool_used", "min": "0", "max": "3"}))

    def test_file_exists_asserts_only_a_created_file(self):
        self.assertTrue(asserts({"type": "file_exists"}))
        self.assertFalse(asserts({"type": "file_exists", "exists": "false"}))

    def test_tool_order_and_llm(self):
        self.assertTrue(asserts({"type": "tool_order"}))
        self.assertTrue(asserts({"type": "llm"}))


class CanUseTest(unittest.TestCase):
    def test_a_tool_the_case_allows(self):
        self.assertTrue(can_use("Bash", ["Read", "Bash(git:*)"], True))
        self.assertTrue(can_use("Read", ["Read"], True))

    def test_a_mocked_mcp_tool(self):
        self.assertTrue(can_use("mcp__srd__report_gap", [], False))

    def test_write_edit_lsp_only_in_a_plain_case(self):
        self.assertTrue(can_use("Write", ["Read"], False))
        self.assertTrue(can_use("Edit", ["Read"], False))
        self.assertFalse(can_use("Write", ["Read", "Bash(git:*)"], True))

    def test_a_tool_the_case_does_not_allow(self):
        self.assertFalse(can_use("Bash", ["Read"], False))
        self.assertFalse(can_use("WebFetch", ["Read"], False))


if __name__ == "__main__":
    unittest.main()
