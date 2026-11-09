"""Tests for jsregex.py. Run: python3 -B -m unittest jsregex_test (from scripts/)."""
import os
import sys
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jsregex  # noqa: E402

# pattern, flags, text, and whether JavaScript's RegExp.test matches. Each
# result was recorded once from Bun (`new RegExp(p, f).test(t)`), not reasoned.
GOLDEN = [
    ("\\w", "", "é", False),
    ("\\d", "", "٣", False),
    ("\\bcat\\b", "", "écat", True),
    ("\\bé", "", " é", False),
    ("x\\B", "", "xé", False),
    ("[^\\w]", "", "é", True),
    ("^a$", "", "a\n", False),
    ("a$", "m", "a\r\nb", True),
    ("^b", "m", "a\rb", True),
    ("a.b", "", "a\rb", False),
    ("a.b", "", "a b", False),
    ("a.b", "s", "a\nb", True),
    ("a$", "m", "a\nb", True),
    ("é", "i", "É", True),
    ("colou?r", "i", "COLOR", True),
    ("(?<y>\\d{4})-\\k<y>", "", "2026-2026", True),
    ("[$]", "", "$", True),
    ("\\$5", "", "cost $5", True),
    ("", "", "anything", True),
    ("[\\s\\S]+", "", "\n", True),
    ("[\\d.]+", "", "3.5", True),
    ("[[]", "", "[", True),
    ("a[&&]b", "", "a&b", True),
    ("\\w+", "i", "_x9", True),
    ("(?<=ab)c", "", "abc", True),
    ("^x", "", "a\nx", False),
]


class CompileTest(unittest.TestCase):
    def test_matches_like_javascript(self):
        for pattern, flags, text, want in GOLDEN:
            with self.subTest(pattern=pattern, flags=flags, text=text):
                have = jsregex.compile(pattern, flags).search(text) is not None

                self.assertEqual(want, have)

    def test_raises_outside_the_subset(self):
        with self.assertRaises(ValueError) as cm:
            jsregex.compile("a++")

        self.assertIn("possessive", str(cm.exception))


class CheckTest(unittest.TestCase):
    def test_inside_the_subset(self):
        for pattern, flags in [
            ("", ""), ("a+?", ""), ("(?:a)", ""), ("(?=a)(?!b)", ""),
            ("(?<=ab)c", ""), ("(?<!a)b", ""), ("(?<n>a)\\k<n>", ""),
            ("x{2,3}", ""), ("[\\s\\S]*", "ims"), ("\\{,3\\}", ""), ("[$]\\$", ""),
            ("a}+", ""),
        ]:
            with self.subTest(pattern=pattern, flags=flags):
                have = jsregex.check(pattern, flags)

                self.assertEqual([], have)

    def test_outside_the_subset(self):
        for pattern, flags, want in [
            ("\\p{L}", "", "\\p{"),
            ("\\P{L}", "", "\\P{"),
            ("\\u{41}", "", "\\u{"),
            ("\\Afoo", "", "anchor"),
            ("foo\\Z", "", "anchor"),
            ("foo\\z", "", "anchor"),
            ("a[]b", "", "empty class"),
            ("a[^]b", "", "[^]"),
            ("a{,3}", "", "{,n}"),
            ("(?P<n>a)", "", "(?P"),
            ("(?>a)", "", "atomic"),
            ("a++", "", "possessive"),
            ("a*+", "", "possessive"),
            ("a?+", "", "possessive"),
            ("a{2}+", "", "possessive"),
            ("(?i)a", "", "inline flag"),
            ("(?i:a)", "", "inline flag"),
            ("a", "g", "flag 'g'"),
            ("a", "y", "flag 'y'"),
            ("a", "u", "flag 'u'"),
            ("[\\W]", "", "\\W inside"),
            ("[\\D]", "", "\\D inside"),
            ("(?<=a+)b", "", "Python"),
            ("(", "", "Python"),
            ("a\\", "", "trailing"),
        ]:
            with self.subTest(pattern=pattern, flags=flags):
                have = jsregex.check(pattern, flags)

                self.assertTrue(any(want in r for r in have), have)

    def test_check_never_raises(self):
        for pattern in ["(", ")", "[", "\\", "(?<", "(?<n", "\\k<", "{"]:
            with self.subTest(pattern=pattern):
                have = jsregex.check(pattern)

                self.assertIsInstance(have, list)


if __name__ == "__main__":
    unittest.main()
