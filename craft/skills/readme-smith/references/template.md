# README Blueprint & Style

The structure and style `readme-smith` writes and audits against, distilled
from strong open-source READMEs. Include only the sections a project needs;
omit empty ones. Order is the default, not a straitjacket.

## Contents

- Root README vs member README
- Section blueprint
- Header snippet
- Navigation (one aid, or none)
- Style rules
- Admonitions
- Excluded sections

## Root README vs member README

A repository with more than one package has one root/main README and one member
README per package. They are different documents:

- Root/main README: the only place for a badges row and a `## License` section.
  An index, not a project page — a Packages table (plus any target/command
  tables) linking down to every member, with no fixed section order. Covers
  installing the whole (e.g. the binary), not each package's `go get`.
- Member README: no badges, no License section, no link up to the root. Covers
  its one package in depth (overview, features, prerequisites, usage,
  configuration); links sideways to a sibling only when it uses it.

Detect: a README is the root form when it sits at the repo root and the repo
has member packages with their own READMEs; otherwise it is a member. A
single-package repo has only the root form, which also carries the full project
page.

Before writing a member README, read the sibling members and match their
section set, prerequisites format, and tone — a repo's READMEs read as a set.

## Section blueprint

1. Header: badges row (root only), the project name as `#` H1, a one-line
   tagline (what it is + for whom), a logo/demo image (plain `![](…)`) only if
   the file exists in the repo, and at most one navigation aid (see Navigation).
2. Overview / Why: 1–3 short paragraphs — the problem it solves, what it is,
   who it's for. Lead here, never with setup.
3. Features: concise bullets of what it does. Capabilities only; mechanics
   belong to Usage, so cut a bullet that re-narrates a run step.
4. Prerequisites: required toolchain/runtime versions, accounts, services. Omit
   if none.
5. Installation: copy-pasteable commands, one block per supported method
   (package manager, binary, source). Enumerate the methods from the tool's own
   docs and manifests; a method absent from a sibling README still exists.
6. Usage: the smallest working example first (quickstart), then deeper
   subsections. Real, runnable commands only.
7. Configuration: flags, env vars, or config-file keys; a table reads well.
8. Examples: end-to-end scenarios, if Usage doesn't cover them.
9. Resources: fuller docs, related projects, background.
10. FAQ / Troubleshooting: common errors and fixes.

## Header snippet

Badges on their own lines, then title, tagline, and image. Adapt; drop any
line whose fact you cannot verify (see Style rules: Badges).

```markdown
[![Go](ci-badge-url)](ci-link)
[![Go Reference](pkg.go.dev-badge-url)](pkg.go.dev-link)
[![Go Version](go-version-badge-url)](go.mod)
[![License](license-badge-url)](LICENSE.md)

# ProjectName

One-line tagline: what it is and who it's for.

![ProjectName](doc/logo.png)
```

## Navigation (one aid, or none)

A README gets at most one navigation aid — never a nav line and a TOC block
together; two is the most common breakage. Choose by length and host:

- Short (fits ~1–2 screens): none — the headings are the navigation.
- Longer, GitHub-hosted: none — GitHub auto-generates a heading TOC; add a
  manual one only if the user asks.
- Longer, other host (Bitbucket, GitLab, self-hosted): one aid — a one-line nav
  of top sections or a generated TOC block, not both:

```markdown
[Overview](#overview) • [Features](#features) • [Install](#installation) • [Usage](#usage)
```

```markdown
<!-- TOC -->
<!-- TOC -->
```

Every anchor must resolve to a real heading anchor (lowercase, spaces →
hyphens, punctuation dropped), so no two headings may share the same text
(`### As a library` twice collides — rename one `Use as a library`). If the
repo already carries a `<!-- TOC -->` block (IDE- or tool-generated), keep it
and add nothing.

## Style rules

- GFM throughout: fenced code blocks that always declare a language; tables for
  options/config; task lists where useful.
- No raw HTML tags: never `<div>`, `<img>`, `<p>`, `<center>`, `<br>`,
  `<details>`, or any rendered tag — GFM cannot center or size content, so a
  plain left-aligned header is correct. HTML comments (`<!-- TOC -->`,
  `<!-- gmdoceg:… -->`) render nothing and are fine.
- Emoji restrained: default to none; at most a single accent in the title and
  light accents on feature bullets if the project's tone invites it, never one
  per heading or per line.
- Real content only: project name, commands, paths, versions, and numbers come
  from the repo. A fact you cannot verify is a `<!-- TODO: … -->` marker, never
  a guess — no invented install steps or benchmark figures.
- Module path vs import path: read the base path from the manifest (`go.mod`
  module directive, `package.json` name, `pyproject.toml`, …) and cross-check
  `git remote -v`; never derive it from an org name or a sibling repo
  (`bitbucket.org/acme/foo` ≠ `github.com/acme/foo`). In Go, `go get`, badges,
  and pkg.go.dev target the module (`github.com/acme/foo`); an `import` targets
  the package — module + subdir (`github.com/acme/foo/pkg/foo`).
- Visibility: never infer public/private from the host — `bitbucket.org`,
  `gitlab.com`, or self-hosted is not evidence of "private," `github.com` not
  of "public." Add no `GOPRIVATE`/auth step unless the user confirms the repo
  is private.
- No horizontal scroll: a code fence scrolls sideways on GitHub past its box
  width; keep every fence line ≤ ~80 chars (hard cap ~100). Break long commands
  with `\`, long strings across lines, and long example output into pieces.
- Badges: each points at the project's real hosting remote (`git remote -v`)
  and a fact that exists — CI that runs there, a published package, the
  declared license/runtime. Omit any whose URL you cannot confirm resolves;
  never invent one from an org name.
- Concise and skimmable: short paragraphs, meaningful headings, examples over
  prose — never a wall of prose where a table or short example would serve.

## Admonitions

GitHub admonitions for genuine callouts, not decoration. Five types, each a
`>`-prefixed blockquote: `[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`,
`[!CAUTION]`.

## Excluded sections

Do not author these as README sections — dedicated files own them; link to the
file in one line at most if genuinely helpful:

- License → `LICENSE` / `LICENSE.md` (the root/main README alone may keep a
  `## License` section; see Root README vs member README)
- Contributing → `CONTRIBUTING.md`
- Changelog → `CHANGELOG.md`
- Code of Conduct → `CODE_OF_CONDUCT.md`
- Security policy → `SECURITY.md`
