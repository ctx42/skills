#!/usr/bin/env python3
"""Prints each skill's always-loaded token surface so regressions show up in
review: description chars (paid every session, for every skill) and the
SKILL.md body word count with a rough token estimate (paid on every trigger;
1 token ~ 0.75 words). Reference files are listed with their word counts but
not totalled: they are on-demand and cost nothing until read.
"""
import fnmatch
import os
import re
import sys

sys.dont_write_bytecode = True  # importing evalroot must not leave __pycache__ in the skill
from evalroot import ROOT  # noqa: E402

ROW = "{:<22} {:>6} {:>7} {:>8}"


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def description(text):
    """Return a plain or folded description scalar joined into one line."""
    lines = text.split("\n")
    if not lines or lines[0] != "---":
        return ""
    parts, on = [], False
    for line in lines[1:]:
        if line == "---":
            break
        if line.startswith("description:"):
            on = True
            v = re.sub(r"^description:\s*[>|]?\s*", "", line)
            if v:
                parts.append(v)
            continue
        if on and re.match(r"[a-zA-Z_-]+:", line):
            on = False
        if on:
            parts.append(line.lstrip())
    return " ".join(parts)


def tokens(words):
    """Return the estimated tokens for a word count: 4/3 words per token is
    coarse but stable, good enough to spot growth between two runs."""
    return words * 4 // 3


def files(pred):
    """Return the files under the repo, outside tmp/, that pred accepts,
    sorted."""
    out = []
    for dp, dns, fs in os.walk(ROOT):
        dns[:] = [d for d in dns if os.path.join(dp, d) != os.path.join(ROOT, "tmp")]
        out += [os.path.join(dp, f) for f in fs if pred(os.path.join(dp, f))]
    return sorted(out)


def main():
    print(ROW.format("skill", "desc", "body-w", "~body-t"))
    print(ROW.format("-----", "----", "------", "-------"))
    total_desc = total_body = 0
    for md in files(lambda p: os.path.basename(p) == "SKILL.md"):
        d = os.path.dirname(md)
        parent = os.path.dirname(d)
        owner = os.path.dirname(parent) if os.path.basename(parent) == "skills" else parent
        name = f"{os.path.basename(owner)}:{os.path.basename(d)}"
        text = read(md)
        desc, words = description(text), len(text.split())
        print(ROW.format(name, len(desc), words, tokens(words)))
        total_desc += len(desc)
        total_body += words
    print(ROW.format("-----", "----", "------", "-------"))
    print(ROW.format("total", total_desc, total_body, tokens(total_body)))
    print()
    print("On-demand references (loaded only when a workflow step reads them):")
    for f in files(lambda p: fnmatch.fnmatchcase(p, "*/references/*.md") or fnmatch.fnmatchcase(p, "*/assets/*.md")):
        print(f"  {len(read(f).split()):6d} words  {os.path.relpath(f, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
