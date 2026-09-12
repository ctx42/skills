---
name: readme-smith
description: >
  Authors and improves README.md files for software projects, grounded in
  the actual repo — never fabricates facts and verifies the commands it
  ships. Use when asked to create, write, draft, review, or improve a README
  or a project's front-page documentation.
argument-hint: "[create|improve] [<readme-path>]"
---

# readme-smith

Create and improve a project's `README.md`. Pick the mode from `$1` when given,
else from the request; `$2` (or the request) names the README path:

- Create — no usable README exists, or the user asks for a new/rewritten one.
- Improve — the user names an existing README to review or upgrade.

If ambiguous, ask one question: create new or improve existing?

Structure and style come from
[`references/template.md`](references/template.md) *(eager: read once per
run)*; every decision defers to it.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. The README is the payload — write it in full
to the file, state its path, and do not paste it back into chat.

## Non-negotiables (both modes)

- Never fabricate. A claim, command, version, or number you cannot verify from
  the repo or the user is a gap: ask, and if still unknown leave an explicit
  `<!-- TODO: … -->` marker.
- Verify commands. Execute every install and quickstart command you ship and
  make it pass (see Verify); a command you cannot run is marked, not guessed.

## Go example injection (gomake)

When the project is Go and examples belong in the README, read
[`references/gomake.md`](references/gomake.md) *(on-demand: Go project with
README examples)* and follow it: with a `:project:doc-eg` gomake target,
examples are injected from testable `Example…` functions, never hand-written.

## Create mode

1. Scan the repo. Ground everything in real code: package manifests
   (`package.json`, `go.mod`, `pyproject.toml`, `Cargo.toml`, …), the
   entrypoint / main command, existing docs, `examples/`, CI config, and
   `.github/` or `assets/` for a logo or demo media, and `.editorconfig`,
   `.markdownlint`, or `.prettierrc` for the Markdown wrap width. Note the
   language, every install or integration method the tool's own docs and
   manifests declare (never inferred from sibling READMEs), run command, and
   public surface. Decide root vs member README per `references/template.md`.

2. Ask only the gaps. List what code cannot reveal — positioning (what problem,
   for whom), audience, notable features to lead with, roadmap — and ask in one
   batched round. Do not ask what the repo already answers.

3. Draft from the blueprint in `references/template.md`. A fact neither the
   scan nor the answers yielded is a `<!-- TODO: … -->` marker, never a guess.
   For Go examples, prefer gomake injection (see Go example injection).

4. Verify (below), fixing the draft until it passes.

5. Write `README.md` at the repo root (or the path the user gave). State the
   path and any remaining `TODO` markers.

## Improve mode

No edits until the user approves the findings.

1. Resolve the target. State the exact README path in scope. Scan the repo (as
   in Create step 1) so the audit is grounded in code, not just prose.

2. Audit against `references/template.md`:
   - Structure — sections present and ordered per the blueprint; root/member,
     navigation, and excluded-section rules hold; no colliding headings.
   - Accuracy — commands, versions, paths, and badges match the repo; no stale
     or fabricated claims.
   - Style — fences declare a language, admonitions valid and non-decorative,
     emoji restrained, header plain GFM.
   - Completeness — a newcomer can install, run, and understand the project;
     gaps are real gaps, not guesses. In a Go project with `:project:doc-eg`,
     hand-written example snippets are a finding (see Go example injection).

3. Report only. Group findings Blocker / Should-fix / Nit; each names the
   location, the problem in one line, the `references/template.md` rule it
   breaks, and a minimal fix. End with a one-line verdict.

4. Fix on confirmation. Apply approved findings, then Verify. State what
   changed.

## Verify

Run before finishing in either mode; fix the README until every check passes.

Static — re-check the draft against `references/template.md` (Root vs member,
Navigation, Style rules, Excluded sections), then:

- [ ] Every internal link and nav/TOC anchor resolves to a real heading or file.
- [ ] Every code fence declares a language and no fence line exceeds ~100 chars
      (long output split across lines).
- [ ] Every gap is a `<!-- TODO: … -->` marker, not a guessed command, version,
      or number.
- [ ] Prose is wrapped and tables padded to the repo's `[*.md] max_line_length`
      (80 when unset), counted in characters, not bytes: an em dash is one
      column, so byte-based length checks over-report.

Dynamic:

- [ ] Execute the install and quickstart commands exactly as written and make
      them pass, or mark the blocking prerequisite. Never ship an unrun command;
      if the environment cannot run it (toolchain missing, permission denied),
      say so and leave it flagged rather than claiming it works.

## Self-application

`readme-smith` obeys the repo authoring standard. When you change this skill,
re-audit it with `skill-smith` in improve mode.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/craft/readme-smith.md` when this
directory is read-only. On a correction or self-caught mistake, first draft the
lesson **generically** — a rule for any README, not tied to the one file at hand
— and present it for the user's approval. Only once approved, append the
one-line rule to whichever is writable (creating it) and report where. Never
append an unapproved lesson.
