#!/usr/bin/env python3
"""Generate go/evals/style--* native eval cases. Rewrites only style--* dirs.

Usage: gen.py [--check DIR]  (--check also materialises every scaffold under
DIR and runs `go vet` + a width check, outside any eval).
"""
import os
import shutil
import subprocess
import sys
import textwrap

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
EVALS = os.path.join(ROOT, "go", "evals")

ENGLISH = "The user writes English; reply in English."

GOMOD_DEP = """module example.com/{mod}

go 1.26

require github.com/ctx42/testing v0.56.0
"""
GOSUM = """github.com/ctx42/testing v0.56.0 h1:+yZwRy+5JQb+14YtRTGJxWbAMAP9qlU9pMa8TPqgdzE=
github.com/ctx42/testing v0.56.0/go.mod h1:wRBqNRtlxDZnXIjgCX3zr05Acl6JC1D6cSBN2IpaMIs=
"""
GOMOD_NODEP = """module example.com/{mod}

go 1.26
"""

PASS_TAGS = ["skill:style", "sec:style:usage", "sec:style:production",
             "sec:style:test", "sec:style:self-learning", "ref:style/checking"]
PASS_TOOLS = ["Read", "Glob", "Grep", "Skill", "LSP", "Write", "Edit"]
FAN_TOOLS = PASS_TOOLS + ["Agent", "Task"]

NATO = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf",
        "hotel"]


def dedent(s):
    return textwrap.dedent(s).lstrip("\n")


# --------------------------------------------------------------------------
# Record template (cases 7, 10, 11, 12).

def record_src(pkg, wrap_v=False, recv_r=False, pair_nodoc=False,
               failed_to=False, ticket=False, add_doc_rec=False):
    pair_doc = "" if pair_nodoc else \
        '// Pair returns the record in the form "key=value".\n'
    recv = "r" if recv_r else "rec"
    add_doc = ("// Add adds n to rec.Value and returns the new value.\n"
               if add_doc_rec else
               "// Add adds n to the record's value and returns the new "
               "value.\n")
    verb = "%v" if wrap_v else "%w"
    split_ctx = "failed to parse record %d: %w" if failed_to else \
        "record %d: %w"
    tick = "\t// SHOP-42: an empty part is a parse error, not skipped.\n" \
        if ticket else ""
    return (
        f"// Package {pkg} parses key-value records.\n"
        f"package {pkg}\n"
        "\n"
        "import (\n"
        "\t\"fmt\"\n"
        "\t\"strconv\"\n"
        "\t\"strings\"\n"
        ")\n"
        "\n"
        "// Record is one key-value pair.\n"
        "type Record struct {\n"
        "\tKey   string\n"
        "\tValue int\n"
        "}\n"
        "\n"
        f"{pair_doc}"
        f"func ({recv} Record) Pair() string {{\n"
        f"\treturn {recv}.Key + \"=\" + strconv.Itoa({recv}.Value)\n"
        "}\n"
        "\n"
        f"{add_doc}"
        "func (rec *Record) Add(n int) int {\n"
        "\trec.Value += n\n"
        "\treturn rec.Value\n"
        "}\n"
        "\n"
        "// Parse parses s in the form \"key=value\".\n"
        "func Parse(s string) (Record, error) {\n"
        "\tkey, raw, _ := strings.Cut(s, \"=\")\n"
        "\tval, err := strconv.Atoi(raw)\n"
        "\tif err != nil {\n"
        f"\t\treturn Record{{}}, fmt.Errorf(\"parse value: {verb}\", err)\n"
        "\t}\n"
        "\treturn Record{Key: key, Value: val}, nil\n"
        "}\n"
        "\n"
        "// Split parses every sep-separated record in s.\n"
        "func Split(s, sep string) ([]Record, error) {\n"
        "\tvar recs []Record\n"
        f"{tick}"
        "\tfor i, part := range strings.Split(s, sep) {\n"
        "\t\trec, err := Parse(part)\n"
        "\t\tif err != nil {\n"
        f"\t\t\treturn nil, fmt.Errorf(\"{split_ctx}\", i, err)\n"
        "\t\t}\n"
        "\t\trecs = append(recs, rec)\n"
        "\t}\n"
        "\treturn recs, nil\n"
        "}\n"
    )


def record_test(pkg, given_blank=True, then_surplus=False, got=False,
                swap_order=False, bad_subtest=False):
    have = "got" if got else "have"
    pair = (
        "func Test_Record_Pair(t *testing.T) {\n"
        "\t// --- Given ---\n"
        "\trec := Record{Key: \"a\", Value: 1}\n"
        "\n"
        "\t// --- When ---\n"
        f"\t{have} := rec.Pair()\n"
        "\n"
        "\t// --- Then ---\n"
        f"\tassert.Equal(t, \"a=1\", {have})\n"
        "}\n"
    )
    add = (
        "func Test_Record_Add(t *testing.T) {\n"
        "\t// --- Given ---\n"
        "\trec := &Record{Key: \"a\", Value: 1}\n"
        "\n"
        "\tn := 2\n"
        "\n"
        "\t// --- When ---\n"
        "\thave := rec.Add(n)\n"
        "\n"
        "\t// --- Then ---\n"
        "\tassert.Equal(t, 3, have)\n"
        "\n"
        "\tassert.Equal(t, 3, rec.Value)\n"
        "}\n"
    )
    first, second = (add, pair) if swap_order else (pair, add)
    errname = "error - value not a number." if bad_subtest else \
        "error - value not a number"
    gb = "\n" if given_blank else ""
    ts = "\n" if then_surplus else ""
    return (
        f"package {pkg}\n"
        "\n"
        "import (\n"
        "\t\"testing\"\n"
        "\n"
        "\t\"github.com/ctx42/testing/pkg/assert\"\n"
        ")\n"
        "\n"
        f"{first}"
        "\n"
        f"{second}"
        "\n"
        "func Test_Parse(t *testing.T) {\n"
        "\tt.Run(\"valid\", func(t *testing.T) {\n"
        "\t\t// --- Given ---\n"
        "\t\ts := \"a=1\"\n"
        "\n"
        "\t\t// --- When ---\n"
        "\t\thave, err := Parse(s)\n"
        "\n"
        "\t\t// --- Then ---\n"
        "\t\tassert.NoError(t, err)\n"
        "\t\tassert.Equal(t, Record{Key: \"a\", Value: 1}, have)\n"
        "\t})\n"
        "\n"
        f"\tt.Run(\"{errname}\", func(t *testing.T) {{\n"
        "\t\t// --- Given ---\n"
        "\t\ts := \"a=x\"\n"
        "\n"
        "\t\t// --- When ---\n"
        "\t\thave, err := Parse(s)\n"
        "\n"
        "\t\t// --- Then ---\n"
        "\t\tassert.ErrorContain(t, \"invalid syntax\", err)\n"
        "\t\tassert.Zero(t, have)\n"
        "\t})\n"
        "}\n"
        "\n"
        "func Test_Split(t *testing.T) {\n"
        "\tt.Run(\"valid\", func(t *testing.T) {\n"
        "\t\t// --- Given ---\n"
        "\t\ts := \"a=1\"\n"
        f"{gb}"
        "\t\tsep := \";\"\n"
        "\n"
        "\t\t// --- When ---\n"
        "\t\thave, err := Split(s, sep)\n"
        "\n"
        "\t\t// --- Then ---\n"
        "\t\tassert.NoError(t, err)\n"
        f"{ts}"
        "\t\tassert.Equal(t, []Record{{Key: \"a\", Value: 1}}, have)\n"
        "\t})\n"
        "\n"
        "\tt.Run(\"error - bad record\", func(t *testing.T) {\n"
        "\t\t// --- Given ---\n"
        "\t\ts := \"a=1;b=x\"\n"
        f"{gb}"
        "\t\tsep := \";\"\n"
        "\n"
        "\t\t// --- When ---\n"
        "\t\thave, err := Split(s, sep)\n"
        "\n"
        "\t\t// --- Then ---\n"
        "\t\tassert.ErrorContain(t, \"invalid syntax\", err)\n"
        "\t\tassert.Nil(t, have)\n"
        "\t})\n"
        "}\n"
    )


def line_of(text, needle, nth=1):
    n = 0
    for i, ln in enumerate(text.split("\n"), 1):
        if needle in ln:
            n += 1
            if n == nth:
                return i
    raise ValueError(f"{needle!r} not found")


# --------------------------------------------------------------------------
# Emitters.

def fm_list(xs):
    return "[" + ", ".join(xs) + "]"


def prompt_md(name, tags, body, max_turns=40, timeout=300, tools=PASS_TOOLS,
              asp=ENGLISH):
    if timeout > 300:  # lint allows over 300 s only on a fan-out-tagged case
        tags = tags + ["fan-out"]
    lines = ["---", f"tags: {fm_list(['case:' + name] + tags)}", "runs: 1",
             f"max_turns: {max_turns}", f"timeout_seconds: {timeout}",
             f"allowed_tools: {fm_list(tools)}", "append_system_prompt: |"]
    for ln in asp.rstrip("\n").split("\n"):
        lines.append(("  " + ln) if ln else "")
    lines += ["---", "", body, ""]
    return "\n".join(lines)


GO_MOD_DOWNLOAD = """# Runs have no network: fill the run's module cache now, from the local cache
# that dev/eval-changed.sh serves as GOPROXY.
go mod download
"""


def scaffold_sh(files, extra=""):
    out = ["#!/usr/bin/env bash", "set -euo pipefail"]
    dirs = sorted({os.path.dirname(p) for p in files if os.path.dirname(p)})
    if dirs:
        out.append("mkdir -p " + " ".join(dirs))
    for path, content in files.items():
        tag = "EOF_" + "".join(c if c.isalnum() else "_" for c in
                               path).upper()
        assert tag not in content
        out.append(f"cat > {path} <<'{tag}'")
        out.append(content.rstrip("\n"))
        out.append(tag)
    if "go.sum" in files:
        out.append(GO_MOD_DOWNLOAD.rstrip("\n"))
    if extra:
        out.append(extra.rstrip("\n"))
    return "\n".join(out) + "\n"


def g_regex(pattern, target="last_message", match=None, flags=None):
    if isinstance(target, str):
        t = target
    else:
        t = "{source: file, path: " + target[1] + "}"
    fm = ["type: regex", f"target: {t}"]
    if match:
        fm.append(f'match: {match if match == "not_contains" else repr(match).replace(chr(39), chr(34))}')
    if flags:
        fm.append(f'flags: "{flags}"')
    return "---\n" + "\n".join(fm) + "\n---\n" + pattern + "\n"


def file_t(path):
    return ("file", path)


def g_tool(tool, min_=None, max_=None, input_match=None, arm=None):
    fm = ["type: tool_used", f"tool: {tool}"]
    if input_match:
        fm.append("input_match: '" + input_match.replace("'", "''") + "'")
    if min_ is not None:
        fm.append(f"min: {min_}")
    if max_ is not None:
        fm.append(f"max: {max_}")
    if arm:
        fm.append(f"arm: {arm}")
    return "---\n" + "\n".join(fm) + "\n---\n"


def g_never(tool, input_match=None):
    return g_tool(tool, 0, 0, input_match, "both")


def width_pattern(limit, tab=4, max_tabs=6):
    alts = [f"^\\t{{{k}}}[^\\t\\n]{{{limit - tab * k + 1},}}$"
            for k in range(max_tabs + 1)]
    return "|".join(alts)


CASES = {}


def case(name, prompt, graders, files=None, extra=""):
    CASES[name] = dict(prompt=prompt, graders=graders, files=files,
                       extra=extra)


# --------------------------------------------------------------------------
# 1. production-rules-while-writing

EDITORCONFIG_72 = dedent("""
    root = true

    [*.go]
    indent_style = tab
    tab_width = 4
    max_line_length = 72
""")

SERVICE_GO = dedent("""
    // Package svc serves records from a store and keeps an audit log.
    package svc

    import "io"

    // Service serves records from a store and writes an audit log.
    type Service struct {
    	store  io.Closer
    	audit  io.Closer
    	served int
    }

    // New returns a Service over store that logs to audit.
    func New(store, audit io.Closer) *Service {
    	return &Service{store: store, audit: audit}
    }

    // Served returns the number of records served so far.
    func (svc *Service) Served() int {
    	return svc.served
    }
""")

LOAD_STYLE = ("This project's Go conventions live in the go:style skill; "
              "load it\nbefore editing any .go file.")

n = "style--production-rules-while-writing"
case(n,
     prompt_md(n, ["skill:style", "sec:style:production",
                   "sec:style:self-learning"],
               "Add a Close method to the Service type in service.go",
               max_turns=30, tools=["Read", "Glob", "Grep", "Skill", "LSP",
                                    "Write", "Edit"],
               asp=ENGLISH + "\n" + LOAD_STYLE),
     {
         "b1-tab-indented": g_regex(r"^ +\S", file_t("service.go"),
                                    "not_contains", "m"),
         "b1-within-resolved-limit": g_regex(width_pattern(72),
                                             file_t("service.go"),
                                             "not_contains", "m"),
         # errors.Join keeps both Close errors matchable, as %w does.
         "b1-wraps-with-w": g_regex(r'fmt\.Errorf\("[a-z][^"%]*: %w"|errors\.Join\(',
                                    file_t("service.go")),
         "b1-no-v-or-failed-to": g_regex(r"%v|[Ff]ailed to",
                                         file_t("service.go"),
                                         "not_contains"),
         "b1-close-has-godoc": g_regex(
             r"// Close [^\n]*\n(//[^\n]*\n)*func \(\w+ \*Service\) Close\(\)",
             file_t("service.go")),
         "b2-no-have-want-got": g_regex(r"\b(have|want|got)\b",
                                        file_t("service.go"),
                                        "not_contains"),
         "b2-no-subtests": g_regex(r"t\.Run\(|\*testing\.T",
                                   file_t("service.go"), "not_contains"),
     },
     files={".editorconfig": EDITORCONFIG_72,
            "go.mod": GOMOD_NODEP.format(mod="svc"),
            "service.go": SERVICE_GO})

# --------------------------------------------------------------------------

SETTING_GO = dedent("""
    // Package foo parses "key=value" settings.
    package foo

    import (
    	"bufio"
    	"fmt"
    	"io"
    	"strconv"
    	"strings"
    )

    // Setting is one parsed key-value pair.
    type Setting struct {
    	Key   string
    	Value int
    }

    // Parse parses one "key=value" line.
    func Parse(line string) (Setting, error) {
    	// split at the first equals sign
    	key, raw, _ := strings.Cut(line, "=")
    	val, err := strconv.Atoi(raw)
    	if err != nil {
    		return Setting{}, fmt.Errorf("parse %s: %v", key, err)
    	}
    	return Setting{Key: key, Value: val}, nil
    }

    func FirstLine(rd io.Reader) (string, error) {
    	line, err := bufio.NewReader(rd).ReadString('\\n')
    	if err != nil && err != io.EOF {
    		return "", fmt.Errorf("failed to read line: %w", err)
    	}
    	return strings.TrimSpace(line), nil
    }

    // String returns the setting in its "key=value" form.
    func (s Setting) String() string {
    	return s.Key + "=" + strconv.Itoa(s.Value)
    }
""")

SETTING_TEST = dedent("""
    package foo

    import (
    	"errors"
    	"strings"
    	"testing"
    	"testing/iotest"

    	"github.com/ctx42/testing/pkg/assert"
    )

    func Test_Parse(t *testing.T) {
    	t.Run("valid", func(t *testing.T) {
    		// --- Given ---
    		line := "a=1"

    		// --- When ---
    		have, err := Parse(line)

    		// --- Then ---
    		assert.NoError(t, err)
    		assert.Equal(t, Setting{Key: "a", Value: 1}, have)
    	})

    	t.Run("error - value not a number", func(t *testing.T) {
    		// --- Given ---
    		line := "a=x"

    		// --- When ---
    		have, err := Parse(line)

    		// --- Then ---
    		assert.ErrorContain(t, "invalid syntax", err)
    		assert.Zero(t, have)
    	})
    }

    func Test_FirstLine(t *testing.T) {
    	t.Run("line with newline", func(t *testing.T) {
    		// --- Given ---
    		rd := strings.NewReader("a=1\\nb=2\\n")

    		// --- When ---
    		have, err := FirstLine(rd)

    		// --- Then ---
    		assert.NoError(t, err)
    		assert.Equal(t, "a=1", have)
    	})

    	t.Run("last line without newline", func(t *testing.T) {
    		// --- Given ---
    		rd := strings.NewReader("a=1")

    		// --- When ---
    		have, err := FirstLine(rd)

    		// --- Then ---
    		assert.NoError(t, err)
    		assert.Equal(t, "a=1", have)
    	})

    	t.Run("error - reader fails", func(t *testing.T) {
    		// --- Given ---
    		rd := iotest.ErrReader(errors.New("disk gone"))

    		// --- When ---
    		have, err := FirstLine(rd)

    		// --- Then ---
    		assert.ErrorContain(t, "disk gone", err)
    		assert.Empty(t, have)
    	})
    }

    func Test_Setting_String(t *testing.T) {
    	// --- Given ---
    	set := Setting{Key: "a", Value: 1}

    	// --- When ---
    	have := set.String()

    	// --- Then ---
    	assert.Equal(t, "a=1", have)
    }
""")

n = "style--fix-applies-everything-behind-a-green-gate"
F = file_t("pkg/foo/foo.go")
case(n,
     prompt_md(n, PASS_TAGS + ["needs-shell"], "/go:style ./pkg/foo fix",
               max_turns=60,
               tools=PASS_TOOLS + ["Bash(go test:*)", "Bash(go:*)"]),
     {
         # Write or Edit, whichever the run edits with: no edit call
         # precedes the first `go test ... -race`.
         "b1-baseline-before-edit": g_regex(
             r'^(?:(?!"name":"(?:Edit|Write)")[\s\S])*?'
             r'"command":"(?:[^"\\]|\\.)*?go test(?:[^"\\]|\\.)*-race', "trace"),
         "b2-fix-wrap-v": g_regex(r"%v", F, "not_contains"),
         "b2-fix-failed-to": g_regex(r"[Ff]ailed to", F, "not_contains"),
         "b2-fix-error-equality": g_regex(r"err [!=]= io\.EOF", F,
                                          "not_contains"),
         "b2-fix-godoc": g_regex(r"// FirstLine [^\n]*\n(//[^\n]*\n)*func FirstLine\(", F),
         "b2-fix-receiver": g_regex(r"func \(s Setting\)", F, "not_contains"),
         "b2-fix-comment-sentence": g_regex(r"// split at the first equals sign\n",
                                            F, "not_contains"),
         "b2-gate-rerun": g_tool("Bash", 2, None, r"go test[^\"]*-race"),
         "b3-one-line-per-fix": g_regex(r"foo\.go:(Parse|FirstLine|String|Setting)"),
         "b3-gate-result": g_regex(
             r"(go test|gate|race)[^\n]*(pass|green|\bok\b)|"
             r"(pass|green|\bok\b)[^\n]*(go test|gate|race)", flags="i"),
         "b4-no-diff": g_regex(r"```diff|^@@|^[+-]\t", match="not_contains",
                               flags="m"),
         "b4-no-commit": g_never("Bash", r"git\s+commit"),
     },
     files={"go.mod": GOMOD_DEP.format(mod="foo"), "go.sum": GOSUM,
            "pkg/foo/foo.go": SETTING_GO,
            "pkg/foo/foo_test.go": SETTING_TEST})

# --------------------------------------------------------------------------
# Module of record packages.

def module_files(variants, mod="shop"):
    files = {"go.mod": GOMOD_DEP.format(mod=mod), "go.sum": GOSUM}
    for pkg, (src_kw, test_kw) in variants.items():
        files[f"internal/{pkg}/{pkg}.go"] = record_src(pkg, **src_kw)
        files[f"internal/{pkg}/{pkg}_test.go"] = record_test(pkg, **test_kw)
    return files


FOUR = dict(wrap_v=True, recv_r=True, pair_nodoc=True)
four_variants = {p: (FOUR, dict(given_blank=False)) for p in NATO}

# 12. fanout-opposing-fixes-kept-apart
clean = {}
fan12 = {}
for i, p in enumerate(NATO):
    if i < 4:
        fan12[p] = (clean, dict(given_blank=False))
    else:
        fan12[p] = (clean, dict(given_blank=True, then_surplus=True))
f12 = module_files(fan12)
ta = f12["internal/alpha/alpha_test.go"]
add_blank = line_of(ta, "assert.Equal(t, 3, have)") + 1
for p in NATO:
    tt = f12[f"internal/{p}/{p}_test.go"]
    assert line_of(tt, "assert.Equal(t, 3, have)") + 1 == add_blank, p

_ITEM = r"(?:^|\n)[ \t]*\**\d+\."


def _IN_ITEM_HAS(pat):
    """Lookahead: pat occurs before the next numbered item."""
    return r"(?=(?:(?!\n[ \t]*\**\d+\.)[\s\S])*?" + pat + ")"


# Within one finding: stop at another fix verb or the next numbered item.
_NO_VERB = r"(?:(?!\b(?:insert|add|delete|remove)\b|\n\s*\**\d+\.)[\s\S])*?"


def js_exact(text):
    """A JS regex matching exactly text, on one line."""
    out = []
    for ch in text:
        if ch == "\n":
            out.append("\\n")
        elif ch == "\t":
            out.append("\\t")
        elif ch in "\\^$.*+?()[]{}|/":
            out.append("\\" + ch)
        else:
            out.append(ch)
    return "^" + "".join(out) + "$"


# 12 (after the pick): every site gets its own direction, nothing else moves.
APPLY_ALL = ENGLISH + "\n" + (
    "Automated eval: the user is absent. Whenever the skill would stop and "
    "wait\nfor the user, take the next scripted answer below as the reply and "
    "continue\nin this same run; never end the run to wait. If none fits, give "
    "the most\nplausible answer and continue.\n\n"
    "1. Apply all of them. If the go test gate cannot run here, apply them\n"
    "   anyway; I will run the tests myself.")
graders12 = {}
for p in NATO:
    graders12[f"b7-{p}-test-fixed"] = g_regex(
        js_exact(record_test(p)), file_t(f"internal/{p}/{p}_test.go"))
    graders12[f"b7-{p}-source-unchanged"] = g_regex(
        js_exact(record_src(p)), file_t(f"internal/{p}/{p}.go"))
n = "style--fanout-opposing-fixes-kept-apart"
case(n,
     prompt_md(n, PASS_TAGS + ["needs-shell"],
               "/go:style ./... max_issues=25 depth=standard",
               max_turns=80, timeout=600,
               tools=FAN_TOOLS + ["Bash(go test:*)"], asp=APPLY_ALL),
     graders12,
     files=f12)

# --------------------------------------------------------------------------

def write_case(name, c):
    d = os.path.join(EVALS, name)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, "graders"))
    with open(os.path.join(d, "prompt.md"), "w") as f:
        f.write(c["prompt"])
    for gname, body in c["graders"].items():
        with open(os.path.join(d, "graders", gname + ".md"), "w") as f:
            f.write(body)
    if c["files"]:
        with open(os.path.join(d, "case.yaml"), "w") as f:
            f.write(f'schema_version: "1.1"\nname: {name}\ncontext:\n'
                    "  scaffold_script: scaffold.sh\n")
        p = os.path.join(d, "scaffold.sh")
        with open(p, "w") as f:
            f.write(scaffold_sh(c["files"], c["extra"]))
        os.chmod(p, 0o755)


def check(base):
    def width(line):
        col = 0
        for ch in line:
            col = (col // 4 + 1) * 4 if ch == "\t" else col + 1
        return col
    for name, c in CASES.items():
        if not c["files"]:
            continue
        d = os.path.join(base, name)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        subprocess.run(["bash", os.path.join(EVALS, name, "scaffold.sh")],
                       cwd=d, check=True)
        limit = 72 if ".editorconfig" in c["files"] else 80
        for p, content in c["files"].items():
            if p.endswith(".go"):
                for i, ln in enumerate(content.split("\n"), 1):
                    if width(ln) > limit:
                        print(f"WIDTH {name} {p}:{i} {width(ln)}")
        env = dict(os.environ, GOFLAGS="-mod=mod", GOPROXY="off")
        r = subprocess.run(["go", "vet", "./..."], cwd=d, env=env,
                           capture_output=True, text=True)
        fmt = subprocess.run(["gofmt", "-l", "."], cwd=d,
                             capture_output=True, text=True)
        t = subprocess.run(["go", "test", "./..."], cwd=d, env=env,
                           capture_output=True, text=True)
        print(f"{name}: vet={r.returncode} gofmt={fmt.stdout.strip() or 'ok'}"
              f" test={t.returncode}")
        if r.returncode:
            print(r.stderr[:1500])
        if t.returncode:
            print(t.stdout[-1500:], t.stderr[-800:])


if __name__ == "__main__":
    for name, c in CASES.items():
        write_case(name, c)
    print("wrote", len(CASES), "cases")
    if len(sys.argv) == 3 and sys.argv[1] == "--check":
        check(sys.argv[2])
