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
NOTICE = ("Ignore any trailing notice about a company directive "
          "(«Nutzung von Claude und andere AI-Agents»). ")

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


# Runs have Bash: a file read may be Read or a shell cat/sed.
READ_ANY = r'"name":"(?:Read|Bash)","input":\{"(?:file_path|command)":"(?:[^"\\]|\\.)*?'
CMD_RE = r'"command":"(?:[^"\\]|\\.)*?'
SHELL_READ_RE = r'(?:\b|\\n)(?:cat|sed|head|tail|less|awk)\b(?:[^"\\|;&]|\\.)*?'


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


def g_order(before, after):
    def side(x):
        tool, im = x
        if im is None:
            return "{tool: " + tool + "}"
        return "{tool: " + tool + ", input_match: '" + \
            im.replace("'", "''") + "'}"
    return ("---\ntype: tool_order\n"
            f"before: {side(before)}\nafter: {side(after)}\n---\n")


def g_llm(claim, focus=None):
    fm = ["type: llm"]
    if focus:
        fm.append("focus: {source: file, path: " + focus + "}")
    return "---\n" + "\n".join(fm) + "\n---\n" + claim + "\n"


def width_pattern(limit, tab=4, max_tabs=6):
    alts = [f"^\\t{{{k}}}[^\\t\\n]{{{limit - tab * k + 1},}}$"
            for k in range(max_tabs + 1)]
    return "|".join(alts)


CASES = {}


def tool_in(names):
    """Trace regex prefix: inside a string field of a names tool_use input."""
    return (r'"name":"(?:' + names + r')","input":\{'
            r'(?:"[^"]*":(?:"(?:[^"\\]|\\.)*"|[^,}"]*),)*'
            r'"[^"]*":"(?:[^"\\]|\\.)*?')


def backticked_variant(canon, stems):
    """A backticked hyphenated id about stems that is not one of canon."""
    return (r"`(?!(?:" + "|".join(canon) + r")`)"
            r"(?=[a-z0-9-]*(?:" + stems + r"))[a-z0-9]+(?:-[a-z0-9]+)+`")


GO_WRITE = r'"file_path":"[^"]*\.go"'
RECHECK = (r"re-?check|search|grep|diffed|checked[^\n]{0,80}(against|in) the (source|code)|"
           r"against the source|trigger appears|appears (nowhere|at all|in all)")


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
# 2. test-rules-inherit-production

SERVICE_GO_CLOSE = SERVICE_GO.replace("import \"io\"", dedent("""
    import (
    	"fmt"
    	"io"
    )""").strip()) + "\n" + dedent("""
    // Close closes the store, then the audit log.
    func (svc *Service) Close() error {
    	if err := svc.store.Close(); err != nil {
    		return fmt.Errorf("close store: %w", err)
    	}
    	if err := svc.audit.Close(); err != nil {
    		return fmt.Errorf("close audit: %w", err)
    	}
    	return nil
    }
""")

WRITTEN = r'"(?:content|new_string)":"(?:[^"\\]|\\.)*?'
n = "style--test-rules-inherit-production"
case(n,
     prompt_md(n, ["skill:style", "sec:style:production", "sec:style:test",
                   "sec:style:self-learning"],
               "Write tests for Service.Close in service_test.go",
               max_turns=40, tools=["Read", "Glob", "Grep", "Skill", "LSP",
                                    "Write", "Edit"],
               asp=ENGLISH + "\n" + LOAD_STYLE + "\n"
               "Earlier in this session you added Service.Close. The user "
               "wants the\ntests to include a table test and a small test "
               "helper, and the helper\nitself tested too."),
     {
         "b1-tab-indented": g_regex(r"^ +\S", file_t("service_test.go"),
                                    "not_contains", "m"),
         "b1-within-resolved-limit": g_regex(width_pattern(72),
                                             file_t("service_test.go"),
                                             "not_contains", "m"),
         "b1-no-got": g_regex(r"\bgot\b", file_t("service_test.go"),
                              "not_contains"),
         "b2-test-name": g_regex(r"func Test_Service_Close(_\w+)?\(",
                                 file_t("service_test.go")),
         "b2-tabular-suffix": g_regex(r"func Test_Service_Close\w*_tabular\(",
                                      file_t("service_test.go")),
         "b2-t-run": g_regex(r"t\.Run\(", file_t("service_test.go")),
         # Inside a Write/Edit payload, wherever the helper lands.
         "b3-t-helper": g_regex(WRITTEN + r"\\tt\.Helper\(\)", "trace"),
         "b3-helper-takes-tester-t": g_regex(
             WRITTEN + r"func \w+\((\\n\\t)?t tester\.T\b", "trace"),
         "b3-spy-tests-helper": g_regex(
             WRITTEN + r"tester\.(New\(|Spy\b)", "trace"),
         "b4-subtest-names-charset": g_llm(
             "Every subtest name in this Go test file (each string literal "
             "passed to t.Run, and each table-row name field that is passed "
             "to t.Run) uses only letters, digits, spaces, underscores and "
             "hyphens, and none contains a slash.",
             focus="service_test.go"),
     },
     files={".editorconfig": EDITORCONFIG_72,
            "go.mod": GOMOD_DEP.format(mod="svc"), "go.sum": GOSUM,
            "service.go": SERVICE_GO_CLOSE})

# --------------------------------------------------------------------------
# 3. pass-lists-offenses-then-asks

COUNTER_GO = dedent("""
    // Package foo keeps running totals of integer samples.
    package foo

    import "fmt"

    var _ fmt.Stringer = (*Counter)(nil)

    // Counter sums the samples added to it.
    type Counter struct {
    	samples []int
    }

    // Add appends n to the samples.
    func (c *Counter) Add(n int) {
    	c.samples = append(c.samples, n)
    }

    // Sum returns the total of the first k samples.
    func (c *Counter) Sum(k int) int {
    	total := 0
    	for i := 0; i <= k; i++ {
    		total += c.samples[i]
    	}
    	return total
    }

    // String returns a string representation of the value. It is the
    // method the fmt.Stringer interface requires, used by fmt to print
    // the value.
    func (c *Counter) String() string {
    	return fmt.Sprintf("Counter(%d samples)", len(c.samples))
    }
""")

FIRST_LINE = r"^(?=[^\n]*foo\.go)(?=[^\n]*\b80\b)(?=[^\n]*\btab\b)"

n = "style--pass-lists-offenses-then-asks"
case(n,
     prompt_md(n, PASS_TAGS, "/go:style ./pkg/foo"),
     {
         # Read, or a shell read (runs have Bash).
         "b1-reads-checking": g_regex(READ_ANY + r"checking\.md", "trace"),
         "b1-first-line-target-and-settings": g_regex(FIRST_LINE),
         "b2-no-formatter-or-linter": g_never(
             "Bash", r"gofmt|goimports|go vet|golangci|staticcheck"),
         "b3-rules-never-read-whole": g_never("Read", r'rules\.md"\s*\}'),
         "b3-rules-never-cat-whole": g_never(
             "Bash", CMD_RE + r'(?:\b|\\n)cat\s(?:[^"\\|;&]|\\.)*?rules\.md'),
         "b3-rules-never-catted": g_never(
             "Bash", CMD_RE + r'(?:\b|\\n)(less|head)\s(?:[^"\\|;&]|\\.)*?rules\.md'),
         "b4-off-by-one-not-reported": g_regex(
             # Only as a finding: a closing hand-off to go:review is allowed.
             r"^\s*\d+\.[^\n]*(foo\.go:2[12]\b|<= k|off-by-one)",
             match="not_contains", flags="mi"),
         "b5-file-line": g_regex(r"foo\.go:\d+"),
         "b5-rule-id": g_regex(r"receivers-three-letter-type"),
         "b5-severity-groups": g_regex(r"^(?=[\s\S]*Should-fix)(?=[\s\S]*\bNit)"),
         "b5-verdict": g_regex(r"fix[- ]first|\bclean\b", flags="i"),
         "b5-counts": g_regex(
             r"\d+\s*(Blockers?|Should-fix|Nits?)\b|"
             r"(Blockers?|Should-fix|Nits?)\W{0,3}\d+", flags="i"),
         "b6-asks-which": g_regex(
             r"which[^\n]{0,80}(apply|fix)|(apply|fix)[^\n]{0,80}\?",
             flags="i"),
         "b6-no-edit": g_never("Edit"),
         "b6-no-write": g_never("Write"),
     },
     files={"go.mod": GOMOD_NODEP.format(mod="foo"),
            "pkg/foo/foo.go": COUNTER_GO})

# --------------------------------------------------------------------------
# 4. fix-applies-everything-behind-a-green-gate  (and 8. terse-output)

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
# 5. delegated-by-review

STORE_GO = dedent("""
    // Package store keeps named counters in memory.
    package store

    // Store holds counters by name.
    type Store struct {
    	counts map[string]int
    }

    // New returns an empty Store.
    func New() *Store {
    	return &Store{counts: map[string]int{}}
    }

    // Inc adds one to the counter called name.
    func (sto *Store) Inc(name string) {
    	sto.counts[name]++
    }
""")
STORE_TEST = dedent("""
    package store

    import (
    	"testing"

    	"github.com/ctx42/testing/pkg/assert"
    )

    func Test_Store_Inc(t *testing.T) {
    	// --- Given ---
    	sto := New()

    	name := "a"

    	// --- When ---
    	sto.Inc(name)

    	// --- Then ---
    	assert.Equal(t, 1, sto.counts["a"])
    }
""")
STORE_DIFF = dedent("""

    // Total returns the sum of the counters named in names.
    func (s *Store) Total(names []string) int {
    	total := 0
    	for i := 1; i < len(names); i++ {
    		total += s.counts[names[i]]
    	}
    	return total
    }
""")
GIT_SETUP = dedent("""
    git init -q -b main
    git add -A
    git -c user.name=eval -c user.email=eval@example.com commit -qm init
    cat >> pkg/store/store.go <<'EOF_DIFF'
""") + "\n" + STORE_DIFF.rstrip("\n") + "\nEOF_DIFF\n"

n = "style--delegated-by-review"
case(n,
     prompt_md(n, ["skill:style", "skill:review", "sec:style:usage",
                   "sec:style:production", "sec:style:test",
                   "sec:style:self-learning", "ref:style/checking",
                   "sec:review:working-diff-injected", "sec:review:check-mode",
                   "sec:review:self-learning", "needs-shell"],
               "/go:review", max_turns=50,
               tools=PASS_TOOLS + ["Bash(git:*)"]),
     {
         "b1-style-invoked": g_tool("Skill", 1, None, r"style"),
         "b1-no-edit": g_never("Edit"),
         "b1-no-write": g_never("Write"),
         "b1-no-pick-step": g_regex(
             r"which (of (these|the) )?(style )?offen[cs]es", match="not_contains",
             flags="i"),
         "b2-style-offense-merged": g_regex(
             r"receivers-three-letter-type|receiver[^\n]{0,80}`s`|"
             r"`s`[^\n]{0,80}receiver", flags="i"),
         "b2-correctness-alongside": g_regex(
             r"^(?=[\s\S]*correctness)(?=[\s\S]*(i := 1|first name|names\[0\]|skips))",
             flags="i"),
     },
     files={"go.mod": GOMOD_DEP.format(mod="store"), "go.sum": GOSUM,
            "pkg/store/store.go": STORE_GO,
            "pkg/store/store_test.go": STORE_TEST},
     extra=GIT_SETUP)

# --------------------------------------------------------------------------
# 6. rules-change-only-through-review

n = "style--rules-change-only-through-review"
case(n,
     prompt_md(n, ["skill:style", "sec:style:usage", "ref:style/checking",
                   "sec:style:self-learning"],
               "/go:style add a rule that test helpers never return errors",
               max_turns=20),
     {
         "b1-no-edit": g_never("Edit"),
         "b1-no-write": g_never("Write"),
         # Named in the reply, or run: a go:review call carrying the rule.
         "b2-names-review-add": g_regex(
             r'review add\b[^\n"]*helpers?[^\n"]*errors?|'
             r'"skill":"(go:)?review","args":"add\b[^"]*helpers?[^"]*errors?',
             "trace"),
     })

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

# 7. broad-target-auto-plan-first
IDS = ["wrap-errors-w", "receivers-three-letter-type", "every-exported-symbol",
       "separate-distinct-topics"]
n = "style--broad-target-auto-plan-first"
case(n,
     prompt_md(n, PASS_TAGS, "/go:style ./...", max_turns=30,
               tools=FAN_TOOLS),
     {
         "b1-no-fanout-agent": g_never("Agent"),
         "b1-no-fanout-task": g_never("Task"),
         "b2-max-issues-default": g_regex(r"(max_issues|cap)\D{0,12}25",
                                          flags="i"),
         "b2-depth-default": g_regex(r"depth\W{0,12}standard", flags="i"),
         "b2-packages-listed": g_regex(
             "^" + "".join(f"(?=[\\s\\S]*\\b{p}\\b)" for p in NATO)),
         "b3-no-go-file-read": g_never("Read", r'\.go"'),
         "b3-no-go-file-shell-read": g_never("Bash", CMD_RE + SHELL_READ_RE + r"\w\.go(?![\w.])"),
         "b3-no-findings": g_regex(
             "|".join(IDS) + r"|\.go:\d+", match="not_contains"),
         "b3-no-edit": g_never("Edit"),
         "b3-no-write": g_never("Write"),
     },
     files=module_files(four_variants))

# 10. severity-and-ids-are-stable
two_variants = {p: (dict(recv_r=True, pair_nodoc=True), {})
                for p in NATO[:3]}
VARIANT_ID = (r"(?<![\w-])(?!receivers-three-letter-type\b|every-exported-symbol\b)"
              r"(?=[a-z0-9-]*(receiver|godoc|doc))[a-z0-9]+(?:-[a-z0-9]+)+\b")
n = "style--severity-and-ids-are-stable"
case(n,
     prompt_md(n, PASS_TAGS, "/go:style ./...", max_turns=40),
     {
         # An id seen on both sides of a severity heading line.
         "b1-same-severity-everywhere": g_regex(
             r"(every-exported-symbol|receivers-three-letter-type)[\s\S]*"
             r"^\W*(Blocker|Should-fix|Nit)s?\W*$[\s\S]*\1",
             match="not_contains", flags="m"),
         "b2-godoc-id": g_regex(r"every-exported-symbol"),
         "b2-receiver-id": g_regex(r"receivers-three-letter-type"),
         "b2-no-variant-id": g_regex(
             backticked_variant(["receivers-three-letter-type",
                                 "every-exported-symbol"],
                                "receiver|godoc|doc"),
             match="not_contains"),
         "b3-godoc-blocker-receiver-should-fix": g_regex(
             r"Blocker[\s\S]*every-exported-symbol[\s\S]*Should-fix[\s\S]*"
             r"receivers-three-letter-type"),
         "b3-receiver-never-blocker": g_regex(
             r"receivers-three-letter-type[^\n]*Blocker|"
             r"Blocker[^\n]*receivers-three-letter-type",
             match="not_contains"),
     },
     files=module_files(two_variants))

# 11. fanout-folds-then-caps
fan11 = dict(four_variants)
fan11["bravo"] = (dict(FOUR, failed_to=True, ticket=True),
                  dict(given_blank=False, got=True))
fan11["foxtrot"] = (dict(FOUR, add_doc_rec=True),
                    dict(given_blank=False, swap_order=True,
                         bad_subtest=True))
f11 = module_files(fan11)
t11 = f11["internal/alpha/alpha_test.go"]
noerr = [line_of(t11, "assert.NoError(t, err)", 1),
         line_of(t11, "assert.NoError(t, err)", 2)]
for p in NATO:
    tt = f11[f"internal/{p}/{p}_test.go"]
    assert [line_of(tt, "assert.NoError(t, err)", 1),
            line_of(tt, "assert.NoError(t, err)", 2)] == noerr, p
NOERR_RE = "_test\\.go:(" + "|".join(
    str(x) for x in noerr + [x + 1 for x in noerr]) + ")\\b"

_IN_ITEM = r"(?:(?!^\s*\d+\.)[\s\S])*?"
NO_MIXED_FINDING = (r"^\s*\d+\." + _IN_ITEM + r"(?:insert[^\n]*blank line" +
                    _IN_ITEM + r"delete[^\n]*blank line|delete[^\n]*blank line"
                    + _IN_ITEM + r"insert[^\n]*blank line)")
ALL8 = ",".join(NATO)
n = "style--fanout-folds-then-caps"
case(n,
     prompt_md(n, PASS_TAGS, "/go:style ./... max_issues=25 depth=standard",
               max_turns=80, timeout=600, tools=FAN_TOOLS),
     {
         "b1-no-plan-stop": g_regex(r"wrap-errors-w"),
         "b2-one-worker-per-package": g_tool("Agent", 8, None),
         "b2-pinned-rule-set": g_tool("Agent", 8, None,
                                      r"separate-distinct-topics"),
         "b3-no-cap-share": g_never(
             "Agent", r"max_issues\s*[=:]\s*\d|(at most|up to|no more than) \d+ (offen|finding)"),
         "b4-godoc-folded": g_regex(
             r"every-exported-symbol[\s\S]{0,300}?"
             r"(\b8\b|eight|all (\w+ )?packages|every package|"
             r"\{alpha,(bravo,charlie,delta,echo,foxtrot,golf,|…,)hotel\})",
             flags="i"),
         "b5-nothing-unreported": g_regex(
             r"\b0\b[^\n]{0,30}unreported|unreported[^\n]{0,30}\b0\b|"
             r"(none|nothing|no offen[cs]es?)[^\n]{0,30}(unreported|cut|dropped|left out)",
             flags="i"),
         "b6-no-variant-id": g_regex(
             backticked_variant(IDS, "receiver|exported|topic|blank"),
             match="not_contains"),
         "b6-no-reconcile-note": g_regex(
             r"reconcil\w*[^\n]{0,40}(spelling|\bids?\b|severit)",
             match="not_contains", flags="i"),
         "b7-raw-total": g_regex(r"\b38\b"),
         "b8-asks-which": g_regex(
             r"which[^\n]{0,80}(apply|fix)|(apply|fix)[^\n]{0,80}\?",
             flags="i"),
         "b8-no-edit": g_never("Edit"),
         "b8-no-write": g_never("Write", GO_WRITE),
         "b9-four-ids": g_regex("^" + "".join(f"(?=[\\s\\S]*{i})" for i in IDS)),
         # The pinned id list rides in a worker brief or a file it names.
         "b9-negation-kept": g_regex(
             tool_in("Agent|Task|Write|Bash") + r"no-work-init", "trace"),
         "b9-negation-not-dropped": g_regex(
             tool_in("Agent|Task|Write|Bash") + r"(?<!no-)\bwork-init", "trace",
             "not_contains"),
         "b9-dotted-prefix-only": g_regex(
             tool_in("Agent|Task|Write|Bash") +
             r"match-errors-(is|as|errorsis|errorsas)\b", "trace",
             "not_contains"),
         "b10-identical-graded-identically": g_regex(
             "^" + "".join(
                 f"(?=[\\s\\S]*{i}[^\\n]*\\n?[^\\n]*(\\b8\\b|eight|all|every|{ALL8}))"
                 for i in IDS), flags="i"),
         "b11-recheck-shown": g_regex(RECHECK, flags="i"),
         "b12-no-insert-and-delete": g_regex(NO_MIXED_FINDING,
                                             match="not_contains",
                                             flags="mi"),
         "b13-no-flag-on-one-subject": g_regex(NOERR_RE, match="not_contains"),
         "b14-triggers-quoted": g_regex(
             r"^\s*\d+\.\s[^`\n]*$", match="not_contains", flags="m"),
     },
     files=f11)

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
ADD_RE = "_test\\.go:(" + "|".join(
    str(x) for x in (add_blank - 1, add_blank, add_blank + 1)) + ")\\b"

_ITEM = r"(?:^|\n)[ \t]*\**\d+\."


def _IN_ITEM_HAS(pat):
    """Lookahead: pat occurs before the next numbered item."""
    return r"(?=(?:(?!\n[ \t]*\**\d+\.)[\s\S])*?" + pat + ")"


# Within one finding: stop at another fix verb or the next numbered item.
_NO_VERB = r"(?:(?!\b(?:insert|add|delete|remove)\b|\n\s*\**\d+\.)[\s\S])*?"
n = "style--fanout-opposing-fixes-kept-apart--gate"
case(n,
     prompt_md(n, PASS_TAGS, "/go:style ./... max_issues=25 depth=standard",
               max_turns=80, timeout=600, tools=FAN_TOOLS),
     {
         "b1-one-worker-per-package": g_tool("Agent", 8, None),
         # Each brief carries the id list or names the file holding it.
         "b1-brief-pins-rules": g_tool(
             "Agent", 8, None, r"separate-distinct-topics|/tmp/[^\"]*\.md"),
         "b1-pinned-rule-set": g_regex(
             tool_in("Agent|Task|Write|Bash") + r"separate-distinct-topics",
             "trace"),
         "b2-one-id-all-packages": g_regex(
             "^(?=[\\s\\S]*separate-distinct-topics)" +
             "".join(f"(?=[\\s\\S]*\\b{p}\\b)" for p in NATO)),
         "b2-no-variant-id": g_regex(
             backticked_variant(["separate-distinct-topics"], "topic|blank"),
             match="not_contains"),
         "b3-both-directions": g_regex(
             r"^(?=[\s\S]*\b(insert|add)\b)(?=[\s\S]*\b(delete|remove)\b)",
             flags="i"),
         # The verb nearest before each site is that site's own direction.
         # Within one numbered finding, in either order: a delete aimed at
         # alpha-delta, or an insert aimed at echo-hotel.
         "b3-each-site-own-fix": g_regex(
             _ITEM + r"(?:" + _IN_ITEM_HAS(r"\b(delete|remove)\b")
             + _IN_ITEM_HAS(r"\b(alpha|bravo|charlie|delta)_test\.go") + r"|"
             + _IN_ITEM_HAS(r"\b(insert|add)\b")
             + _IN_ITEM_HAS(r"\b(echo|foxtrot|golf|hotel)_test\.go") + r")",
             match="not_contains", flags="i"),
         "b4-recheck-shown": g_regex(RECHECK, flags="i"),
         "b5-no-flag-at-correct-blank": g_regex(ADD_RE, match="not_contains"),
         # A "Fix:" label or a bold fix heading opening with another verb.
         "b6-fix-opens-with-verb": g_regex(
             r"^\s*(?:[-*]\s+)?\**fix(?:es)?\**:\**\s*\**`?(?!(?:insert|delete|rename|move|"
             r"replace|reword)\b)[a-z]|^\s*(?:\d+\.|-)\s*\*\*(?:add|remove|"
             r"change|put|drop)\b", match="not_contains", flags="mi"),
         "b7-no-edit": g_never("Edit"),
         "b7-no-write": g_never("Write", GO_WRITE),
     },
     files=f12)


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
# 8. terse-output (reuses the six-offense package of case 4)

wrap_line = line_of(SETTING_GO, '%v", key, err)')
eof_line = line_of(SETTING_GO, "err != io.EOF")
recv_line = line_of(SETTING_GO, "func (s Setting)")
n = "style--terse-output"
case(n,
     prompt_md(n, PASS_TAGS, "/go:style ./pkg/foo"),
     {
         "b1-first-line-target-and-settings": g_regex(FIRST_LINE),
         "b2-no-narration": g_regex(
             r"^\W*(I'll|I will|Let me|I read|I've read|I have read|Reading|"
             r"First,|Now,? I|Next,? I|Checking)",
             match="not_contains", flags="m"),
         "b2-no-invocation-restated": g_regex(
             r"as requested|you asked|you ran|you invoked|your (request|invocation)",
             match="not_contains", flags="i"),
         "b3-wrap-stated-once": g_regex(f"foo\\.go:{wrap_line}\\b",
                                        match="count:1"),
         "b3-eof-stated-once": g_regex(f"foo\\.go:{eof_line}\\b",
                                       match="count:1"),
         "b3-receiver-stated-once": g_regex(f"foo\\.go:{recv_line}\\b",
                                            match="count:1"),
         # After the verdict, no site or rule id comes back; no Summary.
         "b4-no-closing-recap": g_regex(
             r"[Vv]erdict[\s\S]*(foo(_test)?\.go:\d+|`[a-z0-9]+(-[a-z0-9]+){2,}`)"
             r"|^\W*(Summary|Recap)\b", match="not_contains", flags="m"),
     },
     files={"go.mod": GOMOD_DEP.format(mod="foo"), "go.sum": GOSUM,
            "pkg/foo/foo.go": SETTING_GO,
            "pkg/foo/foo_test.go": SETTING_TEST})

# --------------------------------------------------------------------------
# 9. incidental-interface-satisfaction

NET_GO = dedent("""
    // Package net wraps byte streams with connection and buffer
    // bookkeeping.
    package net
""")
CONN_GO = dedent("""
    package net

    import (
    	"fmt"
    	"io"
    )

    var _ io.Closer = (*Conn)(nil)

    // Conn is a connection over an underlying stream.
    type Conn struct {
    	rwc io.ReadWriteCloser
    }

    // NewConn returns a Conn over rwc.
    func NewConn(rwc io.ReadWriteCloser) *Conn {
    	return &Conn{rwc: rwc}
    }

    // Close implements io.Closer. The behavior of Close after the first
    // call is undefined. Specific implementations may document their own
    // behavior.
    func (con *Conn) Close() error {
    	if err := con.rwc.Close(); err != nil {
    		return fmt.Errorf("close conn: %w", err)
    	}
    	return nil
    }
""")
BUFFER_GO = dedent("""
    package net

    import "strings"

    // Buffer collects text until it is closed.
    type Buffer struct {
    	parts  []string
    	closed bool
    }

    // Append adds s to the buffer and reports whether it was added; a
    // closed buffer drops s.
    func (buf *Buffer) Append(s string) bool {
    	if buf.closed {
    		return false
    	}
    	buf.parts = append(buf.parts, s)
    	return true
    }

    // Close marks the buffer closed, so later appends are dropped. It
    // always returns nil.
    func (buf *Buffer) Close() error {
    	buf.closed = true
    	return nil
    }

    // String returns the appended text joined in order.
    func (buf *Buffer) String() string {
    	return strings.Join(buf.parts, "")
    }
""")
ALL_TEST = dedent("""
    package net

    import "io"

    // stream is an io.ReadWriteCloser whose Close returns err.
    type stream struct {
    	io.ReadWriter
    	err error
    }

    // Close returns the stream's err.
    func (stm *stream) Close() error {
    	return stm.err
    }
""")
CONN_TEST = dedent("""
    package net

    import (
    	"errors"
    	"testing"

    	"github.com/ctx42/testing/pkg/assert"
    )

    func Test_NewConn(t *testing.T) {
    	// --- Given ---
    	stm := &stream{}

    	// --- When ---
    	have := NewConn(stm)

    	// --- Then ---
    	assert.Same(t, stm, have.rwc)
    }

    func Test_Conn_Close(t *testing.T) {
    	t.Run("closes stream", func(t *testing.T) {
    		// --- Given ---
    		con := NewConn(&stream{})

    		// --- When ---
    		err := con.Close()

    		// --- Then ---
    		assert.NoError(t, err)
    	})

    	t.Run("error - stream close fails", func(t *testing.T) {
    		// --- Given ---
    		cause := errors.New("pipe broken")

    		con := NewConn(&stream{err: cause})

    		// --- When ---
    		err := con.Close()

    		// --- Then ---
    		assert.ErrorIs(t, cause, err)
    	})
    }
""")
BUFFER_TEST = dedent("""
    package net

    import (
    	"testing"

    	"github.com/ctx42/testing/pkg/assert"
    )

    func Test_Buffer_Append(t *testing.T) {
    	t.Run("open buffer", func(t *testing.T) {
    		// --- Given ---
    		buf := &Buffer{}

    		s := "abc"

    		// --- When ---
    		have := buf.Append(s)

    		// --- Then ---
    		assert.True(t, have)

    		assert.Equal(t, "abc", buf.String())
    	})

    	t.Run("closed buffer", func(t *testing.T) {
    		// --- Given ---
    		buf := &Buffer{closed: true}

    		s := "abc"

    		// --- When ---
    		have := buf.Append(s)

    		// --- Then ---
    		assert.False(t, have)

    		assert.Empty(t, buf.String())
    	})
    }

    func Test_Buffer_Close(t *testing.T) {
    	// --- Given ---
    	buf := &Buffer{}

    	// --- When ---
    	err := buf.Close()

    	// --- Then ---
    	assert.NoError(t, err)

    	assert.True(t, buf.closed)
    }

    func Test_Buffer_String(t *testing.T) {
    	// --- Given ---
    	buf := &Buffer{parts: []string{"ab", "c"}}

    	// --- When ---
    	have := buf.String()

    	// --- Then ---
    	assert.Equal(t, "abc", have)
    }
""")

n = "style--incidental-interface-satisfaction"
case(n,
     prompt_md(n, PASS_TAGS, "/go:style ./pkg/net"),
     {
         "b1-conn-close-flagged": g_regex(
             r"conn\.go:\d+[\s\S]{0,400}Close|Close[\s\S]{0,400}conn\.go:\d+"),
         "b2-buffer-left-alone": g_regex(r"buffer\.go:\d+",
                                         match="not_contains"),
         "b3-no-finding-names-buffer": g_regex(
             r"^\s*\d+\.[^\n]*(Buffer|buffer\.go)", match="not_contains",
             flags="m"),
         "b3-no-edit": g_never("Edit"),
     },
     files={"go.mod": GOMOD_DEP.format(mod="netx"), "go.sum": GOSUM,
            "pkg/net/net.go": NET_GO, "pkg/net/conn.go": CONN_GO,
            "pkg/net/buffer.go": BUFFER_GO,
            "pkg/net/all_test.go": ALL_TEST,
            "pkg/net/conn_test.go": CONN_TEST,
            "pkg/net/buffer_test.go": BUFFER_TEST})


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
