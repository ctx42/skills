---
name: readme-smith
description: >
  Authors and upgrades README.md files for software projects. Create mode scans
  the repo, interviews the user only for gaps it cannot infer, and drafts a
  README to a distilled house structure (header/logo, badges, overview,
  features, install, usage, config); improve mode audits an existing README
  against the same rules and fixes it on confirmation. Enforces GFM, GitHub
  admonitions, restrained emoji, no fabricated facts, and verifies that
  install/quickstart commands actually run. Use when asked to create, write,
  draft, review, or improve a README or a project's front-page documentation.
---

# readme-smith

Forge and repair a project's `README.md`. Pick the mode from the request:

- **Create** — no usable README exists, or the user asks for a new/rewritten one.
- **Improve** — the user names an existing README to review or upgrade.

If ambiguous, ask one question: create new or improve existing?

The single source of truth for structure and style is
[`references/template.md`](references/template.md) — the section blueprint, the
style rules (emoji, GFM, admonitions, logo, excluded sections), and the
self-check checklist. Read it once per run. Every decision defers to it.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. The README is the payload — write it in full;
do not also paste it back into chat.

## Non-negotiables (both modes)

- **Never fabricate.** A claim, command, version, or number you cannot verify
  from the repo or the user is a gap. Ask; if still unknown, leave an explicit
  `<!-- TODO: … -->` marker. Never invent install steps or benchmark figures.
  The path comes from the manifest (`go.mod` module, `package.json` name, …) and
  `git remote -v` — never from an org name or a sibling repo. For Go, `go get`,
  badges, and pkg.go.dev take the module; a Go `import` takes the package (module
  + subdir). Do not claim a repo's visibility or add `GOPRIVATE`/auth steps from
  its host URL alone; the host does not reveal public vs private.
- **Excluded sections.** Do not author License, Contributing, Changelog, Code of
  Conduct, or Security as README content — dedicated files own them. Link to
  those files in one line at most.
- **Verify commands.** Every install and quickstart command you ship must be
  executed and made to pass (see Verify). A command you cannot run is marked, not
  guessed.

## Go example injection (gomake)

When the project is **Go**, examples belong in the README, and the
`:project:doc-eg` gomake target is available, generate examples from runnable
code instead of hand-writing snippets — so the README can never drift from code
that compiles. This is the "verify commands" rule applied to examples: each
example is proven by `go test`, not by inspection.

1. **Detect.** Run `gomake --help` and confirm `:project:doc-eg` is listed. If
   absent, hand-write examples as usual.
2. **Author runnable examples first.** Write them as Go testable `Example…`
   functions in `_test.go`; run `go test ./...` until they pass.
3. **Mark the spots.** At each place an example belongs, write a one-line marker
   keyed as `<!-- gmdoceg:<relpath>/<ExampleFuncName> -->`, where `relpath` is the
   example package's directory relative to the Markdown file (e.g.
   `pkg/foo/ExampleNew` for a root README; drop the prefix only when the
   `_test.go` sits in the file's own directory) — immediately above an empty (or
   existing) ```go fence. See `references/template.md` for the exact form.
4. **Inject with gomake.** Run `gomake :project:doc-eg`; it fills each marked
   fence with the matching `Example…` function's body and `// Output:` block.
5. **Never hand-edit injected fences or ship unbacked snippets.** To change an
   injected example, edit its `Example…` function and re-run the target. A `go`
   snippet not backed by a passing `Example…` function is drift.

## Create mode

1. **Scan the repo.** Ground everything in real code. Read: package manifests
   (`package.json`, `go.mod`, `pyproject.toml`, `Cargo.toml`, …), the entrypoint
   / main command, any existing docs, `examples/`, CI config, and `.github/` or
   `assets/` for a logo/icon or demo media. Note the language, install method,
   run command, and public surface.
2. **Ask only the gaps.** From the scan, list what code cannot reveal —
   positioning (what problem, for whom), audience, notable features to lead with,
   roadmap. Ask those in one batched round. Do not ask what the repo already
   answers.
3. **Draft from the blueprint.** Follow the section order and style rules in
   `references/template.md`. Include only sections the project actually needs;
   omit empty ones. Use the repo's real project name, commands, and paths. Use
   an existing logo/demo if found; otherwise skip it — do not fabricate one. For
   Go example content, prefer gomake injection (see Go example injection).
4. **Verify** (see below), fixing the draft until it passes.
5. **Write** `README.md` at the repo root (or the path the user gave). State the
   path and any remaining `TODO` markers. Do not paste the file back.

## Improve mode

Audit the named README against `references/template.md`, report, then fix on
confirmation. Reasoning only until the user approves — no edits during the audit.

1. **Resolve the target.** State the exact README path in scope. Scan the repo
   (as in Create step 1) so the audit is grounded in real code, not just prose.
2. **Audit** against `references/template.md`, checking:
   - **Structure** — sections present and ordered per the blueprint; no excluded
     sections authored as content; exactly one navigation aid (or none), not both
     a nav line and a TOC block; its entries match headings.
   - **Accuracy** — commands, versions, and paths match the repo; no stale or
     fabricated claims; badges reference verifiable facts.
   - **Style** — GFM used well, code fences declare a language, admonitions valid
     and non-decorative, emoji restrained, logo/header well-formed.
   - **Completeness** — a newcomer can install, run, and understand the project;
     gaps are real gaps, not guesses. For a Go project with `:project:doc-eg`,
     hand-written example snippets are a finding — they belong in gomake-injected
     regions (see Go example injection).
3. **Report only.** Group findings **Blocker / Should-fix / Nit**. Each: the
   file location, the problem in one line, the rule from `references/template.md`
   it breaks, and a minimal fix. End with a verdict and per-severity counts.
4. **Fix on confirmation.** Apply approved findings, then **Verify**. State what
   changed; do not paste the whole file back.

## Verify

Run before finishing in either mode. Fix the README until every check passes.

Inspect (static):

- [ ] Every internal link and nav/TOC anchor resolves to a real heading or file.
- [ ] Every code fence declares a language.
- [ ] No fence line scrolls sideways on GitHub (≤ ~100 chars); long output split,
      not dumped on one wide line.
- [ ] Exactly one navigation aid (a nav line XOR a `<!-- TOC -->` block), or none
      — never both; its entries match the actual headings.
- [ ] Import/install path matches the manifest; badges point at the real hosting
      remote (`git remote -v`) and a target that resolves; no visibility guessed
      or `GOPRIVATE`/auth step added from the host URL alone.
- [ ] Admonition syntax is valid GitHub form (`> [!NOTE]`, `> [!TIP]`, …).
- [ ] No raw HTML tags (`<div>`, `<img>`, `<details>`, …); plain GFM only. HTML
      comments (`<!-- TOC -->`, `<!-- gmdoceg:… -->`) are the only exception.
- [ ] No excluded section authored as content; emoji restrained (no per-heading
      decoration); badges reference verifiable facts only.
- [ ] No fabricated command, version, or number; every gap is a `TODO` marker.

Run (dynamic):

- [ ] Execute the install and quickstart commands exactly as written. Make them
      pass, or mark the blocking prerequisite. Never ship an unrun command.
      Running project code may prompt for permission and need a toolchain — if
      the environment cannot run it, say so and leave the command flagged rather
      than claiming it works.

## Self-application

`readme-smith` obeys the repo authoring standard (strict-portable frontmatter, a
README with ≥ 3 evals, references one level deep). When you change this skill,
re-audit it with `skill-smith` in improve mode.
