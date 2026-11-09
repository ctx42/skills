"""Tests for eval_notice.py. Run: python3 -B -m unittest eval_notice_test (from scripts/)."""
import os
import sys
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_notice import strip_notice  # noqa: E402

RE = "«Acme policy»"


class StripNoticeTest(unittest.TestCase):
    def test_drops_a_trailing_paragraph_that_matches(self):
        have = strip_notice("Done.\n\nNote: this falls under «Acme policy» V1.2.\n", RE)

        self.assertEqual("Done.", have)

    def test_keeps_the_text_when_the_last_paragraph_does_not_match(self):
        text = "Note: «Acme policy» applies.\n\nDone."

        have = strip_notice(text, RE)

        self.assertEqual(text, have)

    def test_keeps_a_reply_that_is_only_the_notice(self):
        text = "Note: this falls under «Acme policy»."

        have = strip_notice(text, RE)

        self.assertEqual(text, have)

    def test_keeps_the_text_without_a_pattern(self):
        text = "Done.\n\nNote: «Acme policy»."

        self.assertEqual(text, strip_notice(text, ""))
        self.assertEqual(text, strip_notice(text, None))

    def test_drops_only_the_last_paragraph(self):
        have = strip_notice("A.\n\n«Acme policy» once.\n\n«Acme policy» twice.", RE)

        self.assertEqual("A.\n\n«Acme policy» once.", have)

    def test_reads_the_pattern_as_javascript(self):
        # JavaScript's \w is ASCII-only, so it does not match the é.
        text = "Done.\n\nNote: é."

        have = strip_notice(text, "Note: \\w\\.")

        self.assertEqual(text, have)


if __name__ == "__main__":
    unittest.main()
