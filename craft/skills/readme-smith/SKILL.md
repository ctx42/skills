---
name: readme-smith
description: >
  Authors and improves README.md files for software projects, grounded in
  the actual repo — never fabricates facts and verifies the commands it
  ships. Use when asked to create, write, draft, review, or improve a README
  or a project's front-page documentation.
---

# readme-smith

Forge and repair a project's `README.md`. Pick the mode from the request:

- **Create** — no usable README exists, or the user asks for a new/rewritten one.
- **Improve** — the user names an existing README to review or upgrade.

If ambiguous, ask one question: create new or improve existing?

README structure and style come from
[`references/template.md`](references/template.md) *(eager: read once per run)* —
the section blueprint, the style rules (emoji, GFM, admonitions, logo, excluded
sections), and the self-check checklist. Every decision defers to it.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. The README is the payload — write it in full;
do not also paste it back into chat.

## Non-negotiables (both modes)

These two bite before drafting; `references/template.md` (loaded every run)
holds the full rules and the Verify checklist re-checks them.

- **Never fabricate.** A claim, command, version, or number you cannot verify
  from the repo or the user is a gap. Ask; if still unknown, leave an explicit
  `<!-- TODO: … -->` marker. Never invent install steps or benchmark figures.
- **Verify commands.** Every install and quickstart command you ship must be
  executed and made to pass (see Verify). A command you cannot run is marked, not
  guessed.

Read paths from the manifest (never an org name or sibling repo), keep Go module
vs import distinct, and follow the excluded-section and root-vs-member rules — all
per `references/template.md`.

## Go example injection (gomake)

When the project is **Go** and examples belong in the README, read
[references/gomake.md](references/gomake.md) *(on-demand)* and follow it: if the
`:project:doc-eg` gomake target exists, examples are generated from testable
`Example…` functions and injected — never hand-written — so the README cannot
drift from code that compiles.

## Create mode

1. **Scan the repo.** Ground everything in real code. Read: package manifests
   (`package.json`, `go.mod`, `pyproject.toml`, `Cargo.toml`, …), the entrypoint
   / main command, any existing docs, `examples/`, CI config, and `.github/` or
   `assets/` for a logo/icon or demo media. Note the language, install method,
   run command, and public surface. Decide **root vs member** (see
   Non-negotiables): a repo root with member packages that have their own READMEs
   is a root README; a package subdir is a member. When writing a member, read
   the sibling members and match their section set, prerequisites format, and
   tone.
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
     a nav line and a TOC block; its entries match headings; no two headings
     share the same text (colliding anchors). Root/member correct: a member has
     no badges and no `## License`, and does not link up to the root; the root
     indexes its members.
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
- [ ] No two headings share the same text (GitHub auto-suffixes the duplicate's
      anchor, breaking links) — e.g. not two `### As a library`.
- [ ] Badges and any `## License` section appear on the root/main README only; a
      member README has neither and does not link up to the root, while the root
      links down to every member.
- [ ] Import/install path matches the manifest; badges point at the real hosting
      remote (`git remote -v`) and a target that resolves; no visibility guessed
      or `GOPRIVATE` added from the host URL (see Non-negotiables).
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

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/craft/readme-smith.md` when this
directory is read-only. On a correction or self-caught mistake, first draft the
lesson **generically** — a rule for any README, not tied to the one file at hand
— and present it for the user's approval. Only once approved, append the
one-line rule to whichever is writable (creating it) and report where. Never
append an unapproved lesson.
