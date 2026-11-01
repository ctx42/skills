#!/usr/bin/env python3
"""Pass ledger for the agent-run cases (used by eval-changed.sh).

A case's key is a sha256 over what its run depends on, as far as its tags
say: the case dir; for each skill its tags name (skill:, sec:, ref:), the
SKILL.md text above the first `## ` heading, the `## ` sections its sec: tags
name, the references/ files its ref: tags name, and every other file of the
skill outside SKILL.md, references/, and evals/ (LESSONS.md, assets/, ...);
every file those hashed parts link as `../<skill>/<path>`, one level deep;
the group's shared mocks/ and fixtures/; for a needs-shell case, the shell
runner (eval-shell.mjs, eval-notice.mjs); and the model. A PASS is recorded
under that key in tmp/eval-ledger.json; while the key is unchanged, the case
need not run again.

  eval-ledger.py pending <group> <model> <case>...   print cases without a
                                                     PASS at their current key
  eval-ledger.py record <group> <model> <result.json>
        record each case whose runs all passed; print `FAIL <case>` per
        case with a run that did not pass, `MODEL <case>
        <id>` per run on another model than <model> (neither recorded nor
        cleared), and `LIMIT <n>` when n runs hit the usage limit
  eval-ledger.py twice <group> <model> <case>... [--changed <case>...]
        print the cases that run twice (and pass only when both runs pass):
        those whose case dir changed since their last verdict on <model>,
        and those named after --changed (new or changed in git) that have
        no verdict on <model> yet
  eval-ledger.py estimate <group> <model> <case>...
        print the dollar estimate for running the cases on <model>: each
        case's last stored cost there, else the Opus band (fan-out cases
        their own band)
  eval-ledger.py flaky <group> <model> <case>...
        print `<case> <failed> <runs>` for each case whose last runs at its
        current key on <model> (up to ten) both passed and failed
  eval-ledger.py model <word> [--cached]
        print the model ID that `--model <word>` resolves to (`default`: the
        CLI's default model) from one short `claude -p` probe, and cache it in
        tmp/eval-model.json; with --cached, print the cached ID or nothing.
        Exit 3 when the usage limit cut the probe off.

<model> is a resolved model ID, so a pass is a pass on that model. Each
entry is `<group>/<case>@<model>`: {"key": <key of the last pass, or null
once a later run did not pass>, "costUsd": <cost of one run, the last time>,
"caseKey": <hash of the case dir at the last verdict>, "runs": [<true per
passed run, false per failed one, the last ten at "runsKey">], "runsKey":
<the key those runs were recorded at>}.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True  # importing evalroot must not leave __pycache__ in the skill
from evalroot import ROOT  # noqa: E402
LEDGER = os.path.join(ROOT, "tmp", "eval-ledger.json")
MODELS = os.path.join(ROOT, "tmp", "eval-model.json")


def main_model(usage):
    """Return the model ID that cost the most in a result event's modelUsage
    (the session's model, not a helper model), or None when there is none."""
    best, cost = None, -1.0
    for mid, u in (usage or {}).items():
        c = (u or {}).get("costUSD") or 0
        if c > cost:
            best, cost = mid, c
    return best


def run_model(run):
    """Return the model ID one run reports: its result's `model`, else the
    main model of the last result event in its trace, else None."""
    if run.get("model"):
        return run["model"]
    found = None
    try:
        with open(run.get("tracePath") or "") as f:
            for line in f:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if isinstance(e, dict) and e.get("type") == "result":
                    found = main_model(e.get("modelUsage")) or found
    except OSError:
        pass
    return found


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=1, sort_keys=True)


def resolve(word, cached):
    """Return (exit code, model ID) for `--model <word>`; see the docstring."""
    cache = load_json(MODELS)
    if cached:
        return 0, cache.get(word, "")
    cmd = ["claude", "-p", "Reply with the single word OK.", "--output-format", "json",
           "--max-turns", "1", "--tools", "", "--setting-sources", "project",
           "--no-session-persistence"]
    if word != "default":
        cmd += ["--model", word]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    try:
        j = json.loads(r.stdout)
    except ValueError:
        print(f"eval-ledger: model probe failed: {(r.stderr or r.stdout).strip()[-300:]}", file=sys.stderr)
        return 1, ""
    if j.get("is_error"):
        msg = str(j.get("result"))
        print(f"eval-ledger: model probe failed: {msg[-300:]}", file=sys.stderr)
        return (3 if "limit" in msg.lower() else 1), ""
    mid = main_model(j.get("modelUsage"))
    if not mid:
        print("eval-ledger: model probe reported no model", file=sys.stderr)
        return 1, ""
    cache[word] = mid
    save_json(MODELS, cache)
    return 0, mid


# A history_file run leaves its session (`<uuid>.jsonl`) beside the history
# until eval-changed.sh ends; it is never an input, so no key hashes it.
SESSION = re.compile(r"[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}\.jsonl")


def files_under(top, skip=()):
    """Return the files under top in a stable order, leaving out the dirs
    named in skip and stray session files."""
    out = []
    for dp, dns, fs in os.walk(top):
        dns[:] = sorted(d for d in dns if d not in skip)
        out += [os.path.join(dp, f) for f in sorted(fs) if not SESSION.fullmatch(f)]
    return out


HERE = os.path.dirname(os.path.abspath(__file__))
HISTORY = 10  # runs kept per entry for the flaky count
SHELL_RUNNER = ("eval-shell.mjs", "eval-notice.mjs", "eval-guard.mjs")
LINK = re.compile(r"\.\./(?:\.\./)?([a-z0-9-]+)/([A-Za-z0-9_./-]*[A-Za-z0-9_])")


def slug(heading):
    """Slug a `## ` heading as eval-changed.sh does for sec: tags."""
    return re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")


def split_sections(text):
    """Return (preamble, {slug: section text}) for a SKILL.md body."""
    pre, sections, cur = [], {}, None
    for line in text.splitlines(keepends=True):
        if line.startswith("## "):
            cur = slug(line[3:].strip())
            sections[cur] = line
        elif cur is None:
            pre.append(line)
        else:
            sections[cur] += line
    return "".join(pre), sections


def case_tags(group, case):
    with open(os.path.join(ROOT, group, "evals", case, "prompt.md")) as f:
        m = re.search(r"^tags:\s*\[([^\]]*)\]", f.read(), re.M)
    return [t.strip() for t in m.group(1).split(",")] if m else []


def read(path):
    with open(path, "rb") as f:
        return f.read()


def key(group, case, model):
    skills = {}  # skill -> (sections, refs)
    tags = case_tags(group, case)
    for t in tags:
        mm = re.match(r"^(skill|sec|ref):([a-z0-9-]+)(?:[:/](.+))?$", t)
        if not mm:
            continue
        kind, s, rest = mm.groups()
        secs, refs = skills.setdefault(s, (set(), set()))
        if kind == "sec" and rest:
            secs.add(rest)
        elif kind == "ref" and rest:
            refs.add(rest)
    parts = []  # (label, bytes)
    cdir = os.path.join(ROOT, group, "evals", case)
    parts += [(os.path.relpath(p, ROOT), read(p)) for p in files_under(cdir)]
    for s in sorted(skills):
        secs, refs = skills[s]
        sdir = os.path.join(ROOT, group, "skills", s)
        texts = []
        md = os.path.join(sdir, "SKILL.md")
        pre, sections = split_sections(read(md).decode() if os.path.isfile(md) else "")
        texts.append((f"{group}/skills/{s}/SKILL.md#", pre))
        texts += [(f"{group}/skills/{s}/SKILL.md#{x}", sections.get(x, "")) for x in sorted(secs)]
        for r in sorted(refs):
            rp = os.path.join(sdir, "references", f"{r}.md")
            texts.append((os.path.relpath(rp, ROOT), read(rp).decode() if os.path.isfile(rp) else ""))
        parts += [(label, t.encode()) for label, t in texts]
        for p in files_under(sdir, skip=("evals", "references")):
            if p != md:
                parts.append((os.path.relpath(p, ROOT), read(p)))
        # Files the hashed text links in sibling skills, one level deep.
        linked = set()
        for _, t in texts:
            for name, rel in LINK.findall(t):
                lp = os.path.join(ROOT, group, "skills", name, rel)
                if os.path.isfile(lp):
                    linked.add(lp)
        parts += [(os.path.relpath(p, ROOT), read(p)) for p in sorted(linked)]
    for sub in ("mocks", "fixtures"):
        parts += [(os.path.relpath(p, ROOT), read(p)) for p in files_under(os.path.join(ROOT, group, "evals", sub))]
    if "needs-shell" in tags:
        parts += [(f"runner/{n}", read(os.path.join(HERE, n))) for n in SHELL_RUNNER]
    h = hashlib.sha256(f"model={model}\n".encode())
    for label, data in parts:
        h.update(label.encode() + b"\0")
        h.update(data)
    return h.hexdigest()


def case_key(group, case):
    """Return a sha256 over the case dir alone."""
    cdir = os.path.join(ROOT, group, "evals", case)
    h = hashlib.sha256()
    for p in files_under(cdir):
        h.update(os.path.relpath(p, ROOT).encode() + b"\0")
        h.update(read(p))
    return h.hexdigest()


# Per-case cost bands, measured on Opus on 2026-10-04: (low, high).
BAND = (0.25, 0.80)
FANOUT_BAND = (3.0, 9.0)


def slot(group, case, model):
    return f"{group}/{case}@{model}"


def is_fanout(group, case):
    return "fan-out" in case_tags(group, case)


def estimate(led, group, model, cases):
    """Return the estimate line for running cases on model (see the docstring)."""
    lo = hi = 0.0
    measured = 0
    for c in cases:
        e = led.get(slot(group, c, model))
        if isinstance(e, dict) and isinstance(e.get("costUsd"), (int, float)):
            lo += e["costUsd"]
            hi += e["costUsd"]
            measured += 1
        else:
            b = FANOUT_BAND if is_fanout(group, c) else BAND
            lo += b[0]
            hi += b[1]
    rng = f"~${lo:.2f}" if lo == hi else f"~${lo:.2f}-{hi:.2f}"
    if not cases:
        return rng
    if measured == len(cases):
        return f"{rng} (measured on {model})"
    if measured:
        return f"{rng} ({measured} of {len(cases)} measured on {model}, the rest by the Opus band of 2026-10-04)"
    return f"{rng} (Opus, measured 2026-10-04)"


def main():
    if sys.argv[1] == "model":
        code, mid = resolve(sys.argv[2], "--cached" in sys.argv[3:])
        if mid:
            print(mid)
        return code
    cmd, group, model = sys.argv[1], sys.argv[2], sys.argv[3] or "default"
    led = load_json(LEDGER)
    if cmd == "pending":
        for c in sys.argv[4:]:
            e = led.get(slot(group, c, model))
            if not isinstance(e, dict) or e.get("key") != key(group, c, model):
                print(c)
        return 0
    if cmd == "twice":
        args = sys.argv[4:]
        cut = args.index("--changed") if "--changed" in args else len(args)
        changed = set(args[cut + 1:])
        for c in args[:cut]:
            e = led.get(slot(group, c, model))
            if isinstance(e, dict) and e.get("caseKey"):
                if e["caseKey"] != case_key(group, c):
                    print(c)
            elif c in changed:
                print(c)
        return 0
    if cmd == "estimate":
        print(estimate(led, group, model, sys.argv[4:]))
        return 0
    if cmd == "flaky":
        for c in sys.argv[4:]:
            e = led.get(slot(group, c, model))
            if not isinstance(e, dict) or e.get("runsKey") != key(group, c, model):
                continue
            runs = e.get("runs") or []
            if any(runs) and not all(runs):
                print(c, runs.count(False), len(runs))
        return 0
    with open(sys.argv[4]) as f:
        d = json.load(f)
    limit = 0
    for c in d.get("cases", []):
        name, runs = c["name"], c["arms"]["with"]
        limits = sum("limit" in (r.get("error") or "").lower() for r in runs)
        if limits:
            # A run cut off by the usage limit says nothing about the skill.
            limit += limits
            continue
        other = next((m for m in map(run_model, runs) if m and m != model), None)
        if other:
            # A verdict on another model says nothing about this key.
            print(f"MODEL {name} {other}")
            continue
        k = key(group, name, model)
        prev = led.get(slot(group, name, model))
        hist = prev.get("runs") or [] if isinstance(prev, dict) and prev.get("runsKey") == k else []
        hist = (hist + [bool(r.get("passed") and not r.get("error")) for r in runs])[-HISTORY:]
        entry = {"key": None, "costUsd": sum(r.get("costUsd") or 0 for r in runs) / len(runs),
                 "caseKey": case_key(group, name), "runs": hist, "runsKey": k}
        if all(r.get("passed") and not r.get("error") for r in runs):
            entry["key"] = k
        else:
            # A finished run that did not pass is a verdict on this key: the
            # null key makes the next run take the case again.
            print(f"FAIL {name}")
        led[slot(group, name, model)] = entry
    save_json(LEDGER, led)
    if limit:
        print(f"LIMIT {limit}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
