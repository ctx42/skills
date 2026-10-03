#!/usr/bin/env python3
"""Generate default-review's tally grader: the reply's per-severity open-finding
counts equal the `- [ ] #n [<severity>` entries in the review file the run
wrote. Enumerated, since a regex can't compare counts (system-check's
gen_terse_b4.py pattern). review has no case generator; this owns one file."""
import os

D = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "../../../../srd/evals/review--default-review-of-a-flawed-srd/graders")
CH = r'(?:[^"\\]|\\.)'  # one JSON-string char
WRITE = r'"name":"Write","input":\{"file_path":"[^"]*login\.review\.md","content":"'


def file_has(sev, n):
    entry = rf"- \[ \] #\d+ \[{sev}\b"
    other = rf"(?:(?!{entry}){CH})*"
    return rf"(?=[\s\S]*{WRITE}{other}(?:{entry}{other}){{{n}}}\")"


def reply_says(sev, n):
    # The result event's "result" field is the final reply; zero may go unsaid.
    reply = rf'"result":"{CH}*?'
    if n == 0:
        return rf"(?![\s\S]*{reply}\b[1-9]\d* {sev}s?\b)"
    # Says n, and no other number, for this severity.
    return (rf"(?=[\s\S]*{reply}\b{n} {sev}s?\b)"
            rf"(?![\s\S]*{reply}\b(?!{n}\b)\d+ {sev}s?\b)")


parts = []
for sev in ("blocker", "major", "minor"):
    parts.append("(?:" + "|".join(file_has(sev, n) + reply_says(sev, n)
                                  for n in range(0, 13)) + ")")
open(os.path.join(D, "b6-tally-matches-file.md"), "w").write(
    "---\ntype: regex\ntarget: trace\n---\n^" + "".join(parts) + "\n")
