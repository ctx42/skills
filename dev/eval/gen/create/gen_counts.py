#!/usr/bin/env python3
"""Generate vague-idea's b6 grader: every requirement-group count the reply
states equals that group's requirement entries in the SRD the run wrote, in the
eval standard's format: a list item opening with the backticked identifier,
"- `<PFX>-n` ...".
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


# The reply's group counts are found and judged with lookaheads from the
# start of the trace only, so the pattern stays inside the regex subset Python
# reads alike: a capture made inside a lookahead keeps its value, and the later
# checks use it as a backreference. Each alternative skips the first k counts
# the reply states, then takes the next one that states n.
MAX_COUNTS = 6  # counts judged per reply; a wrong one past them goes unseen
GAP = r"(?:(?!\b[A-Z]{2,6}\b|\\n)[^\n\"]){0,60}?"


def stated(num):
    # "SW … 3 requirements", "`SW`: 3", "SW, the … group: 3", or
    # "`SW` (…) has 3". The gap after the prefix never crosses another group
    # prefix or a line break, which the JSON reply holds as backslash and n.
    return (rf"(?:{GAP}\b{num} requirements?\b|`?\)?(?:\*\*)?:?(?:\*\*)?\s*\|?\s*{num}\b"
            rf"|`?{GAP}:\s*{num}\b|{GAP}\bhas\s+{num}\b)")


ANY_COUNT = r"\b`?[A-Z]{2,6}`?\b" + stated(r"(?:\d+|" + "|".join(WORDS[1:]) + ")")


def file_has(g, n):
    # An SRD Write holds exactly n entries of the group captured as group g.
    # A list item at a line start; the Write content is JSON, so the newline
    # before it is the two characters backslash and n.
    entry = rf"\\n- `\{g}-\d+[a-z]?`"
    other = rf"(?:(?!{entry}){CH})*"
    return rf"{WRITE}{other}(?:{entry}{other}){{{n}}}\""


alts, g = [], 0
for k in range(MAX_COUNTS):
    for n in range(1, 13):
        g += 1
        num = rf"(?:{n}|{WORDS[n]})"
        alts.append(
            # The reply states n for a group, after k other counts.
            rf'(?=[\s\S]*?"result":"(?:{CH}*?{ANY_COUNT}){{{k}}}{CH}*?\b`?([A-Z]{{2,6}})`?\b{stated(num)})'
            # Only a real group is judged: the trace holds an entry of it, so a
            # word such as SRD or DRAFT is never taken for a group.
            rf"(?=[\s\S]*\\n- `\{g}-\d+[a-z]?`)"
            # No SRD Write holds n entries of that group.
            rf"(?![\s\S]*{file_has(g, n)})")
pattern = "^(?:" + "|".join(alts) + ")"
# Companion: some count is stated at all (the match grader passes on none).
open(os.path.join(D, "b6-counts-stated.md"), "w").write(
    "---\ntype: regex\ntarget: last_message\nflags: \"i\"\n---\n"
    r"`?\b[A-Z]{2,6}\b`?\)?[^\n]{0,60}\b(\d+|one|two|three|four|five|six)\s+requirements?\b"
    r"|`[A-Z]{2,6}`\)?(\*\*)?:?(\*\*)?\s*\|?\s*\(?\d+\b"
    r"|`[A-Z]{2,6}`[^\n]{0,60}?:\s*\d+\b"
    r"|`[A-Z]{2,6}`[^\n]{0,60}?\bhas\s+\d+\b" "\n")
open(os.path.join(D, "b6-counts-match.md"), "w").write(
    "---\ntype: regex\ntarget: trace\nmatch: not_contains\n---\n" + pattern + "\n")
