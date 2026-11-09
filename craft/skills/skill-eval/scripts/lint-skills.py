#!/usr/bin/env python3
"""Lints every skill in the repo under test against the conventions recorded
in references/authoring.md. Mechanical checks only: it never edits files.

A "skill" is any directory containing a SKILL.md, outside tmp/ and outside any
assets/ dir. Eval workspaces live in tmp/ and hold snapshots of skills under
test; a SKILL.md under assets/ is an eval fixture, a skill a scenario acts on,
not one this repo ships. Neither is source, and linting either would fail on
files that are meant to be flawed. For each skill this script checks:
  - SKILL.md exists and carries a `## Usage` block,
  - eval scenarios exist in evals/evals.json, with their pass criteria in the
    separate evals/expectations.json (so a run can be given the scenario
    without its rubric), and the two agree id for id,
  - front matter has name + description, name equals the directory name,
  - the description stays near the ~350-char aim (warns past 500) and uses no
    first/second person (warning only),
  - the SKILL.md body stays under ~500 lines / ~5000 tokens (warning only),
  - the body carries the output-discipline line ("Report tersely" or the
    "no preamble or narration" phrasing),
  - the body has a `## Self-learning` block (warning only),
  - relative links resolve, and no positional argument placeholder ($N) is
    left in the text the skill reads,
  - the argument-hint uses bare words and max=N, and a skill taking modes or
    controls carries the unknown-token sentence,
  - every bundled .md reference over ~100 lines starts with a Contents list,
  - Markdown prose wraps at ~80 columns (warning only).

It then cross-checks .claude-plugin/marketplace.json (if present): every
plugin `source` must be a real plugin directory (with
.claude-plugin/plugin.json), and every shipped skill on disk must live under
exactly one plugin's skills/ directory (skills under .claude/skills/ are
project-local and exempt). It checks the manifest versions (dev/version.sh),
that every JSON file git sees parses, the native eval cases (lint-cases.py),
and the free eval checks (eval-check.py).

Exit status is 0 when clean, 1 when any error is found. Warnings do not fail.
"""
import glob
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True  # importing evalroot must not leave __pycache__ in the skill
from evalroot import ROOT  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
WRAP_LIMIT = 80  # the house wrap for Markdown prose (Content hygiene)

count = {"errors": 0, "warnings": 0}


def err(msg):
    print(f"ERROR  {msg}")
    count["errors"] += 1


def warn(msg):
    print(f"WARN   {msg}")
    count["warnings"] += 1


def rel(path):
    return os.path.relpath(path, ROOT)


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def lines_of(text):
    """Return the lines of text as awk reads them: no record after a final
    newline."""
    lines = text.split("\n")
    return lines[:-1] if lines and lines[-1] == "" else lines


def frontmatter(text):
    """Return the lines between the first two --- lines, when the file opens
    with one."""
    lines = lines_of(text)
    if not lines or lines[0] != "---":
        return []
    out = []
    for line in lines[1:]:
        if line == "---":
            break
        out.append(line)
    return out


def joined(fm, key):
    """Return a front matter value joined from its folded or plain lines into
    one string, as the description and argument-hint checks read it."""
    parts, on = [], False
    for line in fm:
        if line.startswith(f"{key}:"):
            on = True
            v = re.sub(rf"^{key}:\s*" + (r"[>|]?\s*" if key == "description" else ""), "", line)
            if v or key != "description":
                parts.append(v)
            continue
        if on and re.match(r"[a-zA-Z_-]+:", line):
            on = False
        if on:
            parts.append(line.lstrip())
    return " ".join(parts)


def check_wrap(path):
    """Warn on Markdown prose wider than WRAP_LIMIT. Skips fenced code blocks
    and table rows (aligned columns legitimately run wide), and flags a line
    only when it stays breakable past the limit: a space after the limit means
    it could have wrapped. Long URLs, paths, and links are exempt. Width is
    characters; rare double-width glyphs (emoji) undercount by one."""
    if not os.path.isfile(path):
        return
    fence = False
    for n, line in enumerate(lines_of(read(path)), 1):
        if re.match(r"\s*```", line):
            fence = not fence
            continue
        if fence or re.match(r"\s*\|", line):
            continue
        if len(line) > WRAP_LIMIT and " " in line[WRAP_LIMIT:]:
            warn(f"{rel(path)}:{n} ({len(line)} cols) exceeds {WRAP_LIMIT}-col wrap")


def link_targets(path):
    """Return the relative link targets of a Markdown file that name a path,
    outside fenced code blocks and blockquotes: a template's placeholder
    targets and an authoring guide's Bad/Good specimens are content to read,
    not navigation to follow."""
    out, fence = [], False
    for line in lines_of(read(path)):
        if re.match(r"\s*```", line):
            fence = not fence
            continue
        if fence or re.match(r"\s*>", line):
            continue
        for m in re.finditer(r"\]\(([^)#][^)]*)\)", line):
            t = m.group(1).split("#", 1)[0]
            if not re.match(r"(https?:|mailto:|#)", t) and "/" in t:
                out.append(t)
    return out


def ids(path):
    """Return the numeric "id" values of a JSON file as a sorted,
    space-terminated list."""
    found = sorted(int(m.group(1)) for m in re.finditer(r'"id"\s*:\s*(\d+)', read(path)))
    return "".join(f"{i} " for i in found)


def lint_skill(d):
    name, r = os.path.basename(d), rel(d)
    skill_md, readme = os.path.join(d, "SKILL.md"), os.path.join(d, "README.md")
    evals, expects = os.path.join(d, "evals", "evals.json"), os.path.join(d, "evals", "expectations.json")
    body = read(skill_md)
    fm = frontmatter(body)

    if not any(re.match(r"name:\s", ln) for ln in fm):
        err(f"{r}: frontmatter missing 'name:'")
    if not any(re.match(r"description:\s*([|>].*)?$|description:\s*\S", ln) for ln in fm):
        err(f"{r}: frontmatter missing 'description:'")
    declared = next((re.sub(r"^name:\s*", "", ln).rstrip() for ln in fm if re.match(r"name:\s", ln)), "")
    if declared != name:
        err(f"{r}: frontmatter name '{declared}' != directory '{name}'")

    # Description size and point of view: the aim is ~350 chars; warn only
    # past 500 so a trigger-rich description has headroom.
    desc = joined(fm, "description")
    if len(desc) > 500:
        warn(f"{r}: description is {len(desc)} chars (aim <= ~350)")
    if re.search(r"(^|[^a-zA-Z])(I|you|your)([^a-zA-Z]|$)", desc, re.I):
        warn(f"{r}: description uses first/second person")

    # Body size: tokens are estimated as bytes/4 (no tokenizer dependency).
    n_lines = body.count("\n")
    tokens = os.path.getsize(skill_md) // 4
    if n_lines > 500:
        warn(f"{r}: SKILL.md is {n_lines} lines (aim <= ~500)")
    if tokens > 5000:
        warn(f"{r}: SKILL.md is ~{tokens} tokens (aim <= ~5000)")

    if not re.search(r"report tersely|no preamble or narration", body, re.I):
        err(f"{r}: SKILL.md lacks the output-discipline line")
    if not re.search(r"^## Self-learning", body, re.M):
        warn(f"{r}: SKILL.md has no '## Self-learning' block")
    if not re.search(r"^##\s+Usage", body, re.M):
        err(f"{r}: SKILL.md has no '## Usage' section")

    # Relative links resolve. A reference file lives one directory deeper than
    # SKILL.md, so a sibling path copied from a SKILL.md into a references/
    # file is one `../` short and silently points nowhere.
    for f in [skill_md] + sorted(glob.glob(os.path.join(d, "references", "*.md"))):
        for t in link_targets(f):
            if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(f), t))):
                err(f"{rel(f)}: link target '{t}' does not exist")

    # No positional argument placeholders anywhere the skill reads: positional
    # substitution is zero-indexed, so "$1 is the first token" is off by one.
    posarg = []
    for top in (skill_md, os.path.join(d, "references"), os.path.join(d, "assets")):
        files = [top] if os.path.isfile(top) else sorted(
            os.path.join(dp, f) for dp, _, fs in os.walk(top) for f in fs)
        for f in files:
            with open(f, "rb") as fh:
                if re.search(rb"(^|[^\\$])\$[0-9]", fh.read(), re.M):
                    posarg.append(f)
    if posarg:
        err(f"{r}: positional argument placeholder ($N) in:\n       "
            + "".join(f"{f} " for f in posarg) + "— name the token in prose instead")

    # Argument conventions: bare flags, never --flag; one cap key, max=N; a
    # skill taking modes or controls carries the unknown-token sentence.
    hint = joined(fm, "argument-hint")
    if re.search(r"(^|[^-])--[a-z]", hint):
        err(f"{r}: argument-hint uses a --flag; use a bare word or key=value")
    if re.search(r"max_[a-z]+=|max <", hint):
        err(f"{r}: argument-hint caps with something other than max=N")
    if re.search(r"[=|]", hint) and "say it was not recognized" not in re.sub(r"\s+", " ", body):
        err(f"{r}: takes modes or controls but lacks the unknown-token sentence")

    # Scenarios in evals/evals.json, pass criteria in evals/expectations.json:
    # separate files, so a run can be handed a scenario without its rubric.
    if os.path.isfile(evals):
        text = read(evals)
        n = sum(1 for ln in lines_of(text) if re.search(r'"query"\s*:', ln))
        if n < 3:
            err(f"{r}: evals/evals.json has {n} scenario(s) (want >= 3)")
        if '"expected_behavior"' in text:
            err(f"{r}: evals/evals.json carries 'expected_behavior' — it belongs in evals/expectations.json")
        if os.path.isfile(expects):
            if '"expected_behavior"' not in read(expects):
                err(f"{r}: evals/expectations.json has no 'expected_behavior' checks")
            sids, eids = ids(evals), ids(expects)
            if sids != eids:
                err(f"{r}: evals ids [{sids}] != expectations ids [{eids}]")
        else:
            err(f"{r}: no evals/expectations.json")
    else:
        err(f"{r}: no evals/evals.json")

    if os.path.isfile(readme):
        err(f"{r}: has a README.md — skills ship none; fold it into SKILL.md")

    check_wrap(skill_md)
    check_wrap(readme)
    for pattern in ("*.md", "references/*.md", "assets/*.md"):
        for f in sorted(glob.glob(os.path.join(d, pattern))):
            if os.path.basename(f) in ("SKILL.md", "README.md") or not os.path.isfile(f):
                continue
            check_wrap(f)
            text = read(f)
            n = text.count("\n")
            # 40 lines, not 25: a leading banner comment may push the heading down.
            head = lines_of(text)[:40]
            if n > 100 and not any(re.match(r"#+\s+Contents|Contents", ln, re.I) for ln in head):
                warn(f"{rel(f)}: {n} lines, no Contents list")


def skill_dirs():
    """Return the skill directories, sorted: every dir holding a SKILL.md,
    outside tmp/, any assets/ dir, and .claude/worktrees."""
    out = []
    for dp, dns, fs in os.walk(ROOT):
        dns[:] = [x for x in dns if x != "assets" and os.path.join(dp, x) != os.path.join(ROOT, "tmp")
                  and not (x == "worktrees" and os.path.basename(dp) == ".claude")]
        if "SKILL.md" in fs:
            out.append(dp)
    return sorted(out, key=lambda p: os.path.join(p, "SKILL.md"))


def check_marketplace(skill_paths):
    """Every plugin `source` is a real plugin directory, and every shipped
    skill lives under exactly one plugin's skills/ dir. Skills under
    .claude/skills/ are project-local maintainer tools, exempt like a
    git-ignored skill (a local, unshipped plugin)."""
    path = os.path.join(ROOT, ".claude-plugin", "marketplace.json")
    if not os.path.isfile(path):
        warn("no .claude-plugin/marketplace.json — skipping marketplace checks")
        return
    try:
        plugins = json.loads(read(path)).get("plugins")
    except (ValueError, AttributeError):
        plugins = None
    if not isinstance(plugins, list):
        err('marketplace.json: no "plugins" array (invalid or malformed)')
        return
    sources = []
    for p in plugins:
        if not isinstance(p, dict) or not p.get("name"):
            continue
        src = str(p.get("source", ""))
        src = src[2:] if src.startswith("./") else src
        sources.append(src)
        if not os.path.isfile(os.path.join(ROOT, src, ".claude-plugin", "plugin.json")):
            err(f"marketplace: plugin '{p['name']}' source '{src}' has no .claude-plugin/plugin.json")
    for sp in skill_paths:
        if sp.startswith(".claude/skills/"):
            continue
        if subprocess.run(["git", "-C", ROOT, "check-ignore", "-q", sp]).returncode == 0:
            continue
        hits = sum(1 for s in sources if sp.startswith(f"{s}/skills/"))
        if hits != 1:
            err(f"skill '{sp}' sits under {hits} plugin sources (want exactly 1)")


def check_versions():
    """Every manifest version matches the VER file; dev/version.sh owns the
    version logic."""
    script = os.path.join(ROOT, "dev", "version.sh")
    if not os.access(script, os.X_OK):
        warn("skipping version-drift check (dev/version.sh missing or not executable)")
        return
    sys.stdout.flush()
    if subprocess.run([script, "verify"]).returncode != 0:
        err("manifest versions drifted from VER (run ./dev/version.sh sync)")


def no_constant(name):
    raise ValueError(f"{name} is not JSON")


def check_json():
    """Every JSON file git sees parses: tracked ones, and untracked ones that
    are not ignored, so a new spec is checked before it is added. A tracked
    file deleted in the working tree is skipped."""
    r = subprocess.run(["git", "-C", ROOT, "ls-files", "-co", "--exclude-standard", "*.json"],
                       capture_output=True, text=True)
    for f in r.stdout.splitlines():
        p = os.path.join(ROOT, f)
        if not os.path.isfile(p):
            continue
        try:
            with open(p, encoding="utf-8") as fh:
                json.loads(fh.read(), parse_constant=no_constant)
        except ValueError:
            err(f"{f}: not valid JSON")


def run_tool(script):
    """Run a sibling checker on the repo and return its output lines."""
    sys.stdout.flush()
    r = subprocess.run([sys.executable, "-B", os.path.join(HERE, script)], capture_output=True, text=True)
    return r.stdout.splitlines()


def check_cases():
    """The native eval cases (lint-cases.py); its last line carries its
    counts."""
    out = run_tool("lint-cases.py")
    for line in out[:-1]:
        print(line)
    m = re.fullmatch(r"cases: (\d+) error\(s\), (\d+) warning\(s\)", out[-1] if out else "")
    count["errors"] += int(m.group(1)) if m else 1
    count["warnings"] += int(m.group(2)) if m else 0


def check_evals():
    """The free eval checks (eval-check.py): contracts, probe files,
    generators, grader literals, and triggers."""
    out = run_tool("eval-check.py")
    for line in out:
        if line.startswith("ERR"):
            print(re.sub(r"^ERR *", "ERROR  ", line))
    m = re.search(r" (\d+) error\(s\)$", out[-1] if out else "")
    count["errors"] += int(m.group(1)) if m else 1


def main():
    os.environ["SKILL_EVAL_ROOT"] = ROOT
    paths = []
    for d in skill_dirs():
        paths.append(rel(d))
        lint_skill(d)
    check_marketplace(paths)
    check_versions()
    check_json()
    check_cases()
    check_evals()
    print("----")
    print(f"{count['errors']} error(s), {count['warnings']} warning(s).")
    return 1 if count["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
