#!/usr/bin/env python3
"""Generate go/evals/review--* native eval cases. Re-runnable; owns only review--*."""
import json
import os
import shutil
import uuid
import random

# Seeded so a rerun reproduces the committed history files byte for byte.
_rng = random.Random(42)


def _uuid4():
    return uuid.UUID(int=_rng.getrandbits(128), version=4)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
EVALS = os.path.join(ROOT, "go/evals")

ENGLISH = "The user writes English; reply in English.\n"
PERSONA = """Automated eval: the user is absent. Whenever the skill would stop and wait
for the user, take the next scripted answer below as the reply and continue
in this same run; never end the run to wait. If none fits, give the most
plausible answer and continue.
Before taking a scripted answer, write out in full, as your reply text, the
message you would send the user at that point.
"""
WIRING = """Eval wiring: this workspace is the go plugin's git clone, checked out at
./go (the run loads a read-only copy of it). Wherever the skill names
`../style/SKILL.md` or `../style/rules.md`, use ./go/skills/style/SKILL.md and
./go/skills/style/rules.md in this workspace; they are the writable clone.
"""
NOTICE = ("Ignore any trailing notice about a company directive "
          "(«Nutzung von Claude und andere AI-Agents»). ")

CHECK_TAGS = ["skill:review", "sec:review:usage", "sec:review:working-diff-injected",
              "sec:review:check-mode", "ref:style/checking", "sec:style:production"]
RULE_TAGS = ["skill:review", "sec:review:usage", "sec:review:working-diff-injected",
             "sec:review:rule-edit-and-learn-modes", "ref:review/rule-editing"]

GIT_INIT = """git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
"""

# ---------------------------------------------------------------- helpers


def heredocs(files):
    out = []
    for i, (path, body) in enumerate(files.items()):
        d = os.path.dirname(path)
        if d:
            out.append(f"mkdir -p {d}")
        if not body.endswith("\n"):
            body += "\n"
        out.append(f"cat > {path} <<'EOF_{i}'\n{body}EOF_{i}")
    return "\n".join(out) + "\n"


def scaffold(*parts):
    return "#!/usr/bin/env bash\nset -euo pipefail\n" + "".join(parts)


def commit(msg="initial"):
    return f"git add -A\ngit commit -qm '{msg}'\n"


def g_regex(pattern, target="last_message", flags=None, match=None):
    fm = ["type: regex"]
    if isinstance(target, str):
        fm.append(f"target: {target}")
    else:
        fm.append(f"target: {{source: file, path: {target['file']}}}")
    if match:
        fm.append(f'match: "{match}"')
    if flags:
        fm.append(f'flags: "{flags}"')
    return "---\n" + "\n".join(fm) + "\n---\n" + pattern + "\n"


def g_tool(tool, input_match=None, min_=None, max_=None, both=False):
    fm = ["type: tool_used", f"tool: {tool}"]
    if input_match:
        fm.append(f"input_match: '{input_match}'")
    if min_ is not None:
        fm.append(f"min: {min_}")
    if max_ is not None:
        fm.append(f"max: {max_}")
    if both:
        fm.append("arm: both")
    return "---\n" + "\n".join(fm) + "\n---\n"


def g_never(tool, input_match=None):
    return g_tool(tool, input_match, 0, 0, True)


def g_exists(path, exists=True):
    return f"---\ntype: file_exists\npath: \"{path}\"\nexists: {str(exists).lower()}\n---\n"


def g_llm(claim, focus="last_message"):
    return f"---\ntype: llm\nfocus: {focus}\n---\n{NOTICE}{claim}\n"


def write_case(name, tags, prompt, graders, scaffold_sh=None, history=None,
               allowed=None, max_turns=40, timeout=300, asp=None):
    d = os.path.join(EVALS, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "graders"))
    # lint allows over 300 s only on a fan-out- or long-tagged case
    if timeout > 300 and "long" not in tags:
        tags = tags + ["fan-out"]
    fm = [f"tags: [case:{name}, {', '.join(tags)}]", "runs: 1",
          f"max_turns: {max_turns}", f"timeout_seconds: {timeout}",
          f"allowed_tools: [{', '.join(allowed)}]"]
    if asp:
        fm.append("append_system_prompt: |")
        fm += ["  " + ln if ln else "" for ln in asp.rstrip("\n").split("\n")]
    with open(os.path.join(d, "prompt.md"), "w") as f:
        f.write("---\n" + "\n".join(fm) + "\n---\n\n" + prompt + "\n")
    if scaffold_sh or history:
        y = ['schema_version: "1.1"', f"name: {name}", "context:"]
        if scaffold_sh:
            y.append("  scaffold_script: scaffold.sh")
        if history:
            y.append("  history_file: history.jsonl")
        with open(os.path.join(d, "case.yaml"), "w") as f:
            f.write("\n".join(y) + "\n")
    if scaffold_sh:
        p = os.path.join(d, "scaffold.sh")
        with open(p, "w") as f:
            f.write(scaffold_sh)
        os.chmod(p, 0o755)
    if history:
        with open(os.path.join(d, "history.jsonl"), "w") as f:
            f.write(history)
    for gname, body in graders.items():
        with open(os.path.join(d, "graders", gname + ".md"), "w") as f:
            f.write(body)


def line_of(src, needle):
    for i, ln in enumerate(src.split("\n"), 1):
        if needle in ln:
            return i
    raise SystemExit(f"needle not found: {needle}")


class History:
    """A hand-built session transcript for context.history_file (--resume)."""

    def __init__(self):
        self.sid = str(_uuid4())
        self.prev = None
        self.lines = []
        self.n = 0

    def _add(self, typ, msg):
        u = str(_uuid4())
        self.n += 1
        self.lines.append({
            "parentUuid": self.prev, "isSidechain": False, "userType": "external",
            "cwd": "/work/project", "sessionId": self.sid, "version": "2.1.288",
            "type": typ, "message": msg, "uuid": u,
            "timestamp": f"2026-10-01T10:{self.n:02d}:00.000Z"})
        self.prev = u

    def user(self, text):
        self._add("user", {"role": "user", "content": text})

    def _assistant(self, content, stop):
        self._add("assistant", {
            "id": f"msg_{_uuid4().hex[:24]}", "type": "message",
            "role": "assistant", "model": "claude-opus-5-5", "content": content,
            "stop_reason": stop, "stop_sequence": None,
            "usage": {"input_tokens": 10, "output_tokens": 10}})

    def say(self, text):
        self._assistant([{"type": "text", "text": text}], "end_turn")

    def tool(self, text, name, inp, result):
        tid = f"toolu_{_uuid4().hex[:24]}"
        content = ([{"type": "text", "text": text}] if text else [])
        content.append({"type": "tool_use", "id": tid, "name": name, "input": inp})
        self._assistant(content, "tool_use")
        self._add("user", {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": tid, "content": result}]})

    def edit(self, text, path, old, new):
        self.tool(text, "Edit", {"file_path": path, "old_string": old,
                                 "new_string": new, "replace_all": False},
                  f"The file {path} has been updated successfully.")

    def dump(self):
        return "\n".join(json.dumps(x) for x in self.lines) + "\n"


# ------------------------------------------------- style rulebook fixture

STYLE_SKILL = """---
name: style
description: >
  Enforced Go coding style for this project (production and test code).
license: MIT
---

# style

Authoritative Go style rules. Apply the Production section to `*.go` and the
Test section to `*_test.go`; Test inherits Production unless a Test rule
overrides it. Per-rule detection detail lives in [rules.md](rules.md).

Change the rules only through `go:review`; never hand-edit them.

## Production

### Formatting

- gofmt + goimports always; never hand-format or reorder imports manually.
- Separate multi-line switch cases with a blank line; none before the first.

### Naming

- No name stutter: `pkg.Thing`, not `pkg.PkgThing`.
- Receivers are a short type abbreviation, never a single letter: `pag *page`,
  `cfg *config`.

### Functions & methods

- A func whose sole parameter is a local `*T`/`T` belongs on T as a method
  (`pag.f()`, not `f(pag)`).
- No naked returns in non-trivial functions.

### Errors

- Wrap errors with `%w` and add context; never swallow the error.
- Match errors with `errors.Is`/`errors.As`, never `==`.

### API design

- `context.Context` is the first parameter when used; never store it in a
  struct.
- Assert implementations at compile time: `var _ Iface = (*T)(nil)` near the
  top of the file.
- No work in `init()`; no package-level mutable state or singletons.

## Test

### Structure

- Structure every test body with the `--- Given ---`, `--- When ---`, and
  `--- Then ---` comment markers, in order.
- Table-driven subtests via `t.Run`; one case per table row.

### Naming

- Test function names are `Test_Func` and `Test_Type_Method`; add `_tabular`
  for table tests.
- Name the actual value `have` and the expected value `want`, never `got`.

### Helpers & fixtures

- Test helpers call `t.Helper()`.
- Simple test helpers shared within a package live in `all_test.go`.
"""

STYLE_RULES = """# Go style — deep rules

Keyed detection detail for the rules in `SKILL.md` (same directory). An entry
adds only what a capable reviewer can't infer from the one-line rule — an
exemption or a detection heuristic — in two short sentences. Open an entry only
when about to flag its rule; never preload the file. Grows via
`go:review add`.

## Contents

- No name stutter (Production)
- Method over a single-receiver-arg func (Production)
- Assert implementations at compile time (Production)
- Test helpers in all_test.go (Test)

## No name stutter (Production)

Exemption: a name fixed by a contract outside the package, such as a method
another type is asserted against. Detect: a member repeating its type or
package qualifier (`client.ClientDo`) with no same-file pin.

## Method over a single-receiver-arg func (Production)

Exemption: the arg is one of several equals with no clear receiver. Detect: an
unexported func with a single local-type parameter.

## Assert implementations at compile time (Production)

Exemption: an unexported type only ever used through its concrete type. Detect:
a type passed as an interface with no `var _ Iface = (*T)(nil)` in its file.

## Test helpers in all_test.go (Test)

Exemption: a helper used by one test file only may stay beside it. Detect: a
helper declared in a `_test.go` file other than `all_test.go` and called from
two or more test files.
"""

STYLE_FILES = {"go/skills/style/SKILL.md": STYLE_SKILL,
               "go/skills/style/rules.md": STYLE_RULES}
SKILL_P = {"file": "go/skills/style/SKILL.md"}
RULES_P = {"file": "go/skills/style/rules.md"}

# ------------------------------------------- 1 review-the-current-diff

STORE_OLD = """// Package store persists named blobs in a directory.
package store

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
)

// ErrReadOnly is returned by Save when the store does not accept writes.
var ErrReadOnly = errors.New("store is read-only")

// Store reads and writes named blobs under one directory.
type Store struct {
	dir      string
	readOnly bool
}

// New returns a Store rooted at dir.
func New(dir string, readOnly bool) *Store {
	return &Store{dir: dir, readOnly: readOnly}
}

// Load returns the blob stored under name.
func (sto *Store) Load(name string) ([]byte, error) {
	data, err := os.ReadFile(filepath.Join(sto.dir, name))
	if err != nil {
		return nil, fmt.Errorf("load %s: %w", name, err)
	}
	return data, nil
}

// Save writes data under name.
func (sto *Store) Save(name string, data []byte) error {
	if err := sto.check(); err != nil {
		return fmt.Errorf("save %s: %w", name, err)
	}
	return os.WriteFile(filepath.Join(sto.dir, name), data, 0o600)
}

// check reports whether the store accepts writes.
func (sto *Store) check() error {
	if sto.readOnly {
		return ErrReadOnly
	}
	return nil
}
"""

STORE_NEW = STORE_OLD.replace(
    """	data, err := os.ReadFile(filepath.Join(sto.dir, name))
	if err != nil {
		return nil, fmt.Errorf("load %s: %w", name, err)
	}
	return data, nil""",
    """	data, _ := os.ReadFile(filepath.Join(sto.dir, name))
	return data, nil""").replace(
    'return fmt.Errorf("save %s: %w", name, err)',
    'return fmt.Errorf("save %s: %v", name, err)')
assert STORE_NEW != STORE_OLD and "%v" in STORE_NEW and "data, _" in STORE_NEW

CACHE = """package store

import "errors"

// Cache writes through to a Store and remembers the last value per name.
type Cache struct {
	sto  *Store
	last map[string][]byte
}

// NewCache returns a Cache writing through to sto.
func NewCache(sto *Store) *Cache {
	return &Cache{sto: sto, last: map[string][]byte{}}
}

// Put caches data under name and saves it; on a read-only store the cached
// copy is kept and the write is skipped.
func (cac *Cache) Put(name string, data []byte) error {
	cac.last[name] = data
	err := cac.sto.Save(name, data)
	if errors.Is(err, ErrReadOnly) {
		return nil
	}
	return err
}
"""

V_LINE = line_of(STORE_NEW, '"save %s: %v"')
R_LINE = line_of(STORE_NEW, "data, _ := os.ReadFile")


def case_review_diff():
    sc = scaffold(
        GIT_INIT,
        heredocs({"go.mod": "module example.com/kv\n\ngo 1.22", "store/store.go": STORE_OLD,
                  "store/cache.go": CACHE}),
        commit(),
        heredocs({"store/store.go": STORE_NEW}),
        "git add store/store.go\n")
    graders = {
        "b1-target-is-the-diff": g_regex(r"^(?=[\s\S]*\bdiff\b)(?=[\s\S]*store\.go)", flags="i"),
        "b2-names-tools-run": g_regex(
            r"(tools?|ran|shell|commands? run)[^\n]{0,120}(none|nothing|no (gofmt|go vet|vet|lint|tests?|shell|commands?)|LSP|grep|Read|awk)",
            flags="i"),
        "b2-no-gofmt-vet-lint-test": g_never("Bash", r"gofmt|go vet|golangci|go test|go build|staticcheck"),
        "b3-style-from-go-style": g_regex(r"go:style"),
        "b4-no-write": g_never("Write"),
        "b4-no-edit": g_never("Edit"),
        "b4-tree-unchanged": g_regex(r"^(?=[\s\S]*data, _ := os\.ReadFile)(?=[\s\S]*\"save %s: %v\")",
                                     target={"file": "store/store.go"}),
        "b5-severity-groups": g_regex(r"^(?=[\s\S]*Blocker)(?=[\s\S]*(Should-fix|Nit))"),
        "b5-file-line": g_regex(r"store\.go:\d+"),
        "b5-rule-or-dimension": g_regex(r"^(?=[\s\S]*correctness)(?=[\s\S]*wrap-errors-w)", flags="i"),
        "b6-verdict": g_regex(r"fix[- ]first", flags="i"),
        "b6-counts": g_regex(r"\b\d+\s+blockers?\b|blockers?\W{0,3}\d+", flags="i"),
        # The Load finding sits in the Blocker group and its own item names a
        # concrete reaching input. Regex, not a judge: Haiku failed correct runs.
        "b7-dropped-error-blocker": g_regex(
            r"Blocker(?:(?!Should-fix|\bNits?\b)[\s\S])*?" + rf"store\.go:{R_LINE}\b"
            r"(?=(?:(?!^\s*\d+\.|^#)[\s\S])*?(Load\(|missing|nonexistent|unreadable|permission))",
            flags="m"),
        "b8-wrap-named": g_regex(r"wrap-errors-w"),
        "b8-wrap-reported-once": g_regex(rf"store\.go:{V_LINE}\b", match="count:1"),
        # The :34 finding sits in the Blocker group (before Should-fix/Nit) and
        # its own item, up to the next numbered item or heading, names both
        # correctness and the wrap rule. Single-finding is b8-wrap-reported-once.
        "b8-wrap-under-correctness": g_regex(
            r"Blocker(?:(?!Should-fix|\bNits?\b)[\s\S])*?store\.go:34\b"
            r"(?=(?:(?!^\s*\d+\.|^#)[\s\S])*?correctness)"
            r"(?=(?:(?!^\s*\d+\.|^#)[\s\S])*?(wrap-errors-w|%w))", flags="m"),
    }
    write_case("review--review-the-current-diff",
               CHECK_TAGS, "/go:review", graders, scaffold_sh=sc,
               allowed=["Read", "Glob", "Grep", "Skill", "Bash(git:*)"],
               max_turns=40, timeout=300, asp=ENGLISH)


# ------------------------------------- 2 broad-target-auto-plan-first

PKGS = ["api", "auth", "cache", "config", "events", "httpx", "logx",
        "metrics", "queue", "retry", "worker"]

PKG_SRC = {
    "api": """// Package api routes requests by path prefix.
package api

import "strings"

// Route returns the handler name for path, or "" when none matches.
func Route(routes map[string]string, path string) string {
	for prefix, name := range routes {
		if strings.HasPrefix(path, prefix) {
			return name
		}
	}
	return ""
}
""",
    "auth": """// Package auth checks bearer tokens.
package auth

import "strings"

// Token returns the bearer token from an Authorization header value.
func Token(header string) string {
	return strings.TrimPrefix(header, "Bearer ")[0:32]
}
""",
    "cache": """// Package cache holds values in memory.
package cache

// Cache maps keys to values.
type Cache struct {
	m map[string]string
}

// Set stores v under k.
func (c *Cache) Set(k, v string) {
	c.m[k] = v
}
""",
    "config": """// Package config reads settings from key=value lines.
package config

import "strings"

// Parse returns the settings in text, one key=value pair per line.
func Parse(text string) map[string]string {
	out := map[string]string{}
	for _, line := range strings.Split(text, "\\n") {
		parts := strings.Split(line, "=")
		out[parts[0]] = parts[1]
	}
	return out
}
""",
    "events": """// Package events fans events out to subscribers.
package events

// Bus delivers events to every subscriber.
type Bus struct {
	subs []chan string
}

// Publish sends ev to every subscriber.
func (bus *Bus) Publish(ev string) {
	for _, sub := range bus.subs {
		sub <- ev
	}
}
""",
    "httpx": """// Package httpx holds HTTP helpers.
package httpx

import "net/http"

// IsOK reports whether resp has a 2xx status.
func IsOK(resp *http.Response) bool {
	return resp.StatusCode >= 200 && resp.StatusCode <= 300
}
""",
    "logx": """// Package logx formats log lines.
package logx

import "fmt"

// Line formats one log line.
func Line(level, msg string) string {
	return fmt.Sprintf("[%s] %s", level, msg)
}
""",
    "metrics": """// Package metrics counts events.
package metrics

// Counter counts events.
type Counter struct {
	n int
}

// Inc adds one to the counter.
func (cnt *Counter) Inc() {
	cnt.n++
}

// Value returns the count.
func (cnt *Counter) Value() int {
	return cnt.n
}
""",
    "queue": """// Package queue is a FIFO of ints.
package queue

// Queue is a FIFO of ints.
type Queue struct {
	items []int
}

// Pop removes and returns the oldest item.
func (que *Queue) Pop() int {
	v := que.items[0]
	que.items = que.items[1:]
	return v
}
""",
    "retry": """// Package retry repeats a call until it succeeds.
package retry

// Do calls fn up to n times and returns its last error.
func Do(n int, fn func() error) error {
	var err error
	for i := 0; i < n; i++ {
		err = fn()
	}
	return err
}
""",
    "worker": """// Package worker runs jobs in the background.
package worker

import "sync"

// Pool counts the jobs it has run.
type Pool struct {
	done int
}

// Run runs every job concurrently and waits for them.
func (poo *Pool) Run(jobs []func()) {
	var wg sync.WaitGroup
	for _, job := range jobs {
		wg.Add(1)
		go func() {
			defer wg.Done()
			job()
			poo.done++
		}()
	}
	wg.Wait()
}
""",
}


# Clean, documented helpers so the module is over the ~500-line size below
# which a broad target is reviewed in context: this scenario tests fan-out.
FILLER = """package {p}

import (
	"sort"
	"strings"
)

// Keys returns the keys of m in ascending order.
func Keys(m map[string]int) []string {{
	keys := make([]string, 0, len(m))
	for key := range m {{
		keys = append(keys, key)
	}}
	sort.Strings(keys)
	return keys
}}

// Sum returns the total of values.
func Sum(values []int) int {{
	total := 0
	for _, val := range values {{
		total += val
	}}
	return total
}}

// Clamp returns val limited to the range lo to hi.
func Clamp(val, lo, hi int) int {{
	if val < lo {{
		return lo
	}}
	if val > hi {{
		return hi
	}}
	return val
}}

// Join returns parts joined by sep, skipping empty parts.
func Join(parts []string, sep string) string {{
	kept := make([]string, 0, len(parts))
	for _, part := range parts {{
		if part != "" {{
			kept = append(kept, part)
		}}
	}}
	return strings.Join(kept, sep)
}}
"""


def module_files():
    files = {"go.mod": "module example.com/svc\n\ngo 1.22"}
    for p in PKGS:
        files[f"{p}/{p}.go"] = PKG_SRC[p]
        files[f"{p}/helpers.go"] = FILLER.format(p=p)
    return files


def case_broad_plan_first():
    sc = scaffold(GIT_INIT, heredocs(module_files()), commit())
    tags = CHECK_TAGS
    all_pkgs = "^" + "".join(rf"(?=[\s\S]*\b{p}\b)" for p in PKGS)
    gate = {
        "b1-switches-to-plan-first": g_regex(r"plan[_ -]?first|broad|budget|propos", flags="i"),
        "b2-max-issues-25": g_regex(r"max_issues\W{0,4}25", flags="i"),
        "b2-depth-standard": g_regex(r"depth\W{0,8}standard", flags="i"),
        "b2-package-list": g_regex(all_pkgs),
        "b2-asks": g_regex(r"\?|\breply\b|go[- ]ahead|\bconfirm|approve|say \W?go", flags="i"),
        "b2-no-fanout": g_never("Agent"),
        "b2-no-style-pass": g_never("Skill", "go:style"),
        "b2-no-findings": g_regex(r"\b[a-z]+\.go:\d+", match="not_contains"),
    }
    write_case("review--broad-target-auto-plan-first--gate", tags, "/go:review ./...", gate,
               scaffold_sh=sc, allowed=["Read", "Glob", "Grep", "Skill", "Agent", "Bash(git:*)"],
               max_turns=30, timeout=240, asp=ENGLISH)
    full = {
        "b3-one-subagent-per-package": g_tool("Agent", min_=11),
        "b3-merged-ranked-report": g_regex(r"^(?=[\s\S]*Blocker)(?=[\s\S]*(ship|fix[- ]first))", flags="i"),
        "b3-capped-at-max-issues": g_regex(r"max_issues|unreported|cap", flags="i"),
        # Attributed: a finding opens on its package path, or a per-package
        # heading or verdict row names the package (regex: the judge split 2:1).
        "b4-findings-attributed": g_regex(
            r"^\s*(?:\d+\.|[-*])\s+`?(?:api|auth|cache|config|events|httpx|logx|metrics|queue|retry|worker)/"
            r"|^#{2,4}[^\n]*\b(?:api|auth|cache|config|events|httpx|logx|metrics|queue|retry|worker)\b"
            r"|^\|\s*`?(?:api|auth|cache|config|events|httpx|logx|metrics|queue|retry|worker)`?\s*\|",
            flags="m"),
    }
    asp = ENGLISH + PERSONA + "\n1. go ahead, those defaults are fine\n"
    write_case("review--broad-target-auto-plan-first", tags, "/go:review ./...", full,
               scaffold_sh=sc, allowed=["Read", "Glob", "Grep", "Skill", "Agent", "Bash(git:*)"],
               max_turns=80, timeout=600, asp=asp)


# --------------------------------------- 3 rule-edit-add-change-remove

RULE_QUERY = ('/go:review add "no naked returns in tests", then /go:review change '
              '"receivers are three letters", then /go:review remove "the compile-time '
              'check rule"')


def case_rule_edit():
    sc = scaffold(GIT_INIT, heredocs(STYLE_FILES), commit())
    gate = {
        "b3-no-write": g_never("Write"),
        "b3-no-edit": g_never("Edit"),
        "b3-flags-the-existing-rule": g_regex(
            r"^(?=[\s\S]*naked)(?=[\s\S]*(duplicate|already|inherit|overlap|conflict|covers|existing))",
            flags="i"),
        "b3-quotes-existing-rule-text": g_regex(r"naked returns in non-trivial functions", flags="i"),
        "b3-shows-proposed-text": g_regex(
            r"^\+\s*- [^\n]*naked return|(after|proposed|new)[^\n]{0,40}[:\n][\s\S]{0,400}naked return",
            flags="im"),
    }
    write_case("review--rule-edit-add-change-remove--gate", RULE_TAGS, RULE_QUERY, gate,
               scaffold_sh=sc, allowed=["Read", "Glob", "Grep", "Skill", "Write", "Edit", "Bash(git:*)"],
               max_turns=30, timeout=240, asp=ENGLISH + WIRING)
    asp = ENGLISH + WIRING + "\n" + PERSONA + """
1. Yes, add it to the Test section anyway.
2. Yes, rewrite the receiver rule that way.
3. Yes, remove it, and its rules.md entry too.
"""
    full = {
        "b1-not-a-review-target": g_never("Skill", "go:style"),
        "b1-no-findings": g_regex(r"\b[a-z]+\.go:\d+", match="not_contains"),
        "b2-test-rule-added": g_regex(r"\n## Test\n[\s\S]*\n- (?=[^\n]*naked return)[^\n]{1,100}\n",
                                      target=SKILL_P, flags="i"),
        "b2-one-line-rule": g_regex(r"\n## Test\n[\s\S]*\n- [^\n]*naked return[^\n]*\n(  [^\n]+\n){2,}",
                                    target=SKILL_P, flags="i", match="not_contains"),
        "b4-one-receiver-rule": g_regex(r"^- (?:[^\n]|\n  )*?receiver", target=SKILL_P,
                                        flags="im", match="count:1"),
        "b4-receiver-rule-says-three": g_regex(r"^- (?:[^\n]|\n  )*?receiver(?:[^\n]|\n  )*?three",
                                               target=SKILL_P, flags="im"),
        "b4-old-wording-gone": g_regex(r"short type abbreviation", target=SKILL_P,
                                       match="not_contains"),
        "b5-skill-line-removed": g_regex(r"compile[- ]time|\(\*T\)\(nil\)", target=SKILL_P,
                                         flags="i", match="not_contains"),
        "b5-rules-entry-and-row-removed": g_regex(r"compile[- ]time", target=RULES_P,
                                                  flags="i", match="not_contains"),
        "b5-other-entries-kept": g_regex(
            r"^(?=[\s\S]*- No name stutter \(Production\))(?=[\s\S]*## Method over a single-receiver-arg func)(?=[\s\S]*## Test helpers in all_test\.go)",
            target=RULES_P),
    }
    write_case("review--rule-edit-add-change-remove", RULE_TAGS, RULE_QUERY, full,
               scaffold_sh=sc, allowed=["Read", "Glob", "Grep", "Skill", "Write", "Edit", "Bash(git:*)"],
               max_turns=60, timeout=300, asp=asp)


# ------------------------------------------- 4 learn-from-the-session

POLL_V0 = """// Package poll fetches readings from remote stations on a fixed interval.
package poll

import (
	"context"
	"time"
)

// Fetcher reads the current value of one item.
type Fetcher interface {
	Fetch(ctx context.Context, name string) (float64, error)
}

// Poller fetches every item on a fixed interval.
type Poller struct {
	ctx      context.Context
	fet      Fetcher
	items    []string
	interval time.Duration
}

// Run polls until the context is cancelled.
func (pol *Poller) Run(out chan<- float64) error {
	for {
		select {
		case <-pol.ctx.Done():
			return pol.ctx.Err()
		case <-time.After(pol.interval):
			for _, name := range pol.items {
				val, err := pol.fet.Fetch(pol.ctx, name)
				if err != nil {
					return err
				}
				out <- val
			}
		}
	}
}

// Summary lists the polled items, comma separated.
func (pol *Poller) Summary() string {
	s := ""
	for i, name := range pol.items {
		if i > 0 {
			s += ", "
		}
		s += name
	}
	return s
}
"""

LEARN_EDITS = []  # (user feedback, assistant text, old, new)
LEARN_EDITS.append((
    "Don't call time.After inside the select loop: every iteration allocates a new "
    "timer that isn't released until it fires, so a long-running loop leaks them. "
    "Create one time.Ticker before the loop and select on its channel.",
    "Switched Run to one ticker created before the loop.",
    """	for {
		select {
		case <-pol.ctx.Done():
			return pol.ctx.Err()
		case <-time.After(pol.interval):""",
    """	tick := time.NewTicker(pol.interval)
	defer tick.Stop()
	for {
		select {
		case <-pol.ctx.Done():
			return pol.ctx.Err()
		case <-tick.C:"""))
LEARN_EDITS.append((
    "In Summary, build the string with strings.Builder instead of += in the loop.",
    "Summary now uses strings.Builder.",
    """	s := ""
	for i, name := range pol.items {
		if i > 0 {
			s += ", "
		}
		s += name
	}
	return s""",
    """	var buf strings.Builder
	for i, name := range pol.items {
		if i > 0 {
			buf.WriteString(", ")
		}
		buf.WriteString(name)
	}
	return buf.String()"""))
LEARN_EDITS.append((
    "Don't keep the context in the Poller struct; pass ctx to Run as its first "
    "parameter instead.",
    "Removed the ctx field; Run now takes ctx first.",
    """type Poller struct {
	ctx      context.Context
	fet      Fetcher""",
    """type Poller struct {
	fet      Fetcher"""))
LEARN_EDITS.append((
    None, None,
    """func (pol *Poller) Run(out chan<- float64) error {
	tick := time.NewTicker(pol.interval)
	defer tick.Stop()
	for {
		select {
		case <-pol.ctx.Done():
			return pol.ctx.Err()
		case <-tick.C:
			for _, name := range pol.items {
				val, err := pol.fet.Fetch(pol.ctx, name)""",
    """func (pol *Poller) Run(ctx context.Context, out chan<- float64) error {
	tick := time.NewTicker(pol.interval)
	defer tick.Stop()
	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-tick.C:
			for _, name := range pol.items {
				val, err := pol.fet.Fetch(ctx, name)"""))
LEARN_EDITS.append((
    "Rename items to stations: in this project the things we poll are always stations.",
    "Renamed items to stations.",
    None, None))


def poll_final():
    src = POLL_V0
    for _, _, old, new in LEARN_EDITS:
        if old:
            assert old in src, old
            src = src.replace(old, new)
    src = src.replace('import (\n\t"context"\n\t"time"\n)',
                      'import (\n\t"context"\n\t"strings"\n\t"time"\n)')
    src = src.replace("pol.items", "pol.stations").replace("\titems    []string",
                                                           "\tstations []string")
    src = src.replace("// Summary lists the polled items", "// Summary lists the polled stations")
    return src


def learn_history():
    h = History()
    h.user("poll/poll.go has my first draft of the station poller. Let's clean it up; "
           "read it first.")
    h.tool("", "Read", {"file_path": "poll/poll.go"}, POLL_V0)
    h.say("Read it: a Poller with Run and Summary. What should change?")
    src = POLL_V0
    for fb, txt, old, new in LEARN_EDITS:
        if fb:
            h.user(fb)
        if old:
            h.edit("" if fb else "", "poll/poll.go", old, new)
            src = src.replace(old, new)
        if fb and old and "strings.Builder" in new:
            o = 'import (\n\t"context"\n\t"time"\n)'
            n = 'import (\n\t"context"\n\t"strings"\n\t"time"\n)'
            h.edit("", "poll/poll.go", o, n)
        if txt and old is None:
            h.tool("", "Edit", {"file_path": "poll/poll.go", "old_string": "items",
                                "new_string": "stations", "replace_all": True},
                   "The file poll/poll.go has been updated. All occurrences of 'items' "
                   "were successfully replaced with 'stations'.")
        if txt:
            h.say(txt)
    h.user("Looks good now, thanks.")
    h.say("Done; poll/poll.go builds with all four changes.")
    return h.dump()


def case_learn():
    sc = scaffold(GIT_INIT,
                  heredocs({**STYLE_FILES, "go.mod": "module example.com/pollr\n\ngo 1.22",
                            "poll/poll.go": POLL_V0}),
                  commit(),
                  heredocs({"poll/poll.go": poll_final()}))
    hist = learn_history()
    gate = {
        "b1-pairs-feedback-with-hunks": g_llm(
            "Each proposed rule is shown with the code change from this session that "
            "resolved the user's correction, as a before/after example or hunk."),
        "b2-proposes-timer-rule": g_regex(r"time\.After", flags="i"),
        "b2-timer-before-after": g_regex(r"(Ticker|NewTimer|timer\.Reset)"),
        "b2-proposes-builder-rule": g_regex(r"strings\.Builder"),
        "b2-builder-before-after": g_regex(r"\+=") ,
        "b2-provenance": g_regex(
            r"(comes? from|came from|provenance|prompted by|source:|from:|you (said|asked|rejected|wrote)|your (correction|feedback|instruction|request|\w+ fix))",
            flags="i"),
        "b3-drops-the-rename": g_llm(
            "The items-to-stations rename is not proposed as a style rule; if it is "
            "mentioned at all, it is as dropped or project-specific."),
        "b4-context-already-covered": g_regex(
            r"^(?=[^\n]*context)(?=[^\n]*(already|covered|existing|duplicate|dedup))", flags="im"),
        "b5-no-write": g_never("Write"),
        "b5-no-edit": g_never("Edit"),
        "b5-asks-to-pick": g_regex(r"\?|\b(tell me|let me know) which\b|\bwhich (to|ones? to) keep\b", flags="i"),
    }
    write_case("review--learn-from-the-session--gate", RULE_TAGS, "/go:review learn", gate,
               scaffold_sh=sc, history=hist,
               allowed=["Read", "Glob", "Grep", "Skill", "Write", "Edit", "Bash(git:*)"],
               max_turns=30, timeout=240, asp=ENGLISH + WIRING)
    asp = ENGLISH + WIRING + "\n" + PERSONA + "\n1. Keep both new rules.\n"
    full = {
        "b5-timer-rule-written": g_regex(r"\n## Production\n[\s\S]*(time\.After|timer)[\s\S]*\n## Test\n",
                                         target=SKILL_P, flags="i"),
        "b5-builder-rule-written": g_regex(r"strings\.Builder", target=SKILL_P),
        "b5-no-context-duplicate": g_regex(r"never store it in a", target=SKILL_P, match="count:1"),
        "b5-no-rename-rule": g_regex(r"station", target=SKILL_P, flags="i", match="not_contains"),
        "b5-shows-the-diff": g_regex(r"```diff|^\+\s*- ", flags="m"),
    }
    write_case("review--learn-from-the-session", RULE_TAGS, "/go:review learn", full,
               scaffold_sh=sc, history=hist,
               allowed=["Read", "Glob", "Grep", "Skill", "Write", "Edit", "Bash(git:*)"],
               max_turns=40, timeout=300, asp=asp)


# --------------------------------------- 7 learn-finds-nothing-new

SRV_V0 = """// Package srv serves the status page.
package srv

import (
	"fmt"
	"net"
)

// Server listens for status requests.
type Server struct {
	addr string
	ln   net.Listener
}

// Start opens the listener.
func (s *Server) Start() error {
	ln, err := net.Listen("tcp", s.addr)
	if err != nil {
		return fmt.Errorf("listen %s: %v", s.addr, err)
	}
	s.ln = ln
	return nil
}
"""

SRV_TEST_V0 = """package srv

import "testing"

func Test_Server_Start(t *testing.T) {
	// --- Given ---
	srv := &Server{addr: "127.0.0.1:0"}

	// --- When ---
	got := srv.Start()

	// --- Then ---
	if got != nil {
		t.Fatal(got)
	}
}
"""


def nothing_history():
    h = History()
    h.user("srv/server.go and srv/server_test.go have the new Start method. Read both "
           "and tidy them up with me.")
    h.tool("", "Read", {"file_path": "srv/server.go"}, SRV_V0)
    h.tool("", "Read", {"file_path": "srv/server_test.go"}, SRV_TEST_V0)
    h.say("Read both. What should change?")
    h.user("Wrap the listen error with %w, not %v, so callers can match it.")
    h.edit("", "srv/server.go", 'return fmt.Errorf("listen %s: %v", s.addr, err)',
           'return fmt.Errorf("listen %s: %w", s.addr, err)')
    h.say("Now wrapped with %w.")
    h.user("In the test, call the result have, never got.")
    h.edit("", "srv/server_test.go", """	got := srv.Start()

	// --- Then ---
	if got != nil {
		t.Fatal(got)
	}""", """	have := srv.Start()

	// --- Then ---
	if have != nil {
		t.Fatal(have)
	}""")
    h.say("Renamed got to have.")
    h.user("The receiver can't be a single letter; use srv for *Server.")
    h.tool("", "Edit", {"file_path": "srv/server.go", "old_string": "s.", "new_string": "srv.",
                        "replace_all": True}, "The file srv/server.go has been updated.")
    h.edit("", "srv/server.go", "func (s *Server) Start() error {",
           "func (srv *Server) Start() error {")
    h.say("Receiver is srv now.")
    h.user("Good, that's it.")
    h.say("Done.")
    return h.dump()


def case_learn_nothing():
    srv_final = SRV_V0.replace("%v", "%w").replace("(s *Server)", "(srv *Server)") \
        .replace("s.addr", "srv.addr").replace("s.ln", "srv.ln")
    test_final = SRV_TEST_V0.replace("got", "have")
    sc = scaffold(GIT_INIT,
                  heredocs({**STYLE_FILES, "go.mod": "module example.com/status\n\ngo 1.22",
                            "srv/server.go": SRV_V0, "srv/server_test.go": SRV_TEST_V0}),
                  commit(),
                  heredocs({"srv/server.go": srv_final, "srv/server_test.go": test_final}))
    graders = {
        "b1-says-already-rules": g_regex(r"already", flags="i"),
        "b1-names-wrap-rule": g_regex(r"%w"),
        "b1-names-have-want-rule": g_regex(r"\bhave\b"),
        "b1-names-receiver-rule": g_regex(r"receiver", flags="i"),
        "b2-no-write": g_never("Write"),
        "b2-no-edit": g_never("Edit"),
        "b3-no-candidate-proposed": g_llm(
            "The reply proposes no new rule and asks the user to pick or confirm no rule "
            "candidate; it does not restate an existing rule as a new candidate."),
        "b4-rules-not-reaching-the-work": g_regex(
            r"(not|n't)\s+(reaching|being applied|applied|followed|being followed|landing|making it)|re-?learn|reach(ing)? the work",
            flags="i"),
    }
    write_case("review--learn-finds-nothing-new", RULE_TAGS, "/go:review learn", graders,
               scaffold_sh=sc, history=nothing_history(),
               allowed=["Read", "Glob", "Grep", "Skill", "Write", "Edit", "Bash(git:*)"],
               max_turns=30, timeout=240, asp=ENGLISH + WIRING)


# ------------------------------------- 5 broad-fix-job-plans-and-pauses

FIX_SRC = {
    "money/money.go": """// Package money converts amounts between floats and cents.
package money

// Cents converts an amount in currency units to whole cents.
func Cents(amount float64) int64 {
	return int64(amount * 100)
}
""",
    "money/money_test.go": """package money

import "testing"

func Test_Cents(t *testing.T) {
	// --- When ---
	have := Cents(2)

	// --- Then ---
	if have != 200 {
		t.Fatalf("have %d, want 200", have)
	}
}
""",
    "parse/parse.go": """// Package parse reads key=value pairs.
package parse

import "strings"

// Pair splits one key=value pair; the value may itself contain '='.
func Pair(s string) (string, string) {
	parts := strings.Split(s, "=")
	return parts[0], parts[1]
}
""",
    "parse/parse_test.go": """package parse

import "testing"

func Test_Pair(t *testing.T) {
	// --- When ---
	key, val := Pair("a=b")

	// --- Then ---
	if key != "a" || val != "b" {
		t.Fatalf("have %q %q, want a b", key, val)
	}
}
""",
    "queue/queue.go": """// Package queue is a FIFO of ints.
package queue

// Queue is a FIFO of ints.
type Queue struct {
	items []int
}

// Push appends v.
func (que *Queue) Push(v int) {
	que.items = append(que.items, v)
}

// Pop removes and returns the oldest item; ok is false when the queue is empty.
func (que *Queue) Pop() (int, bool) {
	if len(que.items) == 0 {
		return 0, true
	}
	v := que.items[0]
	que.items = que.items[1:]
	return v, true
}
""",
    "queue/queue_test.go": """package queue

import "testing"

func Test_Queue_Pop(t *testing.T) {
	// --- Given ---
	que := &Queue{}
	que.Push(7)

	// --- When ---
	have, ok := que.Pop()

	// --- Then ---
	if have != 7 || !ok {
		t.Fatalf("have %d %v, want 7 true", have, ok)
	}
}
""",
    "report/report.go": """// Package report renders plain-text tables.
package report

import "strings"

// Pad right-pads s with spaces to width runes.
func Pad(s string, width int) string {
	if len(s) >= width {
		return s
	}
	return s + strings.Repeat(" ", width-len(s))
}
""",
    "report/report_test.go": """package report

import "testing"

func Test_Pad(t *testing.T) {
	// --- When ---
	have := Pad("ab", 4)

	// --- Then ---
	if have != "ab  " {
		t.Fatalf("have %q, want %q", have, "ab  ")
	}
}
""",
    "ledger/ledger.go": """// Package ledger records postings and balances accounts.
package ledger

import "errors"

// ErrUnbalanced is returned when a transaction's postings do not sum to zero.
var ErrUnbalanced = errors.New("unbalanced transaction")

// Posting moves amount cents into (positive) or out of (negative) account.
type Posting struct {
	Account string
	Amount  int64
}

// Ledger holds the postings of every committed transaction.
type Ledger struct {
	postings []Posting
	closed   map[string]bool
}

// New returns an empty Ledger.
func New() *Ledger {
	return &Ledger{closed: map[string]bool{}}
}
""",
    "ledger/post.go": """package ledger

// Post commits a transaction whose postings must sum to zero.
func (led *Ledger) Post(txn []Posting) error {
	var sum int64
	for _, pst := range txn {
		sum += pst.Amount
	}
	if sum != 0 {
		_ = ErrUnbalanced
	}
	led.postings = append(led.postings, txn...)
	return nil
}
""",
    "ledger/close.go": """package ledger

// Close marks every account in names closed and returns how many were open.
func (led *Ledger) Close(names []string) int {
	n := 0
	for i := 1; i < len(names); i++ {
		if !led.closed[names[i]] {
			n++
		}
		led.closed[names[i]] = true
	}
	return n
}
""",
    "ledger/balance.go": """package ledger

// Average returns the mean posting amount for account.
func (led *Ledger) Average(account string) int64 {
	var sum, cnt int64
	for _, pst := range led.postings {
		if pst.Account == account {
			sum += pst.Amount
			cnt++
		}
	}
	return sum / cnt
}
""",
    "ledger/ledger_test.go": """package ledger

import "testing"

func Test_Ledger_Post(t *testing.T) {
	// --- Given ---
	led := New()
	txn := []Posting{{"cash", 100}, {"sales", -100}}

	// --- When ---
	err := led.Post(txn)

	// --- Then ---
	if err != nil {
		t.Fatal(err)
	}
}
""",
}


def case_fix_job():
    sc = scaffold(GIT_INIT,
                  heredocs({"go.mod": "module example.com/books\n\ngo 1.22",
                            ".gitignore": "tmp/", **FIX_SRC}),
                  commit())
    tags = CHECK_TAGS + ["sec:style:test", "ref:review/fixing"]
    allowed = ["Read", "Glob", "Grep", "Skill", "Write", "Edit", "Bash(git:*)", "Bash(go:*)"]
    plan = {"file": "tmp/review-fix-plan.md"}
    gate = {
        "b1-plan-written": g_exists("tmp/review-fix-plan.md"),
        "b1-plan-one-chunk-per-package": g_regex(
            r"^(?=[\s\S]*money)(?=[\s\S]*parse)(?=[\s\S]*queue)(?=[\s\S]*report)(?=[\s\S]*ledger)",
            target=plan),
        "b1-plan-status-boxes": g_regex(r"\[ \]", target=plan),
        "b1-asks-go-ahead": g_regex(r"\?|go[- ]ahead|say \W?go|\bconfirm|approve", flags="i"),
        "b1-no-go-edit": g_never("Edit", r"\.go\""),
        "b1-no-go-write": g_never("Write", r"\.go\""),
        "b2-ledger-split-into-files": g_regex(
            r"^(?=[\s\S]*post\.go)(?=[\s\S]*close\.go)(?=[\s\S]*balance\.go)", target=plan),
    }
    write_case("review--broad-fix-job-plans-and-pauses--gate", tags, "/go:review ./... fix",
               gate, scaffold_sh=sc, allowed=allowed, max_turns=50, timeout=300, asp=ENGLISH)
    asp = ENGLISH + PERSONA + """
1. go ahead
2. go ahead
3. go ahead
4. go ahead
5. go ahead
6. go ahead
7. go ahead
"""
    full = {
        "b3-red-output-captured": g_regex(r"--- FAIL", target="trace"),
        "b3-test-named-have-want": g_regex(r"\"file_path\":\"[^\"]*_test\.go\"[^\n]*\bhave\b",
                                           target="trace"),
        "b3-no-got": g_regex(r"\"file_path\":\"[^\"]*_test\.go\"[^\n]*\bgot\b", target="trace",
                             match="not_contains"),
        "b4-race-gate-per-chunk": g_tool("Bash", r"go test[^\"]*\./\.\.\.[^\"]*-race|go test[^\"]*-race[^\"]*\./\.\.\.",
                                         min_=3),
        "b4-boxes-ticked": g_regex(r"\[x\]", target=plan, flags="i"),
        # No b5 (pause after each chunk): scripted runs take answers silently,
        # so a pause leaves no trace; accepted harness limit (plan Phase 0, 2).
        "b6-never-commits": g_never("Bash", "git commit"),
    }
    # Five chunks, each proven red then green: over 300 s on a normal run.
    write_case("review--broad-fix-job-plans-and-pauses", tags + ["long"], "/go:review ./... fix", full,
               scaffold_sh=sc, allowed=allowed, max_turns=80, timeout=600, asp=asp)


# ----------------------------------------------------- 6 terse-output

FOO = """// Package foo computes statistics over integer samples.
package foo

import "errors"

// ErrEmpty is returned when a statistic needs at least one sample.
var ErrEmpty = errors.New("no samples")

// Series holds integer samples in arrival order.
type Series struct {
	vals []int
}

// Add appends v to the series.
func (s *Series) Add(v int) {
	s.vals = append(s.vals, v)
}

// Max returns the largest sample.
func (s *Series) Max() int {
	m := s.vals[0]
	for _, v := range s.vals[1:] {
		if v > m {
			m = v
		}
	}
	return m
}

// Mean returns the arithmetic mean of the samples.
func (s *Series) Mean() (float64, error) {
	if len(s.vals) == 0 {
		return 0, ErrEmpty
	}
	sum := 0
	for _, v := range s.vals {
		sum += v
	}
	return float64(sum) / float64(len(s.vals)), nil
}
"""


def case_terse():
    sc = scaffold(GIT_INIT,
                  heredocs({"go.mod": "module example.com/demo\n\ngo 1.22", "pkg/foo/foo.go": FOO}),
                  commit())
    graders = {
        "b1-no-preamble": g_regex(
            r"^\s*(I'll|I will|Let me|I've|I have|I read|I'm|Reading|First,|Now|Okay|OK,|Sure|Here's|Here is|Done)",
            match="not_contains"),
        "b1-opens-with-target-or-findings": g_regex(
            r"^\s*(?:#+\s*)?[^\n]*(pkg/foo|foo\.go|Blocker|Target)"),
        "b1-no-rule-reading-narration": g_regex(
            r"(read|loaded|loading|reading|consulted)[^.\n]{0,30}(rules|rulebook|style guide|SKILL\.md|checking\.md)",
            flags="i", match="not_contains"),
        "b2-max-finding-once": g_regex(r"foo\.go:2[01]\b", match="count:1"),
        "b2-budget-depth": g_regex(r"depth\W{0,4}standard", flags="i"),
        "b2-budget-unreported": g_regex(r"max_issues|unreported", flags="i"),
    }
    write_case("review--terse-output", CHECK_TAGS, "/go:review ./pkg/foo", graders,
               scaffold_sh=sc, allowed=["Read", "Glob", "Grep", "Skill", "Bash(git:*)"],
               max_turns=30, timeout=240, asp=ENGLISH)


if __name__ == "__main__":
    os.makedirs(EVALS, exist_ok=True)
    case_review_diff()
    case_broad_plan_first()
    case_rule_edit()
    case_learn()
    case_learn_nothing()
    case_fix_job()
    case_terse()
    print("ok")
