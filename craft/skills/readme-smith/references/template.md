# README Blueprint & Style

The canonical structure and style `readme-smith` writes and audits against.
Distilled from strong open-source READMEs. Include only the sections a project
actually needs; omit empty ones. Order is the default, not a straitjacket.

## Contents

- Section blueprint
- Header snippet
- Navigation (one aid, or none)
- Go example markers (gomake)
- Style rules
- Admonitions
- Excluded sections
- Anti-patterns

## Section blueprint

1. **Header** — a badges row (each badge on its own line), the project name as
   `#` H1, a one-line tagline (what it is + for whom), and a logo/demo image
   (plain `![](…)`) if the repo has one. Plain GFM, left-aligned — no wrapping
   `<div>`. Add a single navigation aid only per **Navigation** below.
2. **Overview / Why** — 1–3 short paragraphs: the problem it solves, what it is,
   who it's for. Lead here, not with setup.
3. **Features** — a concise bulleted list of what it does. Sparing emoji accents
   at most; not one per line.
4. **Prerequisites** — required toolchain/runtime versions, accounts, services.
   Omit if none.
5. **Installation** — copy-pasteable install commands, one block per supported
   method (package manager, binary, source).
6. **Usage** — the smallest working example first (quickstart), then deeper
   subsections. Real, runnable commands only.
7. **Configuration** — flags, env vars, or config-file keys. A table reads well.
8. **Examples** — concrete end-to-end scenarios, if usage doesn't cover them.
9. **Resources** — links to fuller docs, related projects, background.
10. **FAQ / Troubleshooting** — common errors and fixes.

## Header snippet

Plain GFM only — **no raw HTML tags** (`<div>`, `<img>`, `<p align>`,
`<center>`, `<br>`). GFM cannot center or size content; a plain left-aligned
header is correct. HTML *comments* are fine — they render nothing and carry the
`<!-- TOC -->` and `<!-- gmdoceg:… -->` markers.

Adapt; drop any line whose fact you cannot verify. Badges on their own lines at
the top, then the title and tagline. Each badge must point at the project's real
hosting remote (`git remote -v`) and a fact that exists — CI that runs there, a
published package, the declared license. Omit any badge whose URL you cannot
confirm resolves; never invent one from an org name. Do **not** infer a repo's
visibility (public/private) from its host — a `bitbucket.org`/`gitlab.com`/
self-hosted URL is not evidence of "private," and a `github.com` URL is not
evidence of "public." Add a logo with a plain image link only if the file
exists in the repo.

```markdown
[![CI](badge-url)](link)
[![Go Report Card](badge-url)](link)
[![GoDoc](badge-url)](link)

# ProjectName

One-line tagline: what it is and who it's for.

![ProjectName](doc/logo.png)
```

## Navigation (one aid, or none)

A README gets **at most one** navigation aid — never a nav line *and* a TOC
block. Two is the most common breakage. Choose by length and host:

- **Short** (fits ~1–2 screens): none. The headings are the navigation.
- **Longer, GitHub-hosted:** none needed — GitHub auto-generates a heading TOC.
  Add a manual one only if the user asks.
- **Longer, other host** (Bitbucket, GitLab, self-hosted): one aid. Either a
  one-line nav of top sections *or* a generated TOC block — pick one:

```markdown
[Overview](#overview) • [Features](#features) • [Install](#installation) • [Usage](#usage)
```

```markdown
<!-- TOC -->
<!-- TOC -->
```

Whichever you use, every anchor must resolve to a real heading. If the repo
already carries a `<!-- TOC -->` block (IDE- or tool-generated), keep that one
and do not also add a nav line.

## Go example markers (gomake)

When the `:project:doc-eg` gomake target exists (see the skill's *Go example
injection* workflow), do not hand-write Go example snippets. Author each as a
testable `Example…` function in `_test.go`, then place a one-line marker where
it belongs, directly above a `go` fence:

````markdown
Use a buffer for stdout to capture program output without touching `os.Stdout`:

<!-- gmdoceg:pkg/foo/ExampleNew -->
```go
```
````

`gomake :project:doc-eg` fills each fence with the named function's body and its
`// Output:` block. The marker key is `<relpath>/<FuncName>`: the exact `Example…`
function name (Go conventions: `ExampleType_method`, `ExampleFunc_suffix`)
prefixed by the example package's directory **relative to the Markdown file** —
e.g. `pkg/foo/ExampleNew` for a README at the repo root. Drop the prefix only
when the `_test.go` lives in the same directory as the file (`relpath` `.`). A
bare `<!-- gmdoceg:ExampleNew -->` silently no-ops when the example is in a
subpackage. One marker per example; the tool refreshes the fence in place —
never hand-edit the fence content, edit the function and re-run.

The injected body *and its `// Output:`* land verbatim in the fence, so the
function must obey **No horizontal scroll** (above): keep its lines short and
split long output rather than printing one wide line. A dump like
`fmt.Printf("%q\n", wireBytes)` overflows — print the value in pieces (e.g. loop
over `bytes.Split(b, []byte("\r\n"))`, one `%q` per line) instead.

## Style rules

- **GFM throughout.** Fenced code blocks that **always declare a language**;
  tables for options/config; task lists where useful.
- **No raw HTML tags.** Plain GFM only — never emit `<div>`, `<img>`, `<p>`,
  `<center>`, `<br>`, `<details>`, or any rendered tag, not even for a centered
  header. Accept plain left-aligned markdown instead. The only HTML allowed is
  *comments* (`<!-- TOC -->`, `<!-- gmdoceg:… -->`), which render nothing.
- **Emoji: restrained.** Default to none. At most a single accent in the title
  and light accents on feature bullets if the project's tone invites it. Never
  decorate every heading.
- **Real content only.** Project name, commands, and paths come from the repo. A
  fact you can't verify is a `<!-- TODO: … -->` marker, never a guess.
- **Module path vs import path.** Read the base path from the manifest (`go.mod`
  module directive, `package.json` name, `pyproject.toml`, …); cross-check
  `git remote -v`; never derive it from an org name or a sibling repo
  (`bitbucket.org/acme/foo` ≠ `github.com/acme/foo`). For Go, keep the two
  distinct: `go get`, badges, and pkg.go.dev target the **module**
  (`github.com/acme/foo`); a Go `import` targets the **package** — module +
  subdir (`github.com/acme/foo/pkg/foo`). Add no `GOPRIVATE`/auth step unless the
  user confirms the repo is private.
- **No horizontal scroll.** A rendered code fence scrolls sideways on GitHub past
  its box width; keep every line in a fence readable (aim ≤ ~80, hard cap ~100
  chars) so it wraps in prose but fits in code. Break long commands with `\`,
  long strings across lines, and long example output into shorter pieces.
- **Badges** reference verifiable facts only (CI that exists, a published
  package, the declared license/runtime) on the real hosting remote. Omit any
  whose URL you cannot confirm resolves.
- **Navigation anchors** must resolve to real heading anchors (lowercase, spaces
  → hyphens, punctuation dropped). Exactly one nav aid, or none (see Navigation).
- **Concise and skimmable.** Short paragraphs, meaningful headings, examples over
  prose.

## Admonitions

Use GitHub admonition syntax for genuine callouts, not decoration:

```markdown
> [!NOTE]
> Useful information the reader should know.

> [!TIP]
> A helpful shortcut.

> [!IMPORTANT]
> Essential to success.

> [!WARNING]
> Risk of a mistake.

> [!CAUTION]
> Risk of a damaging or irreversible outcome.
```

## Excluded sections

Do **not** author these as README sections — dedicated files own them. Link to
the file in one line at most if genuinely helpful.

- License → `LICENSE` / `LICENSE.md`
- Contributing → `CONTRIBUTING.md`
- Changelog → `CHANGELOG.md`
- Code of Conduct → `CODE_OF_CONDUCT.md`
- Security policy → `SECURITY.md`

## Anti-patterns

- Raw HTML tags (`<div align="center">`, `<img>`, `<details>`) — plain GFM only.
- Two navigation aids (a nav line *and* a `<!-- TOC -->` block) — pick one.
- Setup before the reader knows what the project is.
- Emoji on every heading; badge walls of unverifiable facts.
- Code fences with no language; nav links to missing anchors.
- Code fences with lines long enough to scroll sideways on GitHub.
- Import/install path guessed from the org or a sibling repo instead of read
  from the manifest (`bitbucket.org/x` silently rewritten to `github.com/x`).
- Go `import` shown as the bare module path when the package lives in a subdir.
- Assuming a repo is private (adding `GOPRIVATE`/auth notes) from its host URL.
- Invented install steps, versions, or benchmark numbers.
- Re-authoring license/contributing/changelog content that lives elsewhere.
- Walls of prose where a table or short example would serve.
