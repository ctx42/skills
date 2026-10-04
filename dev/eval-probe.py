#!/usr/bin/env python3
"""Decision probes: one cheap question per high-stakes rule, cached.

A probe loads a skill's SKILL.md (plus any listed references) as the system
prompt, gives a prepared situation and one question, and grades the short
answer by regex. No tools, one turn, a small model. All probes that share a
system prompt (a skill and its context files) are asked in ONE call, each
answer under its own `### Q<n>` header: the skill text is paid for once per
skill, not once per probe. An answer whose inputs have not changed is replayed
from tmp/probe-cache/ for free. Grading always re-runs, so a fixed
`pass`/`fail` regex never needs a paid re-run.

Probe file: <group>/skills/<skill>/evals/probes.json
  {"skill_name": "kb", "probes": [{
     "id": "inference-stays-out",       unique within the skill
     "rule": "attested-only",           a contract.json rule id (optional)
     "context": ["SKILL.md", "references/x.md"],   default ["SKILL.md"]
     "prompt": "Situation: ... Question: ... Answer in one line ...",
     "pass": "regex the answer must match",
     "fail": "regex the answer must not match (optional)",
     "class": "load-bearing"}]}        set by --baseline --write
Regexes are Python, case-insensitive, dot matches newline.

Usage:
  ./dev/eval-probe.py                  every probe (unchanged ones are free)
  ./dev/eval-probe.py --skill srd/kb   one skill (repeatable)
  ./dev/eval-probe.py --probe srd/kb:inference-stays-out
  --model M     default haiku; sonnet for a probe haiku cannot judge
  -j N          concurrent calls (default 8)
  --single      one call per probe (the pre-batching path)
  --think       think on the first pass too (it runs without thinking: a
                failure there is always re-asked with thinking, and in every
                measured run thinking-off failed a superset of what thinking-on
                failed, at half the cost and a third of the time)
  --against REF ask against the skill text at git REF (red/green: a probe
                for a fix must FAIL at the pre-fix ref and PASS now)
  --baseline    also ask every probe with no skill text (bare) and with its
                contract rule's `must` sentences deleted (mutated), and class
                it: prior (passes bare), redundant (passes mutated),
                load-bearing (fails both), unmutated (no rule to delete)
  --write       with --baseline: store each class in probes.json
  --strict      confirm every probe with three thinking trials, not only
                first-pass misses (measures flakiness; ~3x the cost)
  --compare M1,M2,...  release calibration: one batched pass per model
                (thinking on), listing the probes the models disagree on
  --no-cache    ignore cached answers (still writes them)
  --show        print every answer, not only failures

A probe that fails in its batch is re-asked alone three times (cached
separately) and reported as FAIL (0/3) or SPLIT (1/3, 2/3) — a split is a
measured ambiguity in the skill text. Exit status is non-zero on any FAIL or
SPLIT.
"""
import argparse
import concurrent.futures as cf
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CACHE = os.path.join(ROOT, "tmp", "probe-cache")
GROUPS = ("go", "srd", "craft")
MAX_BATCH = 8

FRAME = """You are an AI coding agent with the skill below loaded: its SKILL.md \
and the reference files it uses follow. A user is in a session with you. Answer \
the user's question exactly as this skill directs you to act. You have no tools \
in this conversation: answer from the skill text alone, in the form the question \
asks for, briefly. Do not hedge between options; commit to what the skill says \
you do."""

BARE = """You are an AI coding agent. A user is in a session with you. Answer \
the user's question as you would act. You have no tools in this conversation: \
answer in the form the question asks for, briefly. Do not hedge between \
options; commit to one."""

BATCH = """Several independent questions follow. Treat each as its own fresh \
situation; nothing from one carries over to another. Answer each under its \
own header line `### Q<n>`, in exactly the form that question asks for."""


def discover(skills, probes):
    out = []
    for g in GROUPS:
        for path in sorted(glob.glob(os.path.join(ROOT, g, "skills", "*", "evals",
                                                  "probes.json"))):
            sdir = os.path.dirname(os.path.dirname(path))
            key = f"{g}/{os.path.basename(sdir)}"
            if skills and key not in skills:
                continue
            with open(path) as f:
                data = json.load(f)
            for p in data.get("probes", []):
                pk = f"{key}:{p['id']}"
                if probes and pk not in probes:
                    continue
                out.append((pk, sdir, p))
    return out


def read(path, ref):
    if not ref:
        with open(path) as f:
            return f.read()
    r = subprocess.run(["git", "show", f"{ref}:{os.path.relpath(path, ROOT)}"],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        raise FileNotFoundError(f"{os.path.relpath(path, ROOT)} not at {ref}")
    return r.stdout


def norm(text):
    return re.sub(r"\s+", " ", text)


def mutate(text, patterns):
    """Delete every sentence a contract `must` pattern matches."""
    t, n = norm(text), 0
    for p in patterns:
        while n < 40:
            m = re.search(p, t, re.I | re.S)
            if not m:
                break
            a = max(t.rfind(". ", 0, m.start()), t.rfind(" - ", 0, m.start()),
                    t.rfind("# ", 0, m.start()))
            a = 0 if a < 0 else a + 2
            b = t.find(". ", m.end())
            b = len(t) if b < 0 else b + 1
            t, n = t[:a] + t[b:], n + 1
    return t, n


def system_prompt(sdir, context, ref=None, rule=None):
    """The skill's system prompt; with `rule`, that rule's sentences deleted.
    Returns (text, sentences removed)."""
    parts, removed = [FRAME], 0
    for cf_ in context:
        path = os.path.normpath(os.path.join(sdir, cf_))
        text = read(path, ref)
        if rule and os.path.normpath(os.path.join(sdir, rule.get("file", "SKILL.md"))) == path:
            text, removed = mutate(text, rule.get("must", []))
        parts.append(f"=== {os.path.relpath(path, os.path.dirname(sdir))} ===\n" + text)
    return "\n\n".join(parts), removed


def call(model, system, prompt, trial, use_cache, think=True):
    key = hashlib.sha256("\0".join([model, system, prompt, str(trial)] +
                                    ([] if think else ["think=0"]))
                         .encode()).hexdigest()
    path = os.path.join(CACHE, key + ".json")
    if use_cache and os.path.isfile(path):
        with open(path) as f:
            d = json.load(f)
        d["cached"] = True
        return d
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as sf:
        sf.write(system)
    # The CLI caches the prompt only up to the end of the user turn, so a
    # different question never reads the skill back: the 1h cache write is
    # pure cost. Turning caching off bills the skill at the plain input rate.
    env = dict(os.environ, DISABLE_PROMPT_CACHING="1")
    env.pop("MAX_THINKING_TOKENS", None)
    if not think:
        env["MAX_THINKING_TOKENS"] = "0"
    try:
        t0 = time.time()
        r = subprocess.run(
            ["claude", "-p", "--model", model, "--tools", "", "--setting-sources", "",
             "--strict-mcp-config", "--disable-slash-commands",
             "--no-session-persistence", "--output-format", "json",
             "--system-prompt-file", sf.name],
            input=prompt, capture_output=True, text=True, timeout=300, env=env)
        wall = time.time() - t0
    except subprocess.TimeoutExpired:
        return {"error": "timed out after 300s", "cost": 0, "wall": 300}
    finally:
        os.unlink(sf.name)
    try:
        j = json.loads(r.stdout)
    except ValueError:
        return {"error": (r.stderr or r.stdout).strip()[-300:], "cost": 0, "wall": 0}
    if j.get("is_error"):
        return {"error": str(j.get("result"))[-300:], "cost": 0, "wall": wall}
    d = {"answer": j.get("result", ""), "cost": j.get("total_cost_usd", 0),
         "wall": wall}
    os.makedirs(CACHE, exist_ok=True)
    with open(path, "w") as f:
        json.dump(d, f)
    d["cached"] = False
    return d


def grade(p, answer):
    flags = re.I | re.S
    if not re.search(p["pass"], answer, flags):
        return False
    if p.get("fail") and re.search(p["fail"], answer, flags):
        return False
    return True


def split_answers(text):
    parts = re.split(r"^[#*\s]*Q(\d+)\b[*:.\s]*$", text, flags=re.M)
    return {int(parts[i]): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}


class Spend:
    def __init__(self):
        self.cost, self.calls, self.lock = 0.0, 0, threading.Lock()

    def add(self, d):
        if d.get("cached") is False:
            with self.lock:
                self.cost += d.get("cost", 0)
                self.calls += 1


def ask_batch(model, system, prompts, use_cache, spend, think, trial=0):
    """One call for every prompt sharing `system`; returns answers or None."""
    if len(prompts) == 1:
        d = call(model, system, prompts[0], trial, use_cache, think)
        spend.add(d)
        return [d.get("answer")] if "error" not in d else d
    q = BATCH + "\n\n" + "\n\n".join(f"### Q{i + 1}\n{p}" for i, p in enumerate(prompts))
    d = call(model, system, q, trial, use_cache, think)
    spend.add(d)
    if "error" in d:
        return d
    a = split_answers(d["answer"])
    return [a.get(i + 1, "") for i in range(len(prompts))]


def run_set(jobs, model, use_cache, nj, spend, batch=MAX_BATCH, think=False,
            trial=0):
    """jobs: list of (system, probe) -> list of (answer | error dict)."""
    groups = {}
    for i, (system, p) in enumerate(jobs):
        groups.setdefault(system, []).append(i)
    # Chunks of MAX_BATCH keep each answer short enough to stay focused and
    # parse cleanly (the bare baseline shares one system prompt across all).
    chunks = [(s, ix[k:k + batch]) for s, ix in groups.items()
              for k in range(0, len(ix), batch)]
    out = [None] * len(jobs)
    with cf.ThreadPoolExecutor(max_workers=max(1, nj)) as ex:
        futs = {ex.submit(ask_batch, model, s, [jobs[i][1]["prompt"] for i in ix],
                          use_cache, spend, think, trial): ix for s, ix in chunks}
        for fut in cf.as_completed(futs):
            res = fut.result()
            for k, i in enumerate(futs[fut]):
                out[i] = res if isinstance(res, dict) else res[k]
    return out


def confirm(model, system, p, use_cache, spend):
    """Re-ask a probe alone three times: FAIL (0/3), SPLIT, or PASS (3/3)."""
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        results = list(ex.map(lambda t: call(model, system, p["prompt"], t, use_cache),
                              range(3)))
    for d in results:
        spend.add(d)
        if "error" in d:
            return "ERROR", [d]
        d["ok"] = grade(p, d["answer"])
    ok = sum(r["ok"] for r in results)
    return ("PASS" if ok == 3 else "FAIL" if ok == 0 else "SPLIT"), results


def contract_rule(sdir, rid):
    path = os.path.join(sdir, "evals", "contract.json")
    if not rid or not os.path.isfile(path):
        return None
    with open(path) as f:
        return next((r for r in json.load(f).get("rules", []) if r.get("id") == rid), None)


def baseline(items, a, use_cache, spend):
    """Class each probe. Bare answers are close to coin flips, so a probe is
    `prior` only when it passes bare in all 3 trials (a yes/no coin flip
    does so 1 time in 8); thinking is on
    throughout, as in a confirmation."""
    size = 1 if a.single else MAX_BATCH
    bare_jobs = [(BARE, p) for _, _, p in items]
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        trials = list(ex.map(lambda t: run_set(bare_jobs, a.model, use_cache, a.j, spend,
                                               size, True, t), range(3)))
    bare = []
    for k, (_, _, p) in enumerate(items):
        ans = [t[k] for t in trials]
        err = next((x for x in ans if isinstance(x, dict)), None)
        bare.append(err or all(grade(p, x) for x in ans))
    mjobs, removed = [], []
    for (_, sdir, p), b in zip(items, bare):
        # A prior probe is classed already: skip its (costlier) mutated run.
        rule = None if b is True else contract_rule(sdir, p.get("rule"))
        s, n = system_prompt(sdir, p.get("context", ["SKILL.md"]), a.against, rule)
        mjobs.append((s, p))
        removed.append(n if rule else 0)
    mut = run_set([j for j, n in zip(mjobs, removed) if n],
                  a.model, use_cache, a.j, spend, size, True)
    mut_it = iter(mut)
    classes, detail = {}, {}
    for (pk, _, p), b, n in zip(items, bare, removed):
        m = next(mut_it) if n else None
        b_ok = b is True
        m_ok = isinstance(m, str) and grade(p, m)
        detail[pk] = {"bare": b_ok, "mutated": m_ok if n else None}
        if isinstance(b, dict) or isinstance(m, dict):
            classes[pk] = "error"
        elif b_ok:
            classes[pk] = "prior"
        elif not n:
            classes[pk] = "unmutated"
        elif m_ok:
            classes[pk] = "redundant"
        else:
            classes[pk] = "load-bearing"
    os.makedirs(CACHE, exist_ok=True)
    with open(os.path.join(CACHE, f"baseline{'-single' if a.single else ''}.json"), "w") as f:
        json.dump(detail, f, indent=1)
    return classes


def write_classes(classes):
    by_file = {}
    for pk, c in classes.items():
        if c == "error":
            continue
        skill, pid = pk.split(":", 1)
        g, s = skill.split("/")
        by_file.setdefault(os.path.join(ROOT, g, "skills", s, "evals", "probes.json"),
                           {})[pid] = c
    for path, cs in by_file.items():
        with open(path) as f:
            data = json.load(f)
        for p in data["probes"]:
            if p["id"] in cs:
                p["class"] = cs[p["id"]]
        with open(path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")


def compare(live, systems, a, use_cache, spend, t0):
    """Release calibration: one batched pass per model, thinking on, and the
    probes the models disagree on. Haiku failing where a stronger model passes
    is noise in the probe; the reverse is a probe trusting a weak reader."""
    models = a.compare.split(",")
    jobs = [(systems[pk], p) for pk, _, p in live]
    res = {m: run_set(jobs, m, use_cache, a.j, spend, think=True) for m in models}
    split = 0
    print(f"   {'probe':<52} " + " ".join(f"{m:<7}" for m in models))
    for k, (pk, _, p) in enumerate(live):
        v = [isinstance(res[m][k], str) and grade(p, res[m][k]) for m in models]
        if len(set(v)) > 1:
            split += 1
            print(f"   {pk:<52} " + " ".join(f"{'pass' if x else 'FAIL':<7}" for x in v))
    print(f"eval-probe: {len(live)} probe(s) compared, {split} disagree; "
          f"{spend.calls} model call(s), ${spend.cost:.2f}, {time.time() - t0:.0f}s "
          f"({a.compare})")
    return 1 if split else 0


def show(answer):
    return "      | " + answer.strip().replace("\n", "\n      | ")[:600]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skill", action="append", default=[])
    ap.add_argument("--probe", action="append", default=[])
    ap.add_argument("--model", default="haiku")
    ap.add_argument("-j", type=int, default=8)
    ap.add_argument("--single", action="store_true")
    ap.add_argument("--think", action="store_true")
    ap.add_argument("--against")
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--compare")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    items = discover(set(a.skill), set(a.probe))
    if not items:
        print("eval-probe: no probes selected")
        return 0
    use_cache = not a.no_cache
    t0, spend = time.time(), Spend()
    systems = {}
    for pk, sdir, p in items:
        try:
            systems[pk] = system_prompt(sdir, p.get("context", ["SKILL.md"]), a.against)[0]
        except FileNotFoundError as e:
            systems[pk] = None
            print(f"   ABSENT       {pk}  ({e})")
    live = [it for it in items if systems[it[0]]]
    if a.compare:
        return compare(live, systems, a, use_cache, spend, t0)
    if a.single:
        def one(it):
            d = call(a.model, systems[it[0]], it[2]["prompt"], 0, use_cache, a.think)
            spend.add(d)
            return d if "error" in d else d["answer"]
        with cf.ThreadPoolExecutor(max_workers=max(1, a.j)) as ex:
            first = list(ex.map(one, live))
    else:
        first = run_set([(systems[pk], p) for pk, _, p in live], a.model, use_cache,
                        a.j, spend, think=a.think)
    verdicts = {}

    def settle(idx):
        pk, sdir, p = live[idx]
        ans = first[idx]
        if isinstance(ans, str) and grade(p, ans) and not a.strict:
            return pk, "PASS", [{"answer": ans}], p
        if isinstance(ans, dict):
            return pk, "ERROR", [ans], p
        v, res = confirm(a.model, systems[pk], p, use_cache, spend)
        return pk, v, res, p

    bad = 0
    with cf.ThreadPoolExecutor(max_workers=max(1, a.j)) as ex:
        for pk, verdict, results, p in ex.map(settle, range(len(live))):
            verdicts[pk] = verdict
            ok = sum(r.get("ok", False) for r in results)
            tag = verdict if verdict in ("PASS", "ERROR") or len(results) < 3 \
                else f"{verdict} ({ok}/3)"
            print(f"   {tag:<12} {pk}")
            if verdict != "PASS":
                bad += 1
                if verdict == "ERROR":
                    print(f"      {results[0]['error']}")
                else:
                    print(f"      pass: /{p['pass']}/" +
                          (f"  fail: /{p['fail']}/" if p.get("fail") else ""))
                    for r in results:
                        print(show(r["answer"]))
            elif a.show:
                print(show(results[0]["answer"]))
    extra = ""
    if a.baseline:
        classes = baseline(live, a, use_cache, spend)
        for pk in sorted(classes):
            if classes[pk] != "load-bearing":
                print(f"   {classes[pk]:<12} {pk}")
        counts = {c: list(classes.values()).count(c) for c in
                  ("load-bearing", "redundant", "unmutated", "prior", "error")}
        extra = "; " + " / ".join(f"{n} {c}" for c, n in counts.items() if n)
        if a.write:
            write_classes(classes)
    print(f"eval-probe: {len(items)} probe(s), {len(items) - bad} pass, {bad} not{extra}; "
          f"{spend.calls} model call(s), ${spend.cost:.2f}, {time.time() - t0:.0f}s "
          f"({a.model}{', at ' + a.against if a.against else ''}"
          f"{', single' if a.single else ''})")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
