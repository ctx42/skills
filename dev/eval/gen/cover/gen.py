#!/usr/bin/env python3
"""Generate go/evals/cover--* native cases from fixtures in ./fx."""
import os
import shutil
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../../.."))
EVALS = os.path.join(ROOT, "go/evals")

ENGLISH = "The user writes English; reply in English."
PERSONA = """Automated eval: the user is absent. Whenever the skill would stop and wait
for the user, take the next scripted answer below as the reply and continue
in this same run; never end the run to wait. If none fits, give the most
plausible answer and continue.
Before taking a scripted answer, write out in full, as your reply text, the
message you would send the user at that point.

1. Approved. Go ahead with the plan as proposed."""

SHELL = ["Bash(go:*)", "Bash(gofmt:*)", "Bash(mkdir:*)", "Bash(awk:*)", "Bash(rm:*)"]
BASE = ["Read", "Glob", "Grep", "Skill", "Write", "Edit"]
STYLE = ["skill:style", "sec:style:test", "sec:style:production"]


def scaffold(fx):
    root = os.path.join(HERE, "fx", fx)
    out = ["#!/usr/bin/env bash", "set -euo pipefail"]
    dirs = set()
    files = []
    for d, _, fs in os.walk(root):
        for f in fs:
            p = os.path.relpath(os.path.join(d, f), root)
            files.append(p)
    files.append(".gitignore")
    for i, p in enumerate(sorted(files)):
        dd = os.path.dirname(p)
        if dd and dd not in dirs:
            out.append(f"mkdir -p {dd}")
            dirs.add(dd)
        body = "tmp/\n" if p == ".gitignore" else open(os.path.join(root, p)).read()
        tag = f"EOF_{i}"
        out.append(f"cat > {p} <<'{tag}'")
        out.append(body.rstrip("\n"))
        out.append(tag)
    return "\n".join(out) + "\n"


def fm(d):
    lines = ["---"]
    for k, v in d.items():
        if v is None:
            continue
        lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def tl(target):
    return target if target in ("last_message", "trace") else \
        "{source: file, path: %s}" % target


def regex(pat, target="last_message", neg=False, flags=None, match=None):
    h = {"type": "regex", "target": tl(target)}
    if neg:
        h["match"] = "not_contains"
    if match:
        h["match"] = f'"{match}"'
    if flags:
        h["flags"] = f'"{flags}"'
    return fm(h) + pat + "\n"


def used(tool, pat=None, mn=None, mx=None):
    h = {"type": "tool_used", "tool": tool}
    if pat:
        h["input_match"] = "'" + pat.replace("'", "''") + "'"
    if mn is not None:
        h["min"] = mn
    if mx is not None:
        h["max"] = mx
    if mx == 0:
        h["arm"] = "both"
    return fm(h)


def never(tool, pat=None):
    return used(tool, pat, 0, 0)


def order(before, after):
    def side(t, p):
        q = p.replace("'", "''")
        return "{tool: %s, input_match: '%s'}" % (t, q)
    return fm({"type": "tool_order", "before": side(*before), "after": side(*after)})


def exists(path, yes=True):
    return fm({"type": "file_exists", "path": f'"{path}"', "exists": str(yes).lower()})


def count_matches_list(top=15):
    """Stated "cases added ... N" equals the rows the Tests added list names:
    its nested bullets (one per row under a test function), or its bullets
    when the list is flat. Enumerated, since a regex can't compare counts."""
    item = r"[ \t]*- [^\n]*\n"
    nested = r"[ \t]+- [^\n]*\n"
    top_l = r"- [^\n]*\n"
    alts = []
    for n in range(1, top + 1):
        said = rf"(?=[\s\S]*cases?\s+added[^\d\n]{{0,25}}\b{n}\b)"
        deep = rf"Tests added[^\n]*\n(?:{top_l})*(?:{nested}(?:{top_l})*){{{n}}}(?!{item})"
        flat = rf"Tests added[^\n]*\n(?:{top_l}){{{n}}}(?!{item})"
        alts.append(rf"{said}[\s\S]*?(?:{deep}|{flat})")
    return "^(?:" + "|".join(alts) + ")"


# Bash command patterns, matched against the JSON-serialised tool input. S is
# one JSON-string char: a command holds escaped quotes (\"), which [^"]* would
# stop at. A $ inside shell double quotes arrives as \\$.
S = r'(?:[^"\\]|\\.)*'


def run_family(fam):
    return r'"command":"' + S + r'go test' + S + r'-run' + S + r'\^' + fam + r'\((?:\\\\)?\$\|_\)'


WHOLE_PKG_COVER = r'"command":"(?!' + S + r'-run)' + S + r'go test' + S + r'-cover'
UNC = r"(un-?coverable|never be covered|can(no|')?t be covered|unreachable)"
# A write: Write/Edit, or a Bash heredoc or append (`cat > f <<`, `cat >> f`).
WRITE_IN = (r'(?:"name":"(?:Write|Edit)"|"name":"Bash","input":\{"command":"'
            r'(?:[^"\\]|\\.)*\bcat >>? ?\S+)[^\n]*')


def case(name, fx, query, tags, graders, *, persona=False, shell=True,
         extra_tools=(), turns=80, timeout=300):
    d = os.path.join(EVALS, f"cover--{name}")
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, "graders"))
    tools = BASE + list(extra_tools) + (SHELL if shell else [])
    alltags = [f"case:cover--{name}", "skill:cover"] + tags + (["needs-shell"] if shell else [])
    asp = ENGLISH + ("\n" + PERSONA if persona else "")
    head = ["---",
            f"tags: [{', '.join(alltags)}]",
            "runs: 1",
            f"max_turns: {turns}",
            f"timeout_seconds: {timeout}",
            f"allowed_tools: [{', '.join(tools)}]",
            "append_system_prompt: |"]
    head += ["  " + l if l else "" for l in asp.split("\n")]
    head += ["---", "", query, ""]
    open(os.path.join(d, "prompt.md"), "w").write("\n".join(head))
    open(os.path.join(d, "case.yaml"), "w").write(
        f'schema_version: "1.1"\nname: cover--{name}\ncontext:\n  scaffold_script: scaffold.sh\n')
    sp = os.path.join(d, "scaffold.sh")
    open(sp, "w").write(scaffold(fx))
    os.chmod(sp, 0o755)
    for gname, body in graders.items():
        open(os.path.join(d, "graders", gname + ".md"), "w").write(body)


T = {k: f"sec:cover:{k}" for k in [
    "usage", "target", "controls", "per-function-loop",
    "classify-each-uncovered-line", "plan-file-package-module", "write",
    "verify", "un-coverable-categories", "output", "self-learning"]}


def tags(*keys, style=True):
    return [T[k] for k in keys] + (STYLE if style else [])


LOOP = ("target", "per-function-loop", "classify-each-uncovered-line",
        "write", "verify", "output")

# 1 -------------------------------------------------------------------------
case("single-function-in-isolation", "f1", "/go:cover func=Parse", tags(*LOOP), {
    "b1-no-plan-gate": regex(r"error - ", "pkg/cfg/parse_test.go"),
    "b1-no-coined-suffix": regex(r"func Test_Parse_(?!tabular\()", "pkg/cfg/parse_test.go",
                                 neg=True),
    "b2-run-family-only": used("Bash", run_family("Test_Parse"), mn=1),
    "b2-no-whole-package-cover": never("Bash", WHOLE_PKG_COVER),
    "b2-before-is-own-range": regex(r"66\.7|\b4\s*(/|of)\s*6\b"),
    "b2-load-not-credited": regex(r"83\.3|\b5\s*(/|of)\s*6\b", neg=True),
    "b3-empty-row": regex(r'""', "pkg/cfg/parse_test.go"),
    "b3-remeasured": exists("tmp/cover/Parse.after"),
    "b3-after-full": regex(r"100(\.0)?\s*%|\b6\s*(/|of)\s*6\b"),
    "b4-have-want": regex(r"(?=[\s\S]*\bhave\b)(?=[\s\S]*\bwant\b)", "pkg/cfg/parse_test.go"),
    "b4-no-got": regex(r"\bgot\b", "pkg/cfg/parse_test.go", neg=True),
    "b4-error-naming": regex(r'"error - [^"]+"[\s\S]*"error - [^"]+"', "pkg/cfg/parse_test.go"),
})

# 2 -------------------------------------------------------------------------
case("package-target-is-plan-first", "f2", "/go:cover ./pkg/svc",
     tags(*LOOP, "plan-file-package-module"), persona=True, graders={
    **{f"b3-{f.lower()}-after": exists(f"tmp/cover/{f}.after")
       for f in ["Clamp", "Sign", "Pad", "Trunc"]},
    "b3-clamp-done-before-text": order(
        ("Bash", r'"command":"' + S + r'Clamp\.after'),
        ("Edit", r'"file_path":"[^"]*text_test\.go')),
    "b3-pad-done-before-trunc-measured": order(
        ("Bash", r'"command":"' + S + r'Pad\.after'),
        ("Bash", r'"command":"' + S + r'Trunc\.after')),
    "b5-count-reported": regex(r"\b\d+\s+(new\s+)?(cases?|rows?|subtests?)\b"
                               r"|cases?\s+added[^\d\n]{0,25}\d+", flags="i"),
    "b5-count-matches-list": regex(count_matches_list(), flags="im"),
})

# 3 -------------------------------------------------------------------------
NET_T = tags(*LOOP, "plan-file-package-module", "un-coverable-categories", "controls")
case("deferred-and-uncoverable-are-reported", "f3", "/go:cover ./pkg/net", NET_T, {
    "b1-easy-bad-address": regex(r"bad address|missing port", "pkg/net/dial_test.go", flags="i"),
    "b1-network-deferred": regex(r"deferred[\s\S]*dial\.go:[0-9,–\- ]*\b3[5-9]\b", flags="i"),
    "b1-defensive-uncoverable": regex(UNC + r"[\s\S]*dial\.go:3[23]\b", flags="i"),
    "b2-defensive-not-attempted": regex(WRITE_IN + r"empty host:port", "trace", neg=True),
    "b5-mustdial-panic-asserted": regex(WRITE_IN + r"Test_MustDial[^\n]*recover\(\)", "trace"),
    "b6-retry-sleep-deferred": regex(
        r"(deferred|complex)[\s\S]*retry\.go:[0-9,–\- ]*\b1[34]\b[^\n]*(sleep|wait|100\s?ms|slow)",
        flags="i"),
    "b7-no-coined-suffix-write": never(
        "Write", r"func Test_(Dial|MustDial|Retry)_(?!tabular\(|emptyAddress\(|firstTry\()\w+\("),
    "b7-no-coined-suffix-edit": never(
        "Edit", r"func Test_(Dial|MustDial|Retry)_(?!tabular\(|emptyAddress\(|firstTry\()\w+\("),
}, persona=True)

# 4 -------------------------------------------------------------------------

# 5 -------------------------------------------------------------------------

# 6 -------------------------------------------------------------------------

# 7 -------------------------------------------------------------------------

# 8 -------------------------------------------------------------------------

# 9 -------------------------------------------------------------------------

# 10 ------------------------------------------------------------------------
