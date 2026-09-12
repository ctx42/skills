---
name: readme-smith
description: >
  Authors and improves README.md files for software projects, grounded in
  the actual repo — never fabricates facts and verifies the commands it
  ships. Use when asked to create, write, draft, review, or improve a README
  or a project's front-page documentation.
argument-hint: "[create|improve] [<readme-path>]"
license: MIT
---

# readme-smith

## Usage

```
/readme-smith <request>               infer create vs improve from the request (default)
/readme-smith create [<readme-path>]  scan the repo and draft a new README from real code
/readme-smith improve <readme-path>   audit an existing README; fix on confirmation
```

Create and improve a project's `README.md`. Pick the mode from the first token
of the invocation when it is a mode word, else from the request; the next token
(or the request) names the README path:

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
  the repo or the user is a gap: ask, and if still unknown mark it.
  - A fact the README *needs* and lacks (the license, the minimum runtime, the
    published install command) gets a `<!-- TODO: … -->` marker.
  - A claim the README merely *makes* and cannot support (a benchmark figure, a
    download count, "battle-tested") is deleted, not marked. A TODO asking
    someone to source an invented number preserves the invention.
- Verify commands. Run every install and quickstart command you ship (see
  Verify); a command you cannot run is marked, not guessed. Running it is the
  rule — passing is not always available, and a correct command the project has
  not caught up to yet is still the right command to ship.

## Go example injection (gomake)

When the project is Go, the README wants `go` example fences, and the *project*
uses gomake, read [`references/gomake.md`](references/gomake.md) *(on-demand:
Go project with README examples)* and follow it: examples are injected from
testable `Example…` functions, never hand-written.

`:doc:mce` is a gomake built-in, so it lists on any machine with gomake
installed — its presence says nothing about this project. Decide from the repo:
an existing `<!-- gmmce:… -->` marker, a gomake config, or a gomake step in CI.
Absent those, hand-write the examples rather than introducing a tool the
project's own contributors may not have.

Injection needs `Example…` functions, and those are Go source: they join the
test suite, CI, coverage, and the diff. Nobody asking for a README asked for
that, so it gets its own yes — the approval covering the README does not reach
it. Ask once per run, after the README work and before writing any `.go` file:
name each file, the functions going in it, and that it becomes part of the test
suite. On a no, hand-write the examples in create mode, or in improve mode
leave the finding reported and the README untouched — never write the file and
mention it afterwards.

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
     gaps are real gaps, not guesses. In a Go project with `:doc:mce`,
     hand-written example snippets are a finding (see Go example injection).

3. Report only. Group findings Blocker / Should-fix / Nit; each names the
   location, the problem in one line, the `references/template.md` rule it
   breaks, and a minimal fix. A gap only the user can close (the minimum
   runtime, whether the package is published, which remote is real) is a
   finding like any other, asked in its own line — improve mode has no separate
   question round. End with a one-line verdict; the verdict is the ask, so add
   no "shall I apply these?" after it.

4. Fix on confirmation. Apply approved findings, then Verify. State what
   changed.

## Verify

Run before finishing in either mode; fix the README until every check passes.

Static — re-check the draft against `references/template.md` (Root vs member,
Navigation, Style rules, Excluded sections), then:

- [ ] Every internal link and nav/TOC anchor resolves to a real heading or file.
- [ ] Every code fence declares a language and every fence line stays within
      the template's width (≤ ~80 chars, hard cap ~100), long output split
      across lines.
- [ ] Every gap the README needs is a `<!-- TODO: … -->` marker, not a guessed
      command, version, or number; every claim it cannot support is gone.
- [ ] Prose is wrapped and tables padded to the repo's `[*.md] max_line_length`
      (80 when unset), counted in characters, not bytes: an em dash is one
      column, so byte-based length checks over-report.

Dynamic:

- [ ] Run the install and quickstart commands exactly as written; never ship
      one you did not run. Expect at least one that cannot pass yet — an
      unpublished module, a private host, a package not on a registry. On a
      fresh or private project that is the ordinary case, not a failed run:
      the command is right and the project has not caught up to it. Which of
      the two kinds it is decides what happens:
      - *This environment cannot run it* (toolchain missing, permission denied,
        no network): the reader is unaffected. Say so in the reply and leave
        the README alone — never warn the reader about your sandbox.
      - *It runs and fails for a project reason* (module unpublished, package
        not on the registry): it will fail for the reader too, so the reader
        must be told. A `<!-- TODO: … -->` is invisible to them; use a
        `> [!NOTE]` naming what has to happen first, and a TODO only for the
        fact you are missing.

## Self-application

`readme-smith` obeys the repo authoring standard. When you change this skill,
re-check it against `CONTRIBUTING.md` and run `./dev/lint-skills.sh`.

## Self-learning

Obey this skill's lessons when it has any: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/craft/readme-smith.md` when this
directory is read-only. Most runs have none; absence is the normal case and
needs no comment. On a correction or self-caught mistake, append a one-line
rule to whichever path is writable, creating it, and report where.
