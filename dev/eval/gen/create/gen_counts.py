#!/usr/bin/env python3
"""Generate vague-idea's b6 grader: every requirement-group count the reply
states equals that group's `**<PFX>-n:**` entries in the SRD the run wrote.
not_contains: matches a stated count whose group has a different number in
the file. Enumerated, since a regex cannot compare counts; create has no case
generator, so this owns one file."""
import os

D = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "../../../../srd/evals/create--author-from-a-vague-idea/graders")
CH = r'(?:[^"\\]|\\.)'  # one JSON-string char
WRITE = r'"name":"Write","input":\{"file_path":"[^"]*initiatives/[^"]*\.md","content":"'
WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
         "nine", "ten", "eleven", "twelve"]


def file_has(n):
    # The SRD Write holds exactly n entries of the group captured as \1.
    entry = r"\*\*\1-\d+[a-z]?:\*\*"
    other = rf"(?:(?!{entry}){CH})*"
    return rf"{WRITE}{other}(?:{entry}{other}){{{n}}}\""


alts = []
for n in range(1, 13):
    num = rf"(?:{n}|{WORDS[n]})"
    # "GR … 3 requirements" or "`GR`: 3"
    # The gap after the prefix never crosses another group prefix.
    gap = r"(?:(?!\b[A-Z]{2,6}\b)[^\n\"]){0,60}?"
    stated = rf"(?:{gap}\b{num} requirements?\b|`?\)?(?:\*\*)?:?(?:\*\*)?\s*\|?\s*{num}\b)"
    alts.append(rf"{stated}(?<!{file_has(n)}[\s\S]*)")
pattern = (r'"result":"' + CH + r'*?\b`?([A-Z]{2,6})`?\b(?:' + "|".join(alts) + ")")
# Companion: some count is stated at all (the match grader passes on none).
open(os.path.join(D, "b6-counts-stated.md"), "w").write(
    "---\ntype: regex\ntarget: last_message\nflags: \"i\"\n---\n"
    r"`?\b[A-Z]{2,6}\b`?\)?[^\n]{0,60}\b(\d+|one|two|three|four|five|six)\s+requirements?\b"
    r"|`[A-Z]{2,6}`\)?(\*\*)?:?(\*\*)?\s*\|?\s*\d+\b" "\n")
open(os.path.join(D, "b6-counts-match.md"), "w").write(
    "---\ntype: regex\ntarget: trace\nmatch: not_contains\n---\n" + pattern + "\n")
