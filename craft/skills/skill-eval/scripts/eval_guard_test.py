"""Tests for eval_guard.py. Run: python3 -B -m unittest eval_guard_test (from scripts/)."""
import os
import sys
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_guard import deny_home_edits, home_commands, home_writes  # noqa: E402

HOME, WS = "/home/u", "/tmp/claude-eval-sh-1"


def write(tid, inp, name="Write"):
    return {"type": "assistant",
            "message": {"content": [{"type": "tool_use", "id": tid, "name": name, "input": inp}]}}


def result(tid, is_error=False):
    return {"type": "user",
            "message": {"content": [{"type": "tool_result", "tool_use_id": tid, "is_error": is_error}]}}


def bash(tid, command):
    return write(tid, {"command": command}, "Bash")


class DenyHomeEditsTest(unittest.TestCase):
    def test_denies_edits_under_the_real_home(self):
        have = deny_home_edits(HOME, WS)

        self.assertEqual(["--disallowedTools", "Edit(//home/u/**)"], have)

    def test_denies_nothing_when_the_workspace_is_inside_the_home(self):
        have = deny_home_edits(HOME, "/home/u/tmp/claude-eval-sh-1")

        self.assertEqual([], have)


class HomeWritesTest(unittest.TestCase):
    def test_lists_a_write_into_the_real_home(self):
        events = [write("t1", {"file_path": "/home/u/.agent-data/lessons/go/doc.md"}), result("t1")]

        have = home_writes(events, HOME, WS)

        self.assertEqual(["/home/u/.agent-data/lessons/go/doc.md"], have)

    def test_lists_edit_and_notebook_edit_too(self):
        events = [write("t1", {"file_path": "/home/u/a.go"}, "Edit"), result("t1"),
                  write("t2", {"notebook_path": "/home/u/b.ipynb"}, "NotebookEdit"), result("t2")]

        have = home_writes(events, HOME, WS)

        self.assertEqual(["/home/u/a.go", "/home/u/b.ipynb"], have)

    def test_skips_a_refused_write(self):
        events = [write("t1", {"file_path": "/home/u/x.md"}), result("t1", True)]

        have = home_writes(events, HOME, WS)

        self.assertEqual([], have)

    def test_skips_workspace_and_relative_paths(self):
        events = [write("t1", {"file_path": f"{WS}/home/cwd/x.md"}), result("t1"),
                  write("t2", {"file_path": "notes/y.md"}), result("t2"),
                  write("t3", {"file_path": "~/.agent-data/z.md"}), result("t3")]

        have = home_writes(events, HOME, WS)

        self.assertEqual([], have)

    def test_skips_writes_outside_the_real_home(self):
        events = [write("t1", {"file_path": "/tmp/other/x.md"}), result("t1")]

        have = home_writes(events, HOME, WS)

        self.assertEqual([], have)

    def test_does_not_match_a_sibling_of_the_home_by_prefix(self):
        events = [write("t1", {"file_path": "/home/u2/x.md"}), result("t1")]

        have = home_writes(events, HOME, WS)

        self.assertEqual([], have)

    def test_skips_a_write_with_no_result(self):
        events = [write("t1", {"file_path": "/home/u/x.md"})]

        have = home_writes(events, HOME, WS)

        self.assertEqual([], have)


class HomeCommandsTest(unittest.TestCase):
    def test_lists_a_bash_call_that_names_the_real_home(self):
        events = [bash("b1", "wc -l /home/u/.agent-data/lessons/craft/cm.md"), result("b1")]

        have = home_commands(events, HOME)

        self.assertEqual(["wc -l /home/u/.agent-data/lessons/craft/cm.md"], have)

    def test_skips_a_refused_call_and_a_sibling_of_the_home(self):
        events = [bash("b1", "cat /home/u/x"), result("b1", True),
                  bash("b2", "cat /home/u2/x"), result("b2"),
                  bash("b3", "go test ./..."), result("b3")]

        have = home_commands(events, HOME)

        self.assertEqual([], have)

    def test_matches_the_home_at_the_end_of_a_command(self):
        events = [bash("b1", "ls /home/u"), result("b1")]

        have = home_commands(events, HOME)

        self.assertEqual(["ls /home/u"], have)


if __name__ == "__main__":
    unittest.main()
