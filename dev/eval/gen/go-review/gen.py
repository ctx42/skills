#!/usr/bin/env python3
"""Generate go/evals/review--* native eval cases. Re-runnable; owns only review--*."""
import json
import os
import random
import shutil
import uuid


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
EVALS = os.path.join(ROOT, "go/evals")

ENGLISH = "The user writes English; reply in English.\n"
NOTICE = "Ignore any trailing policy notice. "

CHECK_TAGS = ["skill:review", "sec:review:usage",
              "sec:review:check-mode", "ref:style/checking", "ref:style/production"]

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
    # eval-changed.py grants Bash only to needs-shell cases
    if any(t.startswith("Bash") for t in allowed) and "needs-shell" not in tags:
        tags = tags + ["needs-shell"]
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
            r"(tools?|ran|shell|commands? run)[^\n]{0,120}(none|nothing|no (gofmt|go vet|vet|lint|tests?|shell|commands?)|LSP|grep|Read|awk|wc|expand|width)",
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
            r"(?=(?:(?!^\s*\d+\.|^#)[\s\S])*?(Load\(|missing|nonexistent|unreadable|permission|(?:doesn't|does not|not) exist|(?:can't|cannot) (?:be )?read))",
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
               allowed=["Read", "Glob", "Grep", "Skill", "Write", "Edit", "Bash(git:*)"],
               max_turns=40, timeout=300, asp=ENGLISH)


# ------------------------------------------- 5 rule-request-redirects

def case_rule_redirect():
    sc = scaffold(GIT_INIT, heredocs({"go.mod": "module example.com/kv\n\ngo 1.22",
                                      "store/store.go": STORE_OLD}), commit())
    graders = {
        "b1-names-go-style": g_regex(r"go:style"),
        "b1-names-the-command": g_regex(r"/go:style add"),
        "b1-no-findings": g_regex(r"\b[a-z]+\.go:\d+", match="not_contains"),
        "b2-no-write": g_never("Write"),
        "b2-no-edit": g_never("Edit"),
    }
    write_case("review--rule-request-redirects",
               ["skill:review", "sec:review:usage"],
               '/go:review add "no naked returns in tests"', graders, scaffold_sh=sc,
               allowed=["Read", "Glob", "Grep", "Skill", "Write", "Edit"],
               max_turns=20, timeout=180, asp=ENGLISH)


# ------------------------------------- 6 session-rules-offered-at-close

# Seeded so a rerun reproduces the committed history file byte for byte.
_rng = random.Random(6)


def _uuid4():
    return uuid.UUID(int=_rng.getrandbits(128), version=4)


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


NESTED = """\tif err != nil {
		return err
	} else {
		cache[key] = data
	}
	return nil"""
EARLY = """\tif err != nil {
		return err
	}
	cache[key] = data
	return nil"""
NESTED2 = """\tif len(key) == 0 {
		return errors.New("empty key")
	} else {
		delete(cache, key)
	}
	return nil"""
EARLY2 = """\tif len(key) == 0 {
		return errors.New("empty key")
	}
	delete(cache, key)
	return nil"""

MEM_V0 = """// Package mem keeps decoded blobs in memory.
package mem

import "errors"

var cache = map[string][]byte{}

// Put decodes raw and stores it under key.
func Put(key string, raw []byte) error {
	data, err := decode(raw)
""" + NESTED + """
}

// Drop removes key.
func Drop(key string) error {
""" + NESTED2 + """
}

func decode(raw []byte) ([]byte, error) { return raw, nil }
"""


def session_history():
    h = History()
    h.user("mem/mem.go needs tidying; read it first.")
    h.tool("", "Read", {"file_path": "mem/mem.go"}, MEM_V0)
    h.say("Read it: Put and Drop both nest the success path in an else branch.")
    h.user("Return early instead of nesting the else branch in Put.")
    h.edit("", "mem/mem.go", NESTED, EARLY)
    h.say("Done: Put returns early on the error.")
    h.user("Same in Drop: return early instead of nesting the else branch.")
    h.edit("", "mem/mem.go", NESTED2, EARLY2)
    h.say("Done: Drop returns early too.")
    return h.dump()


def case_session_rules():
    sc = scaffold(GIT_INIT, heredocs({"go.mod": "module example.com/mem\n\ngo 1.22",
                                      "mem/mem.go": MEM_V0}), commit(),
                  heredocs({"mem/mem.go": MEM_V0.replace(NESTED, EARLY).replace(NESTED2, EARLY2)}),
                  "git add mem/mem.go\n")
    graders = {
        "b1-heading": g_regex(r"Rules this session taught"),
        "b1-early-return-candidate": g_regex(
            r"Rules this session taught[\s\S]*(early return|return early|nest(ed|ing)?[^\n]{0,40}else)",
            flags="i"),
        "b2-no-write": g_never("Write"),
        "b2-no-edit": g_never("Edit"),
    }
    write_case("review--session-rules-offered-at-close", CHECK_TAGS,
               "/go:review", graders, scaffold_sh=sc, history=session_history(),
               allowed=["Read", "Glob", "Grep", "Skill", "Write", "Edit", "Bash(git:*)"],
               max_turns=40, timeout=300, asp=ENGLISH)


if __name__ == "__main__":
    os.makedirs(EVALS, exist_ok=True)
    case_review_diff()
    case_rule_redirect()
    case_session_rules()
    print("ok")
