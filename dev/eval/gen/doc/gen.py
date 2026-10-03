#!/usr/bin/env python3
"""Generate go/evals/doc--* native eval cases from the doc skill's scenarios."""
import os
import shutil
import textwrap

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../go/evals"))

BASE_TAGS = [
    "skill:doc", "sec:doc:usage", "sec:doc:target", "sec:doc:the-checklist",
    "sec:doc:accuracy", "sec:doc:per-item-loop", "sec:doc:output",
    "sec:style:production",
]
SHELL_TOOLS = ["Bash(go:*)", "Bash(gofmt:*)"]
BASE_TOOLS = ["Read", "Glob", "Grep", "Skill", "Write", "Edit", "LSP"]
ENGLISH = "The user writes English; reply in English."
WIRING = (
    "Automated eval: the user is absent. Whenever the skill would stop and wait\n"
    "for the user, take the next scripted answer below as the reply and continue\n"
    "in this same run; never end the run to wait. If none fits, give the most\n"
    "plausible answer and continue."
)


def esc(s):
    """Escape literal text for a one-line JS regex."""
    out = []
    for ch in s:
        if ch in "\\^$.|?*+()[]{}/":
            out.append("\\" + ch)
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\t":
            out.append("\\t")
        else:
            out.append(ch)
    return "".join(out)


def gomod(mod):
    return {"go.mod": f"module {mod}\n\ngo 1.22\n"}


def write_case(name, query, files, graders, tags_extra=(), shell=True,
               agent=False, answers=None, max_turns=40, timeout=300):
    d = os.path.join(ROOT, name)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, "graders"))
    tags = [f"case:{name}"] + BASE_TAGS + list(tags_extra)
    if shell:
        tags.append("needs-shell")
    tools = list(BASE_TOOLS) + (["Agent"] if agent else []) + SHELL_TOOLS
    asp = ENGLISH
    if answers:
        asp += "\n" + WIRING + "\n\n" + "\n".join(
            f"{i}. {a}" for i, a in enumerate(answers, 1))
    asp_block = textwrap.indent(asp, "  ")
    with open(os.path.join(d, "prompt.md"), "w") as f:
        f.write("---\n")
        f.write(f"tags: [{', '.join(tags)}]\n")
        f.write("runs: 1\n")
        f.write(f"max_turns: {max_turns}\n")
        f.write(f"timeout_seconds: {timeout}\n")
        f.write(f"allowed_tools: [{', '.join(tools)}]\n")
        f.write(f"append_system_prompt: |\n{asp_block}\n")
        f.write("---\n\n")
        f.write(query + "\n")
    with open(os.path.join(d, "case.yaml"), "w") as f:
        f.write(f'schema_version: "1.1"\nname: {name}\ncontext:\n'
                f"  scaffold_script: scaffold.sh\n")
    with open(os.path.join(d, "scaffold.sh"), "w") as f:
        f.write("#!/usr/bin/env bash\nset -euo pipefail\n")
        dirs = sorted({os.path.dirname(p) for p in files if os.path.dirname(p)})
        for i, (path, body) in enumerate(files.items()):
            dn = os.path.dirname(path)
            if dn:
                f.write(f"mkdir -p {dn}\n")
            f.write(f"cat > {path} <<'EOF_{i}'\n{body}EOF_{i}\n")
    os.chmod(os.path.join(d, "scaffold.sh"), 0o755)
    for gname, gbody in graders.items():
        with open(os.path.join(d, "graders", gname + ".md"), "w") as f:
            f.write(gbody)


def rx(target, pattern, flags=None, negate=False):
    t = target if target in ("last_message", "trace") else \
        f"{{source: file, path: {target}}}"
    s = f"---\ntype: regex\ntarget: {t}\n"
    if negate:
        s += 'match: "not_contains"\n'
    if flags:
        s += f'flags: "{flags}"\n'
    return s + f"---\n{pattern}\n"


def used(tool, mn, mx=None, match=None):
    s = f"---\ntype: tool_used\ntool: {tool}\n"
    if match:
        s += f"input_match: '{match}'\n"
    s += f"min: {mn}\n"
    if mx is not None:
        s += f"max: {mx}\n"
    if mx == 0:
        s += "arm: both\n"
    return s + "---\n"


def order(before, after, after_match=None):
    a = f"{{tool: {after}" + (f", input_match: '{after_match}'" if after_match else "") + "}"
    return f"---\ntype: tool_order\nbefore: {{tool: {before}}}\nafter: {a}\n---\n"


def llm(claim):
    return ("---\ntype: llm\nfocus: last_message\n---\n"
            "Ignore any trailing notice about a company directive («Nutzung von "
            "Claude und andere AI-Agents»). " + claim + "\n")


NO_PREAMBLE = (r"^\s*(I'll|I will|Let me|I've|I have|I read|I'm|Reading|First,|"
               r"Now|Okay|OK,|Sure|Here's|Here is|Done)")

# --------------------------------------------------------------------------
# 1. correct-but-terse-is-left-alone
GET_DOC = ("// Get returns the value stored under key, or the zero value when key\n"
           "// is absent.\n")
store_go = (
    "// Package kv holds string values in memory.\n"
    "package kv\n\n"
    "// Store maps keys to values.\n"
    "type Store struct {\n\tm map[string]string\n}\n\n"
    "// NewStore returns an empty Store.\n"
    "func NewStore() *Store {\n\treturn &Store{m: map[string]string{}}\n}\n\n"
    + GET_DOC +
    "func Get(sto *Store, key string) string {\n\treturn sto.m[key]\n}\n"
)
write_case(
    "doc--correct-but-terse-is-left-alone", "/go:doc func=Get",
    {**gomod("example.com/kv"), "kv/kv.go": store_go},
    {
        "b1-reports-nothing-fires": rx(
            "last_message",
            r"(no|none of the)[^.\n]{0,40}(checklist|item|change|edit)|"
            r"nothing[^.\n]{0,30}(fire|change|to (do|fix|change))|unchanged|"
            r"left (alone|as is|untouched)|no changes?",
            flags="i"),
        "b2-comment-byte-identical": rx(
            "kv/kv.go", esc(GET_DOC + "func Get(sto *Store, key string) string {")),
        "b2-no-edit": used("Edit", 0, 0),
        "b3-no-change-line": llm(
            "The reply does not report any change to Get's godoc: no line says "
            "Get's comment was added, fixed, expanded, or rewritten."),
    },
    shell=False,
)

# --------------------------------------------------------------------------
# 2. adds-only-confirmable-facts
STORE_DOC = "// Store adds recs to the archive.\n"
archive_go = (
    "// Package archive keeps records in ID order.\n"
    "package archive\n\n"
    "import \"sort\"\n\n"
    "// Record is one archived entry.\n"
    "type Record struct {\n\tID   int\n\tBody string\n}\n\n"
    "// Archive holds records.\n"
    "type Archive struct {\n\titems []Record\n}\n\n"
    + STORE_DOC +
    "func (arc *Archive) Store(recs []Record) {\n"
    "\tsort.Slice(recs, func(i, j int) bool { return recs[i].ID < recs[j].ID })\n"
    "\tarc.items = append(arc.items, recs...)\n"
    "}\n\n"
    "// Len returns the number of archived records.\n"
    "func (arc *Archive) Len() int {\n\treturn len(arc.items)\n}\n"
)
STORE_GODOC_BLOCK = r"((//[^\n]*\n)*)func \(arc \*Archive\) Store\("
write_case(
    "doc--adds-only-confirmable-facts", "/go:doc func=Store",
    {**gomod("example.com/archive"), "archive/archive.go": archive_go},
    {
        "b1-fires-missing-fact": rx(
            "last_message", r"missing[- ]fact|item\s*#?4|\(4\)|—\s*4\b", flags="i"),
        "b2-documents-mutation": rx(
            "archive/archive.go",
            r"//[^\n]*(sort|reorder|in place|modif|mutat|order)[^\n]*\n(//[^\n]*\n)*"
            r"func \(arc \*Archive\) Store\(", flags="i"),
        "b3-no-concurrency-claim": rx(
            "archive/archive.go",
            r"concurren|goroutine|synchroni|thread|safe for|mutex|lock", flags="i",
            negate=True),
    },
)

# --------------------------------------------------------------------------
# 3. directives-and-interface-method-godoc
BUILD = "//go:build !windows\n"
GEN = "//go:generate stringer -type=Mode\n"
READ_DOC = ("// Read reads up to len(p) bytes into p. It returns the number of bytes\n"
            "// read and any error encountered. At end of input it returns 0, io.EOF.\n")
io_go = (
    BUILD + "\n"
    "// Package io serves bytes from an in-memory buffer.\n"
    "package io\n\n"
    "import \"io\"\n\n"
    + GEN + "\n"
    "// Mode selects how a Source treats its buffer.\n"
    "type Mode int\n\n"
    "// Source modes.\n"
    "const (\n\tModeCopy Mode = iota\n\tModeShare\n)\n\n"
    "var _ io.Reader = (*Source)(nil)\n\n"
    "// Source reads from a fixed byte slice.\n"
    "type Source struct {\n\tbuf []byte\n\toff int\n}\n\n"
    "// NewSource returns a Source that reads buf.\n"
    "func NewSource(buf []byte) *Source {\n\treturn &Source{buf: buf}\n}\n\n"
    + READ_DOC +
    "func (src *Source) Read(p []byte) (int, error) {\n"
    "\tif src.off >= len(src.buf) {\n\t\treturn 0, io.EOF\n\t}\n"
    "\tn := copy(p, src.buf[src.off:])\n"
    "\tsrc.off += n\n"
    "\treturn n, nil\n"
    "}\n"
)
io_files = {**gomod("example.com/demo"), "pkg/io/io.go": io_go}
io_tags = ["sec:doc:plan-file-package-module", "sec:doc:never-touch"]
write_case(
    "doc--directives-and-interface-method-godoc--gate", "/go:doc ./pkg/io",
    io_files,
    {
        "b1-build-directive-in-plan": rx(
            "last_message", r"go:build[^\n]*(never|directive|untouch|leave|skip)|"
            r"(never|directive|untouch)[^\n]*go:build", flags="i"),
        "b1-generate-directive-in-plan": rx(
            "last_message", r"go:generate[^\n]*(never|directive|untouch|leave|skip)|"
            r"(never|directive|untouch)[^\n]*go:generate", flags="i"),
        "b2-plans-read-removal": rx(
            "last_message", r"Read[^\n]*(remov|delet|drop|strip)|"
            r"(remov|delet|drop|strip)[^\n]*\bRead\b", flags="i"),
        "b3-no-write": used("Write", 0, 0),
        "b3-no-edit": used("Edit", 0, 0),
        "b3-file-unchanged": rx("pkg/io/io.go", esc(io_go)),
    },
    tags_extra=io_tags, shell=False,
)
write_case(
    "doc--directives-and-interface-method-godoc", "/go:doc ./pkg/io",
    io_files,
    {
        "b1-build-directive-unchanged": rx(
            "pkg/io/io.go", "^" + esc(BUILD + "\n// Package io")),
        "b1-generate-directive-unchanged": rx(
            "pkg/io/io.go", esc("\n" + GEN)),
        "b2-read-godoc-removed": rx(
            "pkg/io/io.go", r"reads up to len\(p\)|any error encountered", flags="i",
            negate=True),
        "b2-read-kept": rx(
            "pkg/io/io.go", esc("func (src *Source) Read(p []byte) (int, error) {")),
    },
    tags_extra=io_tags,
    answers=["To the plan: \"Approved, go ahead.\""],
)

# --------------------------------------------------------------------------
# 4. terse-output
text_go = (
    "// Package text counts words.\n"
    "package text\n\n"
    "import \"strings\"\n\n"
    "// counts the words in s, splitting on runs of white space.\n"
    "func Foo(s string) int {\n"
    "\tcount := 0\n"
    "\tfor range strings.Fields(s) {\n"
    "\t\t// increment count\n"
    "\t\tcount++\n"
    "\t}\n"
    "\treturn count\n"
    "}\n"
)
write_case(
    "doc--terse-output", "/go:doc func=Foo",
    {**gomod("example.com/text"), "text/text.go": text_go},
    {
        "b1-no-preamble": rx("last_message", NO_PREAMBLE, negate=True),
        "b1-verify-result": rx("last_message", r"gofmt[\s\S]*go build|go build[\s\S]*gofmt"),
        "b2-change-line-format": rx("last_message", r"text\.go:Foo[^\n]{0,20}[—–]"),
        "b2-inline-comment-once": rx(
            "last_message", r"increment count[\s\S]*increment count", negate=True),
        "b3-no-recap-heading": rx(
            "last_message", r"^\W*(In summary|Summary|To summari[sz]e|Overall|In short)\b",
            flags="im", negate=True),
        "b3-change-lines-not-repeated": rx(
            "last_message", r"(text\.go:Foo[\s\S]*){3}", negate=True),
    },
)

# --------------------------------------------------------------------------
# 5. line-target-resolves-to-its-item
svc_head = (
    "// Package svc buffers lines and sends them in batches.\n"
    "package svc\n\n"
    "import (\n\t\"errors\"\n\t\"strings\"\n)\n\n"
    "// ErrClosed is returned when a Svc is used after Close.\n"
    "var ErrClosed = errors.New(\"svc: closed\")\n\n"
    "// Svc buffers lines and sends them in batches of ten.\n"
    "type Svc struct {\n\tlines  []string\n\tclosed bool\n}\n\n"
)
NEW_FN = "// New returns an empty Svc.\nfunc New() *Svc {\n\treturn &Svc{}\n}\n"
ADD_FN = (
    "func (svc *Svc) Add(line string) error {\n"
    "\tif svc.closed {\n\t\treturn ErrClosed\n\t}\n"
    "\t// append the line\n"
    "\tsvc.lines = append(svc.lines, strings.TrimSpace(line))\n"
    "\treturn nil\n"
    "}\n"
)
FLUSH_DOC = "// flush sends the lines.\n"
FLUSH_FN = (
    FLUSH_DOC +
    "func (svc *Svc) Flush(send func([]string)) (int, error) {\n"
    "\tif svc.closed {\n\t\treturn 0, ErrClosed\n\t}\n"
    "\ti := 0\n"
    "\tfor len(svc.lines) > 0 {\n"
    "\t\tn := min(len(svc.lines), 10)\n"
    "\t\tsend(svc.lines[:n])\n"
    "\t\tsvc.lines = svc.lines[n:]\n"
    "\t\t// increment i\n"
    "\t\ti++\n"
    "\t}\n"
    "\treturn i, nil\n"
    "}\n"
)
CLOSE_FN = (
    "// Close marks the svc closed.\n"
    "func (svc *Svc) Close() {\n"
    "\t// set closed to true\n"
    "\tsvc.closed = true\n"
    "}\n"
)
LEN_FN = (
    "// len returns the buffered lines\n"
    "func (svc *Svc) Len() int {\n\treturn len(svc.lines)\n}\n"
)
foo_go = svc_head + NEW_FN + "\n" + ADD_FN + "\n" + FLUSH_FN + "\n" + CLOSE_FN + "\n" + LEN_FN
print("increment line", foo_go.split("\n").index("\t\t// increment i") + 1)
assert foo_go.split("\n").index("\t\t// increment i") + 1 == 42
write_case(
    "doc--line-target-resolves-to-its-item", "/go:doc pkg/svc/foo.go:42",
    {**gomod("example.com/demo"), "pkg/svc/foo.go": foo_go},
    {
        "b1-resolved-to-flush-body": rx(
            "trace", r"(resolv|enclos|innermost|inline comments? (of|in|inside)|line \d+ is (inside|within|in))"
            r"[^\n]{0,120}Flush", flags="i"),
        "b1-flush-godoc-unchanged": rx(
            "pkg/svc/foo.go", esc(FLUSH_DOC + "func (svc *Svc) Flush(")),
        "b2-new-unchanged": rx("pkg/svc/foo.go", esc(NEW_FN)),
        "b2-add-unchanged": rx("pkg/svc/foo.go", esc("\n\n" + ADD_FN)),
        "b2-close-unchanged": rx("pkg/svc/foo.go", esc(CLOSE_FN)),
        "b2-len-unchanged": rx("pkg/svc/foo.go", esc(LEN_FN)),
        "b3-ran-straight": used("Edit", 1),
        "b3-asks-no-approval": rx(
            "last_message", r"approv|shall I|should I|go ahead\?|proceed\?",
            flags="i", negate=True),
        # Item 6 allows "tighten to the why" as well as delete: only the
        # narration itself must go.
        "b4-restating-comment-deleted": rx(
            "pkg/svc/foo.go", r"//\s*(increment|incr|add one to|bump)\b[^\n]*\bi\b", negate=True, flags="i"),
    },
)

# --------------------------------------------------------------------------
# 6. module-mode-with-fanout-and-filter
OTHERS = ["auth", "cache", "config", "events", "httpx", "logx", "metrics",
          "queue", "retry"]
other_src = {
    "auth": ("// Package auth checks bearer tokens.\npackage auth\n\nimport \"strings\"\n\n"
             "func Token(header string) string {\n"
             "\treturn strings.TrimPrefix(header, \"Bearer \")\n}\n"),
    "cache": ("// Package cache holds values in memory.\npackage cache\n\n"
              "// Cache maps keys to values.\ntype Cache struct {\n\tm map[string]string\n}\n\n"
              "func (cac *Cache) Set(k, v string) {\n\tcac.m[k] = v\n}\n"),
    "config": ("// Package config reads key=value settings.\npackage config\n\n"
               "import \"strings\"\n\n"
               "func Parse(text string) map[string]string {\n"
               "\tout := map[string]string{}\n"
               "\tfor _, line := range strings.Split(text, \"\\n\") {\n"
               "\t\tk, v, _ := strings.Cut(line, \"=\")\n"
               "\t\tout[k] = v\n\t}\n\treturn out\n}\n"),
    "events": ("// Package events fans events out to subscribers.\npackage events\n\n"
               "// Bus delivers events to subscribers.\ntype Bus struct {\n\tsubs []chan string\n}\n\n"
               "// publish sends ev\nfunc (bus *Bus) Publish(ev string) {\n"
               "\tfor _, sub := range bus.subs {\n\t\tsub <- ev\n\t}\n}\n"),
    "httpx": ("// Package httpx holds HTTP helpers.\npackage httpx\n\n"
              "import \"net/http\"\n\n"
              "func IsOK(resp *http.Response) bool {\n"
              "\treturn resp.StatusCode >= 200 && resp.StatusCode < 300\n}\n"),
    "logx": ("// Package logx formats log lines.\npackage logx\n\n"
             "import \"fmt\"\n\n"
             "func Line(level, msg string) string {\n"
             "\treturn fmt.Sprintf(\"[%s] %s\", level, msg)\n}\n"),
    "metrics": ("// Package metrics counts events.\npackage metrics\n\n"
                "// Counter counts events.\ntype Counter struct {\n\tn int\n}\n\n"
                "func (cnt *Counter) Inc() {\n\t// add one\n\tcnt.n++\n}\n"),
    "queue": ("package queue\n\n"
              "// Queue is a FIFO of ints.\ntype Queue struct {\n\titems []int\n}\n\n"
              "// Push appends v.\nfunc (que *Queue) Push(v int) {\n"
              "\tque.items = append(que.items, v)\n}\n"),
    "retry": ("// Package retry repeats a call until it succeeds.\npackage retry\n\n"
              "func Do(n int, fn func() error) error {\n"
              "\tvar err error\n\tfor range n {\n\t\tif err = fn(); err == nil {\n"
              "\t\t\treturn nil\n\t\t}\n\t}\n\treturn err\n}\n"),
}
api_go = (
    "// Package api routes request paths to handler names.\n"
    "package api\n\n"
    "import \"strings\"\n\n"
    "// Router maps path prefixes to handler names.\n"
    "type Router struct {\n\troutes map[string]string\n}\n\n"
    "// NewRouter returns an empty Router.\n"
    "func NewRouter() *Router {\n\treturn &Router{routes: map[string]string{}}\n}\n\n"
    "func (rtr *Router) Handle(prefix, name string) {\n"
    "\trtr.routes[prefix] = name\n}\n\n"
    "// match finds the handler\n"
    "func (rtr *Router) Match(path string) string {\n"
    "\tfor prefix, name := range rtr.routes {\n"
    "\t\tif strings.HasPrefix(path, prefix) {\n\t\t\treturn name\n\t\t}\n\t}\n"
    "\treturn \"\"\n}\n"
)
svc_go = (
    "// Package svc wires the api package into a running service.\n"
    "package svc\n\n"
    "import \"example.com/mod/api\"\n\n"
    "// Service serves requests through a Router.\n"
    "type Service struct {\n\trtr *api.Router\n}\n\n"
    "func New(rtr *api.Router) *Service {\n\treturn &Service{rtr: rtr}\n}\n\n"
    "// Lookup returns the handler name for path.\n"
    "func (srv *Service) Lookup(path string) string {\n"
    "\t// call Match\n"
    "\treturn srv.rtr.Match(path)\n}\n"
)
mod_files = {**gomod("example.com/mod"), "api/api.go": api_go, "svc/svc.go": svc_go}
for p in OTHERS:
    mod_files[f"{p}/{p}.go"] = other_src[p]
mod_tags = ["sec:doc:plan-file-package-module", "sec:doc:controls",
            "sec:doc:verify"]
others_alt = "|".join(OTHERS)
write_case(
    "doc--module-mode-with-fanout-and-filter--gate",
    "/go:doc module fanout packages=svc,api",
    mod_files,
    {
        "b1-plan-has-api-item": rx("last_message", r"\bHandle\b"),
        "b1-plan-has-svc-item": rx("last_message", r"\bLookup\b"),
        "b1-no-other-package-items": rx(
            "last_message", rf"\b({others_alt})(/\w+)?\.go\b", negate=True),
        "b1-no-write": used("Write", 0, 0),
        "b1-no-edit": used("Edit", 0, 0),
    },
    tags_extra=mod_tags, shell=False, agent=True, max_turns=60,
)
write_case(
    "doc--module-mode-with-fanout-and-filter",
    "/go:doc module fanout packages=svc,api",
    mod_files,
    {
        "b1-others-reported-skipped": rx(
            "last_message",
            "^(?=[\\s\\S]*skip)" + "".join(f"(?=[\\s\\S]*\\b{p}\\b)" for p in OTHERS),
            flags="i"),
        "b1-auth-untouched": rx("auth/auth.go", esc(other_src["auth"])),
        "b1-metrics-untouched": rx("metrics/metrics.go", esc(other_src["metrics"])),
        "b2-two-workers": used("Agent", 2, 2),
        "b2-api-worker": used("Agent", 1, match=r"\bapi\b"),
        "b2-svc-worker": used("Agent", 1, match=r"\bsvc\b"),
        "b3-router-no-concurrency-claim": rx(
            "api/api.go", r"concurren|goroutine|synchroni|thread|safe for|mutex|lock",
            flags="i", negate=True),
        # Parent plan read + worker read + parent re-read; subagent calls share the trace.
        # After the last worker returns, the parent reads api.go again, by Read
        # or by a shell cat.
        "b4-parent-rereads-after-merge": rx("trace",
            r'"name":"Agent"(?![\s\S]*"name":"Agent")[\s\S]*'
            r'"name":"(?:Read|Bash)","input":\{"(?:file_path|command)":"(?:[^"\\]|\\.)*api/api\.go'),
        "b4-report-says-rechecked": rx(
            "last_message", r"re-?read|re-?check|revert|checked (every|each|all)", flags="i"),
        "b5-verify-passed": rx(
            "last_message",
            r"(gofmt[^\n]*go build|go build[^\n]*gofmt)[^\n]*\b(pass|passed|clean|ok|succeed)"
            r"|\b(pass|passed|clean|ok|succeed)\w*\b[^\n]{0,20}(gofmt[^\n]*go build|go build[^\n]*gofmt)",
            flags="i"),
    },
    tags_extra=mod_tags, agent=True, max_turns=80,
    answers=["To the plan: \"Approved, go ahead.\""],
)

# --------------------------------------------------------------------------
# 7. side-effect-is-not-a-surprise
FILE_DOC = ("// Write writes p to the file. It returns the number of bytes written\n"
            "// and any error encountered.\n")
TEE_DOC = ("// Write writes p to the primary writer. It returns the number of bytes\n"
           "// written and any error encountered.\n")
sink_go = (
    "// Package sink writes byte streams to their destinations.\n"
    "package sink\n\n"
    "import (\n\t\"io\"\n\t\"os\"\n)\n\n"
    "var _ io.Writer = (*fileSink)(nil)\n"
    "var _ io.Writer = (*teeSink)(nil)\n\n"
    "// fileSink writes to an open file.\n"
    "type fileSink struct {\n\tfil *os.File\n}\n\n"
    + FILE_DOC +
    "func (snk *fileSink) Write(p []byte) (int, error) {\n"
    "\treturn snk.fil.Write(p)\n"
    "}\n\n"
    "// teeSink writes to a primary writer and a mirror.\n"
    "type teeSink struct {\n\tprimary io.Writer\n\tmirror  io.Writer\n}\n\n"
    + TEE_DOC +
    "func (tee *teeSink) Write(p []byte) (int, error) {\n"
    "\tn, err := tee.primary.Write(p)\n"
    "\tif err != nil {\n\t\treturn n, err\n\t}\n"
    "\t_, _ = tee.mirror.Write(p)\n"
    "\treturn len(p), nil\n"
    "}\n"
)
sink_files = {**gomod("example.com/demo"), "pkg/sink/sink.go": sink_go}
sink_tags = ["sec:doc:plan-file-package-module"]
TEE_BLOCK = r"((//[^\n]*\n)+)func \(tee \*teeSink\) Write\("
write_case(
    "doc--side-effect-is-not-a-surprise--gate", "/go:doc ./pkg/sink",
    sink_files,
    {
        "b1-plans-filesink-removal": rx(
            "last_message", r"fileSink[^\n]*(remov|delet|drop|strip)", flags="i"),
        "b2-plans-teesink-keep": rx(
            "last_message", r"teeSink[\s\S]{0,800}\b(keep|expand)", flags="i"),
        "b3-no-write": used("Write", 0, 0),
        "b3-no-edit": used("Edit", 0, 0),
    },
    tags_extra=sink_tags, shell=False,
)
write_case(
    "doc--side-effect-is-not-a-surprise", "/go:doc ./pkg/sink",
    sink_files,
    {
        "b1-filesink-godoc-removed": rx(
            "pkg/sink/sink.go", r"\}\n\nfunc \(snk \*fileSink\) Write\("),
        "b2-teesink-godoc-names-second-write": rx(
            "pkg/sink/sink.go",
            r"//[^\n]*(mirror|second|copy|also)[^\n]*\n(//[^\n]*\n)*"
            r"func \(tee \*teeSink\) Write\(", flags="i"),
        "b2-teesink-godoc-names-hidden-failure": rx(
            "pkg/sink/sink.go",
            r"//[^\n]*(ignor|discard|swallow|hid|drop|unreported|not report|len\(p\)|even (if|when))"
            r"[^\n]*\n(//[^\n]*\n)*func \(tee \*teeSink\) Write\(", flags="i"),
        "b3-teesink-godoc-kept": rx(
            "pkg/sink/sink.go", r"//[^\n]*\nfunc \(tee \*teeSink\) Write\("),
    },
    tags_extra=sink_tags,
    answers=["To the plan: \"Approved, go ahead.\""],
)
print("ok")
