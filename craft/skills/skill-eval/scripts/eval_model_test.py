"""Tests for eval_model.py. Run: python3 -B -m unittest eval_model_test (from scripts/)."""
import os
import sys
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_model import main_model  # noqa: E402


class MainModelTest(unittest.TestCase):
    def test_picks_the_costliest_model(self):
        have = main_model({"claude-helper-1": {"costUSD": 0.001}, "claude-main-1": {"costUSD": 0.4}})

        self.assertEqual("claude-main-1", have)

    def test_returns_the_only_model(self):
        have = main_model({"claude-main-1": {"costUSD": 0}})

        self.assertEqual("claude-main-1", have)

    def test_returns_none_without_usage(self):
        self.assertIsNone(main_model(None))
        self.assertIsNone(main_model({}))


if __name__ == "__main__":
    unittest.main()
