#!/usr/bin/env python3
"""Generate the terse-output count graders: enumerate N so a regex can compare
the count the reply states with the highest id in the file the run wrote."""
import os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../srd/evals/system-check--terse-output/graders")

def last_said(n, noun):
    return rf"(?=[\s\S]*\b{n} {noun}\b(?![\s\S]*\b\d+ {noun}\b))"

def write_has_max(path_re, item, n):
    return (rf'(?=[\s\S]*"name":"Write","input":\{{(?=[^\n]*"file_path":"[^"]*{path_re}")'
            rf'(?![^\n]*{item(n + 1)})(?=[^\n]*{item(n)}))')

qnoun = r"(?:open )?questions?"
q = lambda n: rf"\*\*Q{n}\*\*"
alts = [write_has_max(r"labeling\.questions\.md", q, n) + last_said(n, qnoun) for n in range(3, 16)]
open(os.path.join(D, "b4-question-count-matches-file.md"), "w").write(
    "---\ntype: regex\ntarget: trace\n---\n^(?:" + "|".join(alts) + ")\n")

fnoun = r"(?:open )?(?:review )?findings?"
f = lambda n: rf"#{n} \["
alts = [write_has_max(r"labeling\.review\.md", f, n) + last_said(n, fnoun) for n in range(1, 31)]
open(os.path.join(D, "b4-finding-total-matches-file.md"), "w").write(
    "---\ntype: regex\ntarget: trace\n---\n^(?![\\s\\S]*\\b\\d+ " + fnoun + "\\b)|^(?:" + "|".join(alts) + ")\n")
