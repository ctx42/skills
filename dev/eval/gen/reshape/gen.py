#!/usr/bin/env python3
"""Generate go/evals/reshape--* native eval cases. Re-runnable; owns only reshape--*."""
import os
import re
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
EVALS = os.path.join(ROOT, "go/evals")

ENGLISH = "The user writes English; reply in English.\n"
NOTICE = ("Ignore any trailing notice about a company directive "
          "(«Nutzung von Claude und andere AI-Agents»). ")

BASE_TAGS = ["skill:reshape", "sec:reshape:target", "sec:reshape:modifiability",
             "sec:reshape:workflow", "sec:reshape:change-archetypes",
             "sec:reshape:impact-rubric", "sec:reshape:output",
             "sec:reshape:self-learning", "ref:reshape/change-catalog",
             "sec:style:production"]
ALLOWED = ["Read", "Glob", "Grep", "Skill", "LSP", "Write", "Edit"]

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


def scaffold(files, extra=""):
    # Runs have no network: fill the run's module cache now, from the local
    # cache that dev/eval-changed.sh serves as GOPROXY.
    tail = "go mod download\n" if "go.sum" in files else ""
    return "#!/usr/bin/env bash\nset -euo pipefail\n" + heredocs(files) + tail + extra


def g_regex(pattern, target="last_message", flags=None, match=None):
    # JS regex: no inline (?m)/(?i); hoist a leading group into flags.
    m = re.match(r"\(\?([a-z]+)\)", pattern)
    if m:
        flags = "".join(sorted(set((flags or "") + m.group(1))))
        pattern = pattern[m.end():]
    assert "(?m)" not in pattern and "(?i)" not in pattern, pattern
    fm = ["type: regex", f"target: {target}"]
    if match:
        fm.append(f'match: "{match}"')
    if flags:
        fm.append(f'flags: "{flags}"')
    return "---\n" + "\n".join(fm) + "\n---\n" + pattern + "\n"


def g_never(tool):
    return f"---\ntype: tool_used\ntool: {tool}\nmin: 0\nmax: 0\narm: both\n---\n"


def g_llm(claim):
    return f"---\ntype: llm\nfocus: last_message\n---\n{NOTICE}{claim}\n"


READ_ONLY = {"b0-no-write": g_never("Write"), "b0-no-edit": g_never("Edit")}


def write_case(name, prompt, graders, files, tags=(), max_turns=60, timeout=300,
               extra=""):
    d = os.path.join(EVALS, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "graders"))
    alltags = [f"case:{name}"] + BASE_TAGS + list(tags)
    fm = [f"tags: [{', '.join(alltags)}]", "runs: 1",
          f"max_turns: {max_turns}", f"timeout_seconds: {timeout}",
          f"allowed_tools: [{', '.join(ALLOWED)}]",
          "append_system_prompt: |", "  " + ENGLISH.rstrip("\n")]
    with open(os.path.join(d, "prompt.md"), "w") as f:
        f.write("---\n" + "\n".join(fm) + "\n---\n\n" + prompt + "\n")
    with open(os.path.join(d, "case.yaml"), "w") as f:
        f.write(f'schema_version: "1.1"\nname: {name}\ncontext:\n'
                "  scaffold_script: scaffold.sh\n")
    p = os.path.join(d, "scaffold.sh")
    with open(p, "w") as f:
        f.write(scaffold(files, extra))
    os.chmod(p, 0o755)
    for gname, body in graders.items():
        with open(os.path.join(d, "graders", gname + ".md"), "w") as f:
            f.write(body)


def cite_guard(files, valid):
    """not_contains regex: a citation of a consumer file at a line that holds no use.

    valid maps file path -> set of line numbers a correct "before" may start at.
    """
    alts = []
    for path, lines in valid.items():
        base = re.escape(os.path.basename(path))
        ok = "|".join(str(n) for n in sorted(lines))
        alts.append(f"{base}:(?!(?:{ok})\\b)\\d+")
    return "(" + "|".join(alts) + ")"


def go_mod(module, extra=""):
    return f"module {module}\n\ngo 1.22\n{extra}"


# ======================================================= case 1: must, local

MUST1_LIB = '''// Package must reads settings from env-style files.
package must

import (
	"errors"
	"os"
	"path/filepath"
	"strings"
)

// ErrMissing is returned when a key has no value.
var ErrMissing = errors.New("must: missing key")

// Options configures Load.
type Options struct {
	Dir    string // Directory holding the settings file.
	Ext    string // Settings file extension.
	Strict bool   // Fail on malformed lines.
}

// Source holds loaded settings.
type Source struct {
	vals map[string]string
}

// Load reads the settings file in opts.Dir with extension opts.Ext.
func Load(opts Options) *Source {
	src := &Source{vals: map[string]string{}}
	data, err := os.ReadFile(filepath.Join(opts.Dir, "settings"+opts.Ext))
	if err != nil {
		return src
	}
	for _, line := range strings.Split(string(data), "\\n") {
		k, v, ok := strings.Cut(line, "=")
		if !ok {
			continue
		}
		src.vals[strings.TrimSpace(k)] = strings.TrimSpace(v)
	}
	return src
}

// Value returns the value of key, or ErrMissing when it is unset.
func Value(src *Source, key string) (string, error) {
	v, ok := src.vals[key]
	if !ok {
		return "", ErrMissing
	}
	return v, nil
}
'''

# (file, func, [(var, KEY, default or None for return-err)])
MUST1_FUNCS = [
    ("config/server.go", "Server", [("host", "SERVER_HOST", "localhost"), ("port", "SERVER_PORT", "8080"), ("token", "SERVER_TOKEN", None)]),
    ("config/server.go", "Admin", [("addr", "ADMIN_ADDR", "127.0.0.1:9000"), ("user", "ADMIN_USER", "admin"), ("theme", "ADMIN_THEME", "light")]),
    ("config/server.go", "TLS", [("cert", "TLS_CERT", "cert.pem"), ("key", "TLS_KEY", "key.pem")]),
    ("config/store.go", "Database", [("dsn", "DB_DSN", None), ("pool", "DB_POOL", "10"), ("timeout", "DB_TIMEOUT", "5s")]),
    ("config/store.go", "Cache", [("addr", "CACHE_ADDR", "localhost:6379"), ("ttl", "CACHE_TTL", "60s"), ("prefix", "CACHE_PREFIX", "app:")]),
    ("config/store.go", "Queue", [("url", "QUEUE_URL", None), ("workers", "QUEUE_WORKERS", "4"), ("retry", "QUEUE_RETRY", "3")]),
    ("config/notify.go", "Mail", [("host", "MAIL_HOST", "smtp.local"), ("from", "MAIL_FROM", "noreply@example.com"), ("pass", "MAIL_PASS", None)]),
    ("config/notify.go", "Slack", [("hook", "SLACK_HOOK", None), ("channel", "SLACK_CHANNEL", "#ops"), ("name", "SLACK_NAME", "bot")]),
    ("config/notify.go", "Pager", [("key", "PAGER_KEY", "none"), ("level", "PAGER_LEVEL", "warn")]),
    ("config/observe.go", "Logging", [("level", "LOG_LEVEL", "info"), ("format", "LOG_FORMAT", "json"), ("file", "LOG_FILE", "app.log")]),
    ("config/observe.go", "Metrics", [("addr", "METRICS_ADDR", ":9100"), ("path", "METRICS_PATH", "/metrics"), ("ns", "METRICS_NS", None)]),
    ("config/observe.go", "Tracing", [("url", "TRACE_URL", "http://localhost:4318"), ("rate", "TRACE_RATE", "0.1"), ("svc", "TRACE_SERVICE", "app")]),
]


def must1_consumer():
    files, valid = {}, {}
    by_file = {}
    for path, fn, vals in MUST1_FUNCS:
        by_file.setdefault(path, []).append((fn, vals))
    for path, funcs in by_file.items():
        topic = os.path.basename(path)[:-3]
        lines = [f"package config", "", 'import "example.com/must"', ""]
        if path == "config/server.go":
            lines = ["// Package config loads the application settings.", "package config",
                     "", 'import "example.com/must"', "",
                     "// Settings maps setting names to values.",
                     "type Settings map[string]string", ""]
        ok = set()
        for fn, vals in funcs:
            ok.add(len(lines) + 1)
            lines.append(f"// {fn} returns the {fn.lower()} settings.")
            ok.add(len(lines) + 1)
            lines.append(f"func {fn}() (Settings, error) {{")
            ok.add(len(lines) + 1)
            lines.append('\tsrc := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})')
            for var, key, dflt in vals:
                ok.update(range(len(lines) + 1, len(lines) + 6))
                lines.append("")
                lines.append(f'\t{var}, err := must.Value(src, "{key}")')
                lines.append("\tif err != nil {")
                if dflt is None:
                    lines.append("\t\treturn nil, err")
                else:
                    lines.append(f'\t\t{var} = "{dflt}"')
                lines.append("\t}")
            pairs = ", ".join(f'"{v}": {v}' for v, _, _ in vals)
            lines.append(f"\treturn Settings{{{pairs}}}, nil")
            lines.append("}")
            lines.append("")
        files[path] = "\n".join(lines)
        valid[path] = ok
    return files, valid


def case_ranked():
    name = "reshape--ranked-multi-archetype-proposals"
    files = {
        "go.mod": go_mod("example.com/app",
                         "\nrequire example.com/must v0.0.0\n\n"
                         "replace example.com/must => ./third_party/must\n"),
        "third_party/must/go.mod": go_mod("example.com/must"),
        "third_party/must/must.go": MUST1_LIB,
    }
    consumer, valid = must1_consumer()
    files.update(consumer)
    n_value = sum(len(v) for _, _, v in MUST1_FUNCS)
    n_drop = sum(1 for _, _, v in MUST1_FUNCS for x in v if x[2] is not None)
    n = n_value + len(MUST1_FUNCS)
    assert (n_value, n_drop, len(MUST1_FUNCS), n) == (34, 28, 12, 46), (n_value, n_drop, n)
    graders = {
        "b1-header-library": g_regex(r"(?m)^[^\n|]*\bmust\b[^\n|]*\b\d+\s+uses\b"),
        "b1-header-scope": g_regex(r"(?m)^[^\n|]*(module|example\.com/app|\./\.\.\.)[^\n|]*\b\d+\s+uses\b", flags="i"),
        "b1-header-count": g_regex(r"(?m)^[^\n|]*\b46\s+uses\b"),
        "b2-structural": g_regex(r"absorb[- ]the[- ]sequence|move[- ]responsibility[- ]upstream", flags="i"),
        "b2-second-archetype": g_regex(r"options[- ]constructor|default[- ]away[- ]a[- ]param|builder", flags="i"),
        "b3-reach-of-n": g_regex(r"(?m)^\|[^\n]*\b\d+\s*/\s*46\b[^\n]*\|"),
        "b3-ranked-labels": g_regex(r"(?m)^\|\s*1\s*\|[^\n]*\bHigh\b"),
        "b3-tradeoff": g_llm("Each proposal's one-line rationale names what it trades "
                             "against: a cost such as API breakage, implementation "
                             "effort, or impact on other consumers."),
        "b4-cites-site": g_regex(r"config/(server|store|notify|observe)\.go:\d+"),
        "b4-cites-real-lines": g_regex(cite_guard(consumer, valid), match="not_contains"),
        "b4-no-placeholder": g_regex(r"//\s*before\b|//\s*\.\.\.|//\s*…", flags="i", match="not_contains"),
        "b4-before-after": g_llm("Every proposal in the reply shows a before code excerpt "
                                 "and an after code excerpt of a consumer call site."),
        "b5-concrete-diff": g_regex(r"(?m)```diff|^\+\s*func\s+\w+"),
    }
    graders.update(READ_ONLY)
    write_case(name, "/go:reshape must", graders, files)


# ================================================ case 2: oskit, external

OSKIT_RENDER = {
    "template": ("templates", "Template", "template"),
    "partial": ("partials", "Partial", "partial"),
    "layout": ("layouts", "Layout", "layout"),
    "asset": ("assets", "Asset", "asset"),
}


def oskit_consumer():
    files = {}
    for fname, (dirname, fn, what) in OSKIT_RENDER.items():
        head = ""
        if fname == "template":
            head = "// Package render renders pages from templates on disk.\n"
        files[f"pkg/render/{fname}.go"] = f'''{head}package render

import (
	"fmt"
	"path/filepath"
	"strings"

	"github.com/acme/oskit"
)

// Load{fn} returns the {what} called name.
func Load{fn}(name string) (string, error) {{
	f, err := oskit.Open(filepath.Join("{dirname}", name))
	if err != nil {{
		if strings.Contains(err.Error(), "does not exist") {{
			return "", fmt.Errorf("{what} %q not found", name)
		}}
		return "", err
	}}
	defer f.Close()
	data, err := oskit.ReadAll(f)
	if err != nil {{
		return "", err
	}}
	return strings.TrimSpace(string(data)), nil
}}
'''
    files["pkg/render/page.go"] = '''package render

import "strings"

// Page renders the named page inside its layout.
func Page(name string) (string, error) {
	layout, err := LoadLayout("base.html")
	if err != nil {
		return "", err
	}
	body, err := LoadTemplate(name)
	if err != nil {
		return "", err
	}
	return strings.Replace(layout, "{{body}}", body, 1), nil
}
'''
    files["pkg/report/report.go"] = '''// Package report writes run reports.
package report

import "github.com/acme/oskit"

// Save writes data to path.
func Save(path string, data []byte) error {
	f, err := oskit.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	_, err = f.Write(data)
	return err
}

// Exists reports whether path exists.
func Exists(path string) bool {
	_, err := oskit.Stat(path)
	return err == nil
}
'''
    return files


OSKIT_SRC = """// Package oskit wraps the operating system's file calls.
package oskit

import (
	"io"
	"os"
)

// File is an open file.
type File struct {
	fil *os.File
}

// Open opens name for reading.
func Open(name string) (*File, error) {
	fil, err := os.Open(name)
	if err != nil {
		return nil, err
	}
	return &File{fil: fil}, nil
}

// Create creates or truncates name for writing.
func Create(name string) (*File, error) {
	fil, err := os.Create(name)
	if err != nil {
		return nil, err
	}
	return &File{fil: fil}, nil
}

// Read reads up to len(p) bytes into p.
func (fl *File) Read(p []byte) (int, error) { return fl.fil.Read(p) }

// Write writes p to the file.
func (fl *File) Write(p []byte) (int, error) { return fl.fil.Write(p) }

// Close closes the file.
func (fl *File) Close() error { return fl.fil.Close() }

// ReadAll reads from fl until EOF.
func ReadAll(fl *File) ([]byte, error) { return io.ReadAll(fl) }

// Stat describes the named file.
func Stat(name string) (os.FileInfo, error) { return os.Stat(name) }
"""

# oskit is fictional: build v1.4.0 into a throwaway file proxy and `go get` it,
# so it lands in the run's module cache like any external dependency — no
# replace, no go.work (the setup's terms).
OSKIT_FETCH = """px=$(mktemp -d)
src=$px/src/github.com/acme/oskit@v1.4.0
at=$px/proxy/github.com/acme/oskit/@v
mkdir -p "$src" "$at"
printf 'module github.com/acme/oskit\\n\\ngo 1.22\\n' > "$src/go.mod"
cat > "$src/oskit.go" <<'EOF_OSKIT'
""" + OSKIT_SRC + """EOF_OSKIT
cp "$src/go.mod" "$at/v1.4.0.mod"
printf '{"Version":"v1.4.0","Time":"2026-01-01T00:00:00Z"}' > "$at/v1.4.0.info"
printf 'v1.4.0\\n' > "$at/list"
(cd "$px/src" && zip -qr "$at/v1.4.0.zip" github.com/acme/oskit@v1.4.0)
GOPROXY="file://$px/proxy" GOSUMDB=off GOFLAGS=-mod=mod go get github.com/acme/oskit@v1.4.0
rm -rf "$px"
"""


def case_library():
    name = "reshape--proposals-stay-on-the-library"
    files = {"go.mod": go_mod("example.com/site", "\nrequire github.com/acme/oskit v1.4.0\n")}
    files.update(oskit_consumer())
    graders = {
        "b1-changes-oskit-api": g_llm("Every proposal in the reply is a change to oskit's "
                                      "own API (a new or changed oskit function, type, "
                                      "option, or error); none is only a refactor of the "
                                      "consumer code with oskit left as it is."),
        "b1-proposes-oskit-symbol": g_regex(r"oskit\.(ReadFile|ErrNotExist|ErrNotFound|IsNotExist|Read[A-Z]\w*|Err[A-Z]\w*)"),
        "b2-names-declined": g_llm("The reply names a call-site-only cleanup in "
                                   "pkg/render (for example a shared local helper for "
                                   "the four near-identical Load functions) as declined "
                                   "or out of scope, and says why."),
        "b3-sentinel-err-prefix": g_regex(r"\bErr[A-Z][A-Za-z]+\b"),
        "b3-no-get-prefix": g_regex(r"func\s+(\([^)]*\)\s*)?Get[A-Z]", match="not_contains"),
        "b3-scope-render-only": g_regex(r"report\.go:\d+", match="not_contains"),
        "b4-no-write": g_never("Write"),
        "b4-no-edit": g_never("Edit"),
    }
    write_case(name, "/go:reshape oskit in ./pkg/render", graders, files,
               tags=["sec:reshape:usage"], extra=OSKIT_FETCH)


# ============================================== case 3: yaml.v3, external

YAML_SUM = """gopkg.in/check.v1 v0.0.0-20161208181325-20d25e280405 h1:yhCVgyC4o1eVCa2tZl7eS0r+SDo693bJlVdllGtEeKM=
gopkg.in/check.v1 v0.0.0-20161208181325-20d25e280405/go.mod h1:Co6ibVJAznAaIkqp8huTwlJQCZ016jof/cbN4VW5Yz0=
gopkg.in/yaml.v3 v3.0.1 h1:fxVm/GzAzEWqLHuvctI91KS9hhNmmWOoWu0XTYJS7CA=
gopkg.in/yaml.v3 v3.0.1/go.mod h1:K4uyk7z7BCEPqu6E+C64Yfv1cQ7kz7rIZviUmN+EgEM=
"""

YAML_KEYS = '''// Package conf reads layered YAML configuration.
package conf

import (
	"fmt"

	"gopkg.in/yaml.v3"
)

// root parses data and returns its top-level mapping node.
func root(data []byte) (*yaml.Node, error) {
	var doc yaml.Node
	if err := yaml.Unmarshal(data, &doc); err != nil {
		return nil, err
	}
	if doc.Kind != yaml.DocumentNode || len(doc.Content) == 0 {
		return nil, fmt.Errorf("empty document")
	}
	top := doc.Content[0]
	if top.Kind != yaml.MappingNode {
		return nil, fmt.Errorf("top level is not a mapping")
	}
	return top, nil
}

// Keys returns the top-level keys of data in document order.
func Keys(data []byte) ([]string, error) {
	top, err := root(data)
	if err != nil {
		return nil, err
	}
	var keys []string
	for i := 0; i+1 < len(top.Content); i += 2 {
		keys = append(keys, top.Content[i].Value)
	}
	return keys, nil
}

// Get returns the scalar value under the top-level key.
func Get(data []byte, key string) (string, bool, error) {
	top, err := root(data)
	if err != nil {
		return "", false, err
	}
	for i := 0; i+1 < len(top.Content); i += 2 {
		if top.Content[i].Value == key {
			return top.Content[i+1].Value, true, nil
		}
	}
	return "", false, nil
}
'''

YAML_MERGE = '''package conf

import (
	"strings"

	"gopkg.in/yaml.v3"
)

// Comments returns the head comment of every top-level key.
func Comments(data []byte) (map[string]string, error) {
	top, err := root(data)
	if err != nil {
		return nil, err
	}
	out := map[string]string{}
	for i := 0; i+1 < len(top.Content); i += 2 {
		k := top.Content[i]
		out[k.Value] = strings.TrimSpace(strings.TrimPrefix(k.HeadComment, "#"))
	}
	return out, nil
}

// Decode decodes data into v, reporting type mismatches as invalid input.
func Decode(data []byte, v any) error {
	err := yaml.Unmarshal(data, v)
	if err != nil && strings.Contains(err.Error(), "cannot unmarshal") {
		return &InvalidError{Msg: err.Error()}
	}
	return err
}

// InvalidError reports YAML whose shape does not match the target.
type InvalidError struct {
	Msg string // Parser message.
}

// Error implements error.
func (e *InvalidError) Error() string { return "invalid config: " + e.Msg }

// Set replaces the scalar under the top-level key and returns the new YAML.
func Set(data []byte, key, value string) ([]byte, error) {
	top, err := root(data)
	if err != nil {
		return nil, err
	}
	for i := 0; i+1 < len(top.Content); i += 2 {
		if top.Content[i].Value == key {
			top.Content[i+1].Value = value
		}
	}
	return yaml.Marshal(top)
}
'''


def case_external():
    name = "reshape--external-library-public-surface"
    files = {
        "go.mod": go_mod("example.com/svc", "\nrequire gopkg.in/yaml.v3 v3.0.1\n"),
        "go.sum": YAML_SUM,
        "internal/conf/keys.go": YAML_KEYS,
        "internal/conf/merge.go": YAML_MERGE,
    }
    graders = {
        "b1-says-external": g_regex(r"\bexternal\b", flags="i"),
        "b2-cannot-diff-internals": g_regex(r"internals?", flags="i"),
        "b2-public-api-level": g_llm("Every proposal is framed as a change to yaml.v3's "
                                     "public API (an API-shape sketch of new or changed "
                                     "exported signatures), not as a diff against "
                                     "yaml.v3's source files."),
        "b3-local-wrapper": g_regex(r"wrapper", flags="i"),
    }
    graders.update(READ_ONLY)
    write_case(name, "/go:reshape gopkg.in/yaml.v3", graders, files)


# ============================================ case 4: terse, must max=3

MUST4_LIB = '''// Package must reads settings from env-style files.
package must

import (
	"errors"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

// Options configures Load.
type Options struct {
	Dir    string // Directory holding the settings file.
	Ext    string // Settings file extension.
	Strict bool   // Fail on malformed lines.
}

// Source holds loaded settings.
type Source struct {
	vals map[string]string
	raw  map[string]any
}

// Load reads the settings file in opts.Dir with extension opts.Ext.
func Load(opts Options) *Source {
	src := &Source{vals: map[string]string{}, raw: map[string]any{}}
	data, err := os.ReadFile(filepath.Join(opts.Dir, "settings"+opts.Ext))
	if err != nil {
		return src
	}
	for _, line := range strings.Split(string(data), "\\n") {
		k, v, ok := strings.Cut(line, "=")
		if !ok {
			continue
		}
		src.vals[strings.TrimSpace(k)] = strings.TrimSpace(v)
		src.raw[strings.TrimSpace(k)] = strings.TrimSpace(v)
	}
	return src
}

// Value returns the value of key.
func (s *Source) Value(key string) (string, error) {
	v, ok := s.vals[key]
	if !ok {
		return "", errors.New("must: missing key " + key)
	}
	return v, nil
}

// Lookup returns the value of key, whether it is set, and a parse error.
func (s *Source) Lookup(key string) (string, bool, error) {
	v, ok := s.vals[key]
	return v, ok, nil
}

// Raw returns the parsed value of key.
func (s *Source) Raw(key string) any { return s.raw[key] }

// Cursor walks the keys of a Source.
type Cursor struct {
	keys []string
	i    int
}

// Keys returns a cursor positioned before the first key.
func (s *Source) Keys() *Cursor {
	c := &Cursor{i: -1}
	for k := range s.vals {
		c.keys = append(c.keys, k)
	}
	sort.Strings(c.keys)
	return c
}

// Next advances the cursor and reports whether a key is available.
func (c *Cursor) Next() bool {
	c.i++
	return c.i < len(c.keys)
}

// Key returns the current key.
func (c *Cursor) Key() string { return c.keys[c.i] }

// Watch polls key every interval and calls onChange when its value changes,
// giving up after retries failed reads.
func Watch(s *Source, key string, interval time.Duration, retries int, onChange func(string)) error {
	last, _ := s.Value(key)
	fails := 0
	for fails < retries {
		time.Sleep(interval)
		v, err := s.Value(key)
		if err != nil {
			fails++
			continue
		}
		if v != last {
			onChange(v)
			last = v
		}
	}
	return errors.New("must: watch gave up on " + key)
}
'''

MUST4_SERVER = '''// Package app wires the service from its settings.
package app

import (
	"strings"
	"time"

	"example.com/must"
)

// valuer is the part of must.Source the app reads from.
type valuer interface {
	Value(key string) (string, error)
}

// Server holds the HTTP server settings.
type Server struct {
	Host    string
	Port    int
	Workers int
}

// LoadServer reads the server settings.
func LoadServer() Server {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})
	host, err := src.Value("HOST")
	if err != nil {
		host = "localhost"
	}
	port, _ := src.Raw("PORT").(int)
	workers, _ := src.Raw("WORKERS").(int)
	return Server{Host: host, Port: port, Workers: workers}
}

// Mode returns the run mode, defaulting to "prod" when unset.
func Mode(v valuer) string {
	mode, err := v.Value("MODE")
	if err != nil && strings.Contains(err.Error(), "missing key") {
		return "prod"
	}
	return mode
}

// WatchMode reports run-mode changes to onChange.
func WatchMode(onChange func(string)) error {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})
	return must.Watch(src, "MODE", time.Second, 3, onChange)
}
'''

MUST4_STORE = '''package app

import (
	"strings"
	"time"

	"example.com/must"
)

// Store holds the database settings.
type Store struct {
	DSN     string
	Pool    int
	Replica string
}

// LoadStore reads the database settings.
func LoadStore() (Store, error) {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})
	dsn, err := src.Value("DB_DSN")
	if err != nil {
		if strings.Contains(err.Error(), "missing key") {
			dsn = "postgres://localhost/app"
		} else {
			return Store{}, err
		}
	}
	pool, _ := src.Raw("DB_POOL").(int)
	replica, ok, err := src.Lookup("DB_REPLICA")
	if err != nil {
		return Store{}, err
	}
	if !ok {
		replica = dsn
	}
	return Store{DSN: dsn, Pool: pool, Replica: replica}, nil
}

// WatchDSN reports DSN changes to onChange.
func WatchDSN(onChange func(string)) error {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})
	return must.Watch(src, "DB_DSN", time.Second, 3, onChange)
}
'''

MUST4_DUMP = '''package app

import (
	"fmt"
	"strings"

	"example.com/must"
)

// Dump renders every setting as KEY=VALUE lines.
func Dump() string {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})
	var b strings.Builder
	keys := src.Keys()
	for keys.Next() {
		v, err := src.Value(keys.Key())
		if err != nil {
			continue
		}
		fmt.Fprintf(&b, "%s=%s\\n", keys.Key(), v)
	}
	return b.String()
}

// Prefixed returns the keys that start with prefix.
func Prefixed(prefix string) []string {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})
	var out []string
	keys := src.Keys()
	for keys.Next() {
		if strings.HasPrefix(keys.Key(), prefix) {
			out = append(out, keys.Key())
		}
	}
	return out
}

// Timeout returns the request timeout in seconds.
func Timeout() int {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})
	t, _ := src.Raw("TIMEOUT").(int)
	if t == 0 {
		t = 30
	}
	return t
}
'''

MUST4_APP_TEST = '''package app

import "testing"

type fakeValuer struct {
	vals map[string]string
	err  error
}

func (f fakeValuer) Value(key string) (string, error) {
	if f.err != nil {
		return "", f.err
	}
	return f.vals[key], nil
}

func Test_Mode(t *testing.T) {
	t.Run("set", func(t *testing.T) {
		// --- Given ---
		v := fakeValuer{vals: map[string]string{"MODE": "dev"}}

		// --- When ---
		have := Mode(v)

		// --- Then ---
		if have != "dev" {
			t.Errorf("have %q, want %q", have, "dev")
		}
	})
}
'''

MUST4_FEED = '''// Package feed polls the upstream feeds named in the settings.
package feed

import (
	"time"

	"example.com/must"
)

// valuer is the part of must.Source the feed reads from.
type valuer interface {
	Value(key string) (string, error)
}

// URLs returns the feed URLs, one per FEED_* key.
func URLs() []string {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})
	var urls []string
	keys := src.Keys()
	for keys.Next() {
		u, err := src.Value(keys.Key())
		if err != nil {
			continue
		}
		urls = append(urls, u)
	}
	return urls
}

// Interval returns the poll interval read from v.
func Interval(v valuer) time.Duration {
	s, err := v.Value("FEED_INTERVAL")
	if err != nil {
		s = "1m"
	}
	d, err := time.ParseDuration(s)
	if err != nil {
		return time.Minute
	}
	return d
}

// Agent returns the user agent, falling back to a fixed name.
func Agent() string {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})
	agent, ok, err := src.Lookup("FEED_AGENT")
	if err != nil || !ok {
		agent = "feedbot"
	}
	return agent
}

// WatchURLs reports feed list changes to onChange.
func WatchURLs(onChange func(string)) error {
	src := must.Load(must.Options{Dir: "conf", Ext: ".env", Strict: false})
	return must.Watch(src, "FEED_URLS", time.Second, 3, onChange)
}
'''

MUST4_FEED_TEST = '''package feed

import (
	"errors"
	"testing"
	"time"
)

type stubValuer map[string]string

func (s stubValuer) Value(key string) (string, error) {
	v, ok := s[key]
	if !ok {
		return "", errors.New("must: missing key " + key)
	}
	return v, nil
}

func Test_Interval(t *testing.T) {
	t.Run("default", func(t *testing.T) {
		// --- Given ---
		v := stubValuer{}

		// --- When ---
		have := Interval(v)

		// --- Then ---
		if have != time.Minute {
			t.Errorf("have %v, want %v", have, time.Minute)
		}
	})
}
'''


def case_terse():
    name = "reshape--terse-output"
    files = {
        "go.mod": go_mod("example.com/app",
                         "\nrequire example.com/must v0.0.0\n\n"
                         "replace example.com/must => ./third_party/must\n"),
        "third_party/must/go.mod": go_mod("example.com/must"),
        "third_party/must/must.go": MUST4_LIB,
        "app/server.go": MUST4_SERVER,
        "app/store.go": MUST4_STORE,
        "app/dump.go": MUST4_DUMP,
        "app/app_test.go": MUST4_APP_TEST,
        "internal/feed/feed.go": MUST4_FEED,
        "internal/feed/feed_test.go": MUST4_FEED_TEST,
    }
    graders = {
        "b1-opens-on-headline": g_regex(
            r"^\s*(?:#[^\n]*\n+\s*)?(?:[^\n]*(?:grep|language server|LSP)[^\n]*\n+\s*)?[^\n|]*\bmust\b[^\n|]*\b\d+\s+uses\b",
            flags="i"),
        "b1-no-preamble": g_regex(
            r"^\s*(I'll|I will|Let me|I've|I have|I'm|Reading|First,|Now|Okay|OK,|Sure|Here's|Here is|Done|Mapping|Analy[sz])",
            match="not_contains"),
        "b1-table-follows-headline": g_regex(
            r"\b\d+\s+uses\b[^\n]*\n(?:[^|\n][^\n]*\n|\s*\n){0,4}\s*\|\s*#\s*\|", flags="i"),
        "b2-structural-not-hidden": g_llm(
            "Either one of the reported proposals is a structural change (absorb-the-sequence, "
            "move-responsibility-upstream, invert-control, split-the-god-func, iterator, or "
            "expose-the-interface), or the reply says in one line that a structural option "
            "was considered and names what displaced it."),
        "b2-cap-three-rows": g_regex(r"(?m)^\|\s*\d+\s*\|", match="count:3"),
        "b3-no-closing-summary": g_regex(
            r"(?im)^#*\s*\**\s*(summary|recap|in summary|to summari[sz]e|overall)\b",
            match="not_contains"),
        "b3-one-section-per-proposal": g_regex(r"(?m)^#{2,4}\s*\d+[.)]", match="count:3"),
    }
    graders.update(READ_ONLY)
    write_case(name, "/go:reshape must max=3", graders, files, tags=["sec:reshape:usage"])


# ===================================================== case 5: tidy, clean

TIDY_LIB = '''// Package tidy normalizes user-entered text.
package tidy

import "strings"

// Clean trims s and collapses runs of whitespace to one space.
func Clean(s string) string { return strings.Join(strings.Fields(s), " ") }

// Slug returns a lowercase, dash-separated form of s.
func Slug(s string) string { return strings.ToLower(strings.Join(strings.Fields(s), "-")) }

// Words splits s into its whitespace-separated words.
func Words(s string) []string { return strings.Fields(s) }
'''

TIDY_POST = '''// Package blog models blog posts.
package blog

import "example.com/tidy"

// Post is a blog post.
type Post struct {
	Title string
	Slug  string
	Body  string
	Tags  []string
}

// NewPost builds a post from raw form input.
func NewPost(title, body, tags string) Post {
	t := tidy.Clean(title)
	return Post{
		Title: t,
		Slug:  tidy.Slug(t),
		Body:  tidy.Clean(body),
		Tags:  tidy.Words(tags),
	}
}

// Rename changes the post title and its slug.
func (p *Post) Rename(title string) {
	p.Title = tidy.Clean(title)
	p.Slug = tidy.Slug(p.Title)
}
'''

TIDY_SEARCH = '''package blog

import (
	"strings"

	"example.com/tidy"
)

// Matches reports whether the post contains every word of query.
func (p Post) Matches(query string) bool {
	body := strings.ToLower(p.Body)
	for _, w := range tidy.Words(strings.ToLower(query)) {
		if !strings.Contains(body, w) {
			return false
		}
	}
	return true
}

// Titles returns the cleaned titles of raw.
func Titles(raw []string) []string {
	out := make([]string, 0, len(raw))
	for _, r := range raw {
		out = append(out, tidy.Clean(r))
	}
	return out
}

// Anchor returns the in-page anchor for a heading.
func Anchor(heading string) string { return "#" + tidy.Slug(heading) }
'''


def case_restraint():
    name = "reshape--restraint-on-an-api-that-is-fine"
    files = {
        "go.mod": go_mod("example.com/blog",
                         "\nrequire example.com/tidy v0.0.0\n\n"
                         "replace example.com/tidy => ./third_party/tidy\n"),
        "third_party/tidy/go.mod": go_mod("example.com/tidy"),
        "third_party/tidy/tidy.go": TIDY_LIB,
        "blog/post.go": TIDY_POST,
        "blog/search.go": TIDY_SEARCH,
    }
    uses = sum(len(re.findall(r"\btidy\.[A-Z]", files[f])) for f in ("blog/post.go", "blog/search.go"))
    assert uses == 9, uses
    graders = {
        "b1-says-fits": g_llm("The reply says the library's API fits its consumer and "
                              "makes no proposals."),
        "b1-no-table": g_regex(r"(?m)^\|\s*#\s*\|", match="not_contains"),
        "b2-names-absent": g_llm("The reply names specific kinds of friction it looked "
                                 "for and did not find (for example repeated wrappers, "
                                 "inline config building, re-declared interfaces, or "
                                 "error-string matching)."),
        "b3-no-low-label": g_regex(r"\bLow\b", match="not_contains"),
        "b3-declines-reach-1": g_llm("The reply names at least one specific API shape that "
                                     "would help only a single use (such as a batch or "
                                     "variadic Clean for the loop in Titles) and declines "
                                     "it rather than proposing it."),
        "b4-header-count": g_regex(r"(?m)^[^\n|]*\btidy\b[^\n|]*\b9\s+uses\b"),
    }
    graders.update(READ_ONLY)
    write_case(name, "/go:reshape tidy", graders, files)


if __name__ == "__main__":
    case_ranked()
    case_library()
    case_external()
    case_terse()
    case_restraint()
