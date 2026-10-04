#!/usr/bin/env python3
"""Generate go/evals/reshape--* native eval cases. Re-runnable; owns only reshape--*."""
import os
import re
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
EVALS = os.path.join(ROOT, "go/evals")

ENGLISH = "The user writes English; reply in English.\n"
NOTICE = "Ignore any trailing policy notice. "

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


# ===================================================== case 5: tidy, clean


if __name__ == "__main__":
    case_ranked()
    case_library()
    case_external()
