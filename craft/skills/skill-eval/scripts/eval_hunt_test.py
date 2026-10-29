#!/usr/bin/env python3
"""Tests for eval-hunt.py. Run: python3 -B -m unittest eval_hunt_test (from scripts/)."""
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def sh(root, *args):
    subprocess.run(args, cwd=root, check=True, capture_output=True)


def write(root, rel, text="x\n"):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


class ChangedSkills(unittest.TestCase):
    """A skill or reference the working tree deleted is no hunt target."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = cls.root = cls.tmp.name
        sh(root, "git", "init", "-q")
        sh(root, "git", "config", "user.email", "t@example.com")
        sh(root, "git", "config", "user.name", "T")
        for rel in ("craft/skills/gone/SKILL.md", "craft/skills/kept/SKILL.md",
                    "craft/skills/kept/references/old.md",
                    "craft/skills/kept/references/live.md"):
            write(root, rel)
        sh(root, "git", "add", "-A")
        sh(root, "git", "commit", "-qm", "init")
        os.remove(os.path.join(root, "craft/skills/gone/SKILL.md"))
        os.remove(os.path.join(root, "craft/skills/kept/references/old.md"))
        write(root, "craft/skills/kept/SKILL.md", "changed\n")
        write(root, "craft/skills/kept/references/live.md", "changed\n")
        write(root, "craft/skills/new/SKILL.md")
        os.environ["SKILL_EVAL_ROOT"] = root
        sys.modules.pop("evalroot", None)  # another test module may have cached the real root
        spec = importlib.util.spec_from_file_location("eval_hunt", os.path.join(HERE, "eval-hunt.py"))
        cls.eh = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.eh)

    @classmethod
    def tearDownClass(cls):
        os.environ.pop("SKILL_EVAL_ROOT", None)
        cls.tmp.cleanup()

    def test_deleted_skill_dropped(self):
        self.assertEqual(["craft/kept", "craft/new"], sorted(self.eh.changed_skills("HEAD")))

    def test_deleted_reference_dropped(self):
        _, have, _ = self.eh.skill_text("craft/kept", "HEAD")
        self.assertEqual(["SKILL.md", "references/live.md"], have)


if __name__ == "__main__":
    unittest.main()
