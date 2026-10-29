"""Where the skills repo under test lives, for every eval script.

The scripts ship inside the skill-eval skill, so they cannot find the repo
from their own path. The root is $SKILL_EVAL_ROOT when set, else the git top
level of the working directory, else the working directory itself.
"""
import glob
import os
import subprocess


def find_root():
    """Return the absolute root of the skills repo under test."""
    env = os.environ.get("SKILL_EVAL_ROOT")
    if env:
        return os.path.realpath(env)
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True)
    top = r.stdout.strip() if r.returncode == 0 else ""
    return os.path.realpath(top or os.getcwd())


def groups(root):
    """Return the plugin groups under root: top-level directories holding
    skills/<name>/SKILL.md, sorted; tmp/ and hidden directories excluded."""
    found = {os.path.relpath(p, root).split(os.sep)[0]
             for p in glob.glob(os.path.join(root, "*", "skills", "*", "SKILL.md"))}
    return tuple(sorted(g for g in found if g != "tmp" and not g.startswith(".")))


ROOT = find_root()
GROUPS = groups(ROOT)
