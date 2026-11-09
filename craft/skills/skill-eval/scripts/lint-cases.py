#!/usr/bin/env python3
"""Lints the native eval cases (<group>/evals/<case>/) against
references/native-cases.md. Mechanical checks only: it never edits files.
Called by lint-skills.py; prints ERROR and WARN lines and the counts as its
last line ("cases: N error(s), M warning(s)"), exit 1 on any error.

For each group with an evals/ dir it checks:
  - every evals.json scenario has a case `<skill>--<name>` (gate and other
    suffixed variants `<skill>--<name>--<suffix>` count) unless it carries
    `requires` (a live service no case can stand in for), and every case
    belongs to a scenario,
  - prompt.md tags: `case:<dir>` present; each skill:/sec:/ref: tag names a
    real skill, `## ` section, or reference; any other tag is a known free
    tag (FREE_TAGS),
  - needs-shell is tagged exactly when allowed_tools grants Bash, and always
    when a tagged skill injects shell output (!`...`); a needs-shell case (run
    by eval-shell) has no mocks/ and only the grader types that runner
    supports,
  - append_system_prompt exists and opens with the English line,
  - max_turns <= 80; timeout_seconds <= 300, or <= 600 with the fan-out or
    long tag,
  - every grader pattern (regex body, input_match) is inside the JavaScript
    subset Python reads alike (jsregex.check). A lookbehind of varying width
    is valid JavaScript Python cannot run: a warning in a case `claude plugin
    eval` grades, an error in a needs-shell case, which Python grades,
  - at least one grader asserts that something happened (a case of only
    not_contains, max: 0, and exists: false graders passes on an empty
    reply), and a tool_used max: 0 grader names a tool the run may call,
  - a case mock fixture that shadows a suite one (same path under mocks/,
    e.g. the frozen srd-standard.md) is byte-identical to it: case mocks
    cannot reference suite files, so the suite file is the source and the
    copies must follow it,
  - every expectations bullet is checked by a grader, a probe, or the
    scenario's blind_only list, and by nothing else when blind_only.
"""
import json
import os
import re
import sys

sys.dont_write_bytecode = True  # importing the helpers must not leave __pycache__ in the skill
import jsregex  # noqa: E402
from eval_graders import asserts, can_use  # noqa: E402
from evalroot import ROOT  # noqa: E402

ENGLISH = "The user writes English; reply in English."
FREE_TAGS = ("needs-shell", "fan-out", "long")
SHELL_GRADERS = ("regex", "tool_used", "tool_order", "file_exists")
MAX_TURNS, TIMEOUT, TIMEOUT_FANOUT = 80, 300, 600

count = {"errors": 0, "warnings": 0}


def err(msg):
    print(f"ERROR  {msg}")
    count["errors"] += 1


def warn(msg):
    print(f"WARN   {msg}")
    count["warnings"] += 1


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def split(text):
    """Return the front matter text and the body of a file."""
    m = re.match(r"---\n(.*?)\n---\n?(.*)\Z", text, re.S)
    return (m.group(1), m.group(2)) if m else ("", text)


def unquote(v):
    if len(v) >= 2 and v[0] == v[-1] == "'":
        return v[1:-1].replace("''", "'")
    if len(v) >= 2 and v[0] == v[-1] == '"':
        return json.loads(v)
    return v


def scalar(fm, key):
    """Return a top-level scalar with one layer of YAML quotes stripped, or
    None when the key is absent."""
    m = re.search(rf"^{key}:[ \t]*(.*)$", fm, re.M)
    return unquote(m.group(1).strip()) if m else None


def number(v):
    """Return v as a number, or None when it is not one."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def input_matches(fm):
    """Return every input_match value anywhere in the front matter, flow maps
    included."""
    pat = r"""input_match:\s*('(?:[^']|'')*'|"(?:[^"\\]|\\.)*"|[^,}\n]+)"""
    return [unquote(m.group(1).strip()) for m in re.finditer(pat, fm)]


def check_pattern(where, pattern, flags, shell):
    why = jsregex.check(pattern, flags or "")
    if why == [jsregex.VARIABLE_LOOKBEHIND] and not shell:
        warn(f"{where}: {why[0]}; claude plugin eval grades it, Python tools skip it")
    elif why:
        err(f"{where}: pattern is outside the JavaScript subset Python reads alike: {'; '.join(why)}")


def known_tags(group):
    """Return the tags --list-tags prints for every skill of a group."""
    tags = set()
    skills = os.path.join(ROOT, group, "skills")
    for s in sorted(os.listdir(skills)):
        md = os.path.join(skills, s, "SKILL.md")
        if not os.path.isfile(md):
            continue
        tags.add(f"skill:{s}")
        for m in re.finditer(r"^## (.+)$", read(md), re.M):
            tags.add(f"sec:{s}:{slug(m.group(1))}")
        refs = os.path.join(skills, s, "references")
        if os.path.isdir(refs):
            tags.update(f"ref:{s}/{r[:-3]}" for r in os.listdir(refs) if r.endswith(".md"))
    return tags


def scenarios(group):
    """Return "<skill>--<name>" -> (evals.json path, requires) for a group."""
    out = {}
    skills = os.path.join(ROOT, group, "skills")
    for s in sorted(os.listdir(skills)):
        f = os.path.join(skills, s, "evals", "evals.json")
        if not os.path.isfile(f):
            continue
        for e in json.loads(read(f))["evals"]:
            out[f"{s}--{slug(e['name'])}"] = (os.path.relpath(f, ROOT), bool(e.get("requires")))
    return out


def walk(d):
    """Return every file under d, as paths relative to it."""
    return sorted(os.path.relpath(os.path.join(top, f), d)
                  for top, _, files in os.walk(d) for f in files)


def lint_fixture_copies(group, case):
    case_mocks = os.path.join(ROOT, group, "evals", case, "mocks")
    suite_mocks = os.path.join(ROOT, group, "evals", "mocks")
    if not (os.path.isdir(case_mocks) and os.path.isdir(suite_mocks)):
        return
    for rel in walk(case_mocks):
        if "fixtures" not in rel.split(os.sep):
            continue
        src = os.path.join(suite_mocks, rel)
        if not os.path.isfile(src):
            continue
        with open(src, "rb") as a, open(os.path.join(case_mocks, rel), "rb") as b:
            same = a.read() == b.read()
        if not same:
            to = os.path.relpath(os.path.join(case_mocks, rel), ROOT)
            err(f"{to}: differs from the suite copy — cp {os.path.relpath(src, ROOT)} {to}")


def lint_case(group, case, known):
    lint_fixture_copies(group, case)
    rel = f"{group}/evals/{case}"
    fm, _ = split(read(os.path.join(ROOT, rel, "prompt.md")))

    tm = re.search(r"^tags:\s*\[([^\]]*)\]", fm, re.M)
    tags = [t.strip() for t in tm.group(1).split(",") if t.strip()] if tm else []
    if f"case:{case}" not in tags:
        err(f"{rel}/prompt.md: tags lack case:{case}")
    for t in tags:
        if t.startswith("case:"):
            if t != f"case:{case}":
                err(f"{rel}/prompt.md: foreign case tag {t}")
        elif re.match(r"(skill|sec|ref):", t):
            if t not in known:
                err(f"{rel}/prompt.md: tag {t} names no skill, section, or reference")
        elif t not in FREE_TAGS:
            err(f"{rel}/prompt.md: unknown tag {t} (free tags: {', '.join(FREE_TAGS)})")

    # eval-changed grants Bash only to needs-shell cases.
    shell = "needs-shell" in tags
    am = re.search(r"^allowed_tools:\s*\[([^\]]*)\]", fm, re.M)
    bash = bool(am and re.search(r"(^|[\s,])Bash\b", am.group(1)))
    if bash and not shell:
        err(f"{rel}/prompt.md: allowed_tools has Bash but tags lack needs-shell")
    if shell and not bash:
        err(f"{rel}/prompt.md: tagged needs-shell but allowed_tools has no Bash(<cmd>:*)")
    for t in tags:
        s = t[len("skill:"):] if t.startswith("skill:") else None
        md = s and os.path.join(ROOT, group, "skills", s, "SKILL.md")
        if md and not shell and os.path.isfile(md) and "!`" in read(md):
            err(f"{rel}/prompt.md: skill {s} injects shell output (!`…`) but tags lack needs-shell")

    asp = re.search(r"^append_system_prompt:\s*\|[-+]?\n[ \t]+(.*)$", fm, re.M)
    if not asp:
        err(f"{rel}/prompt.md: no append_system_prompt (it opens with the English line)")
    elif asp.group(1).strip() != ENGLISH:
        err(f'{rel}/prompt.md: append_system_prompt does not open with "{ENGLISH}"')

    turns = number(scalar(fm, "max_turns"))
    if not (turns and turns > 0):
        err(f"{rel}/prompt.md: max_turns missing")
    elif turns > MAX_TURNS:
        err(f"{rel}/prompt.md: max_turns {turns:g} > {MAX_TURNS}")
    timeout = number(scalar(fm, "timeout_seconds"))
    cap = TIMEOUT_FANOUT if "fan-out" in tags or "long" in tags else TIMEOUT
    if not (timeout and timeout > 0):
        err(f"{rel}/prompt.md: timeout_seconds missing")
    elif timeout > cap:
        hint = " (fan-out cases tag fan-out, other long runs long, for 600)" if cap == TIMEOUT else ""
        err(f"{rel}/prompt.md: timeout_seconds {timeout:g} > {cap}{hint}")

    if shell and os.path.isdir(os.path.join(ROOT, rel, "mocks")):
        err(f"{rel}: needs-shell cases run through eval-shell, which serves no mocks")
    graders = os.path.join(ROOT, rel, "graders")
    if not os.path.isdir(graders):
        err(f"{rel}: no graders/")
        return
    allowed = [m.group(0) for m in re.finditer(r"[A-Za-z_][\w-]*(\([^)]*\))?", am.group(1))] if am else []
    positive = False
    for g in sorted(f for f in os.listdir(graders) if f.endswith(".md")):
        where = f"{rel}/graders/{g}"
        gfm, body = split(read(os.path.join(graders, g)))
        gtype = scalar(gfm, "type")
        if not gtype:
            err(f"{where}: no type")
            continue
        fields = {"type": gtype, **{k: scalar(gfm, k) for k in ("match", "min", "max", "exists")}}
        if asserts(fields):
            positive = True
        tool = scalar(gfm, "tool")
        if (gtype == "tool_used" and tool and fields["max"] is not None
                and number(fields["max"]) == 0 and not can_use(tool, allowed, shell)):
            err(f"{where}: max: 0 on {tool}, which the run cannot call, so it never fails"
                " — allow the tool or drop the grader")
        for im in input_matches(gfm):
            check_pattern(f"{where} input_match", im, "", shell)
        if shell and gtype not in SHELL_GRADERS:
            err(f"{where}: needs-shell cases run through eval-shell, which grades only {', '.join(SHELL_GRADERS)}")
        if shell and re.search(r"^target:\s*mock_calls", gfm, re.M):
            err(f"{where}: needs-shell cases run without mocks; no mock_calls target")
        if gtype == "regex":
            pattern = body[:-1] if body.endswith("\n") else body
            if not pattern:
                err(f"{where}: empty pattern")
            else:
                check_pattern(where, pattern, scalar(gfm, "flags"), shell)
    if not positive:
        err(f"{rel}: no grader asserts that something happened, so an empty reply passes")


def lint_traceability(group, cases):
    """Every expectations bullet is checked by something, or says it is not:
    a grader b<N>-* in one of the scenario's cases (gate and stop variants
    count), a probe listing "<scenario-slug>#b<N>" in its `bullets`, or the
    scenario's `blind_only` list (graded only in a blind round)."""
    skills = os.path.join(ROOT, group, "skills")
    for s in sorted(os.listdir(skills)):
        ef = os.path.join(skills, s, "evals", "expectations.json")
        if not os.path.isfile(ef):
            continue
        rel = os.path.relpath(ef, ROOT)
        pf = os.path.join(skills, s, "evals", "probes.json")
        exps = json.loads(read(ef))["expectations"]
        sizes = {slug(e["name"]): len(e["expected_behavior"]) for e in exps}
        probed = set()
        if os.path.isfile(pf):
            for p in json.loads(read(pf))["probes"]:
                for b in p.get("bullets") or []:
                    m = re.fullmatch(r"([a-z0-9-]+)#b(\d+)", b)
                    if not m or m.group(1) not in sizes or not 1 <= int(m.group(2)) <= sizes[m.group(1)]:
                        err(f'{os.path.relpath(pf, ROOT)}: probe {p.get("id")}: bullet "{b}" names no expectations bullet')
                    else:
                        probed.add(b)
        for e in exps:
            sl, n_bullets = slug(e["name"]), len(e["expected_behavior"])
            graded = set()
            for case in cases:
                if case != f"{s}--{sl}" and not case.startswith(f"{s}--{sl}--"):
                    continue
                gd = os.path.join(ROOT, group, "evals", case, "graders")
                if os.path.isdir(gd):
                    graded.update(int(m.group(1)) for g in os.listdir(gd)
                                  if (m := re.match(r"b(\d+)-", g)))
            blind = set(e.get("blind_only") or [])
            for i in range(1, n_bullets + 1):
                n = sum([i in graded, f"{sl}#b{i}" in probed, i in blind])
                if n == 0:
                    err(f"{rel}: {e['name']} b{i} has no grader, probe, or blind_only entry")
                if i in blind and n > 1:
                    err(f"{rel}: {e['name']} b{i} is blind_only but is also checked — drop it from blind_only")
            for i in sorted(blind):
                if not (isinstance(i, int) and 1 <= i <= n_bullets):
                    err(f"{rel}: {e['name']}: blind_only {i} names no bullet")


def main():
    for group in sorted(os.listdir(ROOT)):
        evals = os.path.join(ROOT, group, "evals")
        if not os.path.isfile(os.path.join(ROOT, group, ".claude-plugin", "plugin.json")) \
                or not os.path.isdir(evals):
            continue
        known, scen = known_tags(group), scenarios(group)
        cases = sorted(d for d in os.listdir(evals) if os.path.isfile(os.path.join(evals, d, "prompt.md")))
        covered = set()
        for case in cases:
            lint_case(group, case, known)
            parts = case.split("--")
            key = f"{parts[0]}--{parts[1] if len(parts) > 1 else ''}"
            if key in scen:
                covered.add(key)
            else:
                err(f"{group}/evals/{case}: no evals.json scenario {key}")
        for key, (src, requires) in scen.items():
            if key not in covered and not requires:
                err(f"{src}: scenario {key.split('--')[1]} has no native case {group}/evals/{key}")
        lint_traceability(group, cases)
    print(f"cases: {count['errors']} error(s), {count['warnings']} warning(s)")
    return 1 if count["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
