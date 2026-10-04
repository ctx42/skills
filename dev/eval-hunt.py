#!/usr/bin/env python3
"""Ambiguity hunt: find where a changed skill reads two ways, and measure it.

A hunter model reads the skill (and, by default, only proposes situations
touching the lines a diff added) and returns up to four situations where a
careful agent could defensibly act in two ways, each with verbatim quotes.
Quotes are checked mechanically against the text — an item whose quote is not
there, or (diff mode) touches no added line, is dropped unasked. Each
surviving situation is then asked three times on haiku, all of a skill's
situations batched into one call per trial. Only a SPLIT (the three answers
disagree) is reported: a disagreement measured on identical input, which the
eval loop accepts as an edit trigger. Agreement is dropped, not backlogged.
A split on lines that a hunt-driven fix added goes to tmp/eval-backlog.md
instead of another edit (CONTRIBUTING, *The eval loop*).

Everything is cached by input under tmp/probe-cache/; a re-run of an
unchanged skill and diff costs nothing. Splits are written as draft probes to
tmp/eval-hunt/<group>-<skill>.json (set `pass` once the fix decides the answer).

Usage:
  ./dev/eval-hunt.py                    skills whose SKILL.md or references
                                        changed against HEAD (working tree)
  ./dev/eval-hunt.py --base REF         ... changed since REF
  ./dev/eval-hunt.py --skill go/cover   one skill (repeatable)
  --full        hunt the whole SKILL.md, not only the diff
  --hunter M    hunter model (default sonnet)
  --at REF      with --full: hunt the text at git REF (for measuring)
  --model M     measuring model (default haiku); -j N; --no-cache
Exit status is non-zero when any split is found.
"""
import argparse
import concurrent.futures as cf
import importlib.util
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SPEC = importlib.util.spec_from_file_location("eval_probe", os.path.join(ROOT, "dev", "eval-probe.py"))
ep = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ep)
OUT = os.path.join(ROOT, "tmp", "eval-hunt")

HUNT = """You audit an AI-agent skill for places where a careful agent following \
it could defensibly act in two different ways. Look for: two passages that \
conflict; a case the text leaves unspecified at a decision the skill must make; \
a term used in two senses; a cap or count that cannot hold together with \
another rule. Ignore style and wording quality. {scope}Return at most 4, the \
most consequential first, as a JSON array only, no prose:
[{{"quote_a": "<verbatim substring of the skill, 6-25 words>",
  "quote_b": "<second verbatim substring, or same as quote_a>",
  "situation": "<concrete situation the agent is in, 1-3 sentences>",
  "question": "<what the agent does now>",
  "options": ["<A>", "<B>"]}}]
Quotes must be copied exactly from the skill. Options must be mutually \
exclusive actions, each defensible from the text. Return [] if there is none."""

SCOPE = """Only report situations where at least one quote comes from the \
ADDED lines of the diff that follows the skill; the rest of the skill is \
context. """


def norm(t):
    return re.sub(r"[\s`*_>#-]+", " ", t).strip().lower()


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout


def changed_skills(base):
    names = git("diff", "--name-only", base, "--") + git("ls-files", "-o", "--exclude-standard")
    out = []
    for f in names.splitlines():
        m = re.match(r"^(go|srd|craft)/skills/([^/]+)/(SKILL\.md|references/.+\.md)$", f)
        if m and f"{m.group(1)}/{m.group(2)}" not in out:
            out.append(f"{m.group(1)}/{m.group(2)}")
    return out


def skill_text(skill, base=None, at=None):
    """SKILL.md, plus (diff mode) each reference the diff touched: the hunter
    reads what changed and the always-loaded text around it, nothing more."""
    g, s = skill.split("/")
    sdir = os.path.join(ROOT, g, "skills", s)
    parts, files = [], ["SKILL.md"]
    if base:
        rel = os.path.relpath(sdir, ROOT)
        touched = git("diff", "--name-only", base, "--", f"{rel}/references") + \
            git("ls-files", "-o", "--exclude-standard", "--", f"{rel}/references")
        files += sorted({os.path.relpath(os.path.join(ROOT, f), sdir)
                         for f in touched.split() if f.endswith(".md")})
    for f in files:
        parts.append(f"=== {f} ===\n{ep.read(os.path.join(sdir, f), at)}")
    return sdir, files, "\n\n".join(parts)


def added_lines(sdir, files, base):
    rel = [os.path.relpath(os.path.join(sdir, f), ROOT) for f in files]
    diff = git("diff", "-U3", base, "--", *rel)
    added = [l[1:] for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
    for f in rel:  # untracked files: every line is added
        if git("ls-files", "--", f) == "" and os.path.isfile(os.path.join(ROOT, f)):
            with open(os.path.join(ROOT, f)) as fh:
                added += fh.read().splitlines()
                diff += f"\n+++ new file {f}\n"
    return diff, norm("\n".join(added))


def hunt(skill, a, spend):
    sdir, files, text = skill_text(skill, None if a.full else a.base, a.at)
    diff = added = None
    if not a.full:
        diff, added = added_lines(sdir, files, a.base)
        # An item survives only if a quote shares 6 words with an added line,
        # so a diff with no added line that long cannot yield one: skip the
        # hunter call.
        if not any(len(norm(l).split()) >= 6 for l in diff.splitlines()
                   if l.startswith("+") and not l.startswith("+++")):
            return skill, [], "no added line of 6+ words; skipped"
    system = HUNT.format(scope="" if a.full else SCOPE)
    user = text if a.full else f"{text}\n\n=== DIFF ===\n{diff}"
    d = ep.call(a.hunter, system, user, 0, not a.no_cache, think=True)
    spend.add(d)
    if "error" in d:
        return skill, [], d["error"]
    hwall = f"hunter {d.get('wall', 0):.0f}s{' cached' if d.get('cached') else ''}"
    m = re.search(r"\[.*\]", d["answer"], re.S)
    try:
        items = json.loads(m.group(0)) if m else []
    except ValueError:
        return skill, [], "hunter returned no JSON"
    nt, kept, dropped = norm(text), [], 0
    for it in items:
        qs = [norm(it.get("quote_a", "")), norm(it.get("quote_b", ""))]
        ok = all(q and q in nt for q in qs) and len(it.get("options", [])) >= 2
        if ok and added is not None:
            # A quote "from the diff" must overlap an added line by >= 6 words.
            ok = any(any(" ".join(q.split()[i:i + 6]) in added
                         for i in range(max(1, len(q.split()) - 5))) for q in qs)
        if ok:
            kept.append(it)
        else:
            dropped += 1
    if not kept:
        return skill, [], f"{len(items)} proposed, {dropped} dropped; {hwall}"
    letters = "ABCD"
    probes = []
    for it in kept:
        opts = it["options"][:4]
        probes.append({"prompt": f"Situation: {it['situation']}\n\nQuestion: {it['question']} "
                       "Answer on the first line with exactly one letter: " +
                       "; ".join(f"{l}) {o}" for l, o in zip(letters, opts)) +
                       ". Then one sentence why.", "pass": "."})
    sysp = ep.system_prompt(sdir, ["SKILL.md"], a.at)[0]
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        trials = list(ex.map(lambda t: ep.run_set([(sysp, p) for p in probes], a.model,
                                                  not a.no_cache, a.j, spend, think=True,
                                                  trial=t), range(3)))
    found = []
    for k, it in enumerate(kept):
        ans = []
        for t in trials:
            x = t[k]
            mm = re.match(r"\W*([A-D])\b", x) if isinstance(x, str) else None
            ans.append(mm.group(1) if mm else "?")
        if len(set(ans)) > 1 and "?" not in ans:
            found.append({**it, "answers": "".join(ans), "probe": probes[k]["prompt"]})
    return skill, found, f"{len(items)} proposed, {dropped} dropped, {len(kept)} measured; {hwall}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skill", action="append", default=[])
    ap.add_argument("--base", default="HEAD")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--hunter", default="sonnet")
    ap.add_argument("--model", default="haiku")
    ap.add_argument("-j", type=int, default=8)
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--at")

    a = ap.parse_args()
    skills = a.skill or changed_skills(a.base)
    if not skills:
        print("eval-hunt: no changed skill text")
        return 0
    spend, t0, n = ep.Spend(), time.time(), 0
    os.makedirs(OUT, exist_ok=True)
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for skill, found, note in ex.map(lambda s: hunt(s, a, spend), skills):
            print(f"== {skill}: {len(found)} split(s) ({note})")
            for it in found:
                n += 1
                print(f"   SPLIT {it['answers']}  {it['question']}")
                for l, o in zip("ABCD", it["options"]):
                    print(f"      {l}) {o}")
                print(f"      quotes: \"{it['quote_a']}\" / \"{it['quote_b']}\"")
            path = os.path.join(OUT, skill.replace("/", "-") + ".json")
            if found:
                with open(path, "w") as f:
                    json.dump([{"id": "", "rule": "", "prompt": it["probe"], "pass": "",
                                "answers": it["answers"]} for it in found], f, indent=2)
            elif os.path.exists(path):
                os.unlink(path)
    print(f"eval-hunt: {len(skills)} skill(s), {n} split(s); {spend.calls} model call(s), "
          f"${spend.cost:.2f}, {time.time() - t0:.0f}s (hunter {a.hunter}, {a.model})")
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
