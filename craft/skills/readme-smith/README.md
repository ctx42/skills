# readme-smith

Creates and improves a project's `README.md`, grounded in the real repo.

## Usage

```
/readme-smith                         (default) infer create vs improve from the request; asks if ambiguous
/readme-smith create [<readme-path>]  scan the repo and draft a new README, grounded in real code
/readme-smith improve <readme-path>   audit an existing README, report findings, fix on confirmation
```

## Modes

- Create: no usable README exists, or you want a new/rewritten one. It asks
  only for the gaps code cannot reveal.
- Improve: an existing README to audit; findings are grouped by severity and
  fixed only on your confirmation.

Both modes draft and audit against the blueprint in
[references/template.md](references/template.md): GFM, GitHub admonitions,
restrained emoji, a logo only if the repo has one, and no fabricated facts. The
skill never authors Contributing/Changelog/Code-of-Conduct/Security sections
(dedicated files own those), keeps badges and any `## License` section to the
root README, and runs the install/quickstart commands it ships to prove they
work. In a Go project that offers the gomake `:project:doc-eg` target, README
examples are injected from testable `Example…` functions
([references/gomake.md](references/gomake.md)).

## Evaluations

### 1. Create a README from a repo scan

**Request:** `/readme-smith write a README for this project`

**Expected behavior:**
- Scans manifests, entrypoint, examples, and `.github/`/`assets/` for a logo or
  demo before writing anything.
- Batches gap questions (positioning, audience, lead features) in one round;
  does not ask what the repo already answers.
- Drafts to the blueprint order (header/logo → overview → features → install →
  usage → config), using the repo's real name, commands, and paths.
- Executes the install/quickstart commands and fixes them until they pass, or
  flags the blocking prerequisite.

### 2. Never fabricate a missing fact

**Request:** `/readme-smith create a README` (repo has no benchmarks and no
published package)

**Expected behavior:**
- Does not invent install commands, version numbers, or benchmark figures.
- Asks for the unknown fact; if still unknown, leaves an explicit
  `<!-- TODO: … -->` marker instead of guessing.
- Omits badges it cannot back with a verifiable fact.

### 3. Improve an existing README

**Request:** `/readme-smith improve pkg/foo/README.md` (a member README in a
multi-package repo)

**Expected behavior:**
- Reports its `## License` section as a finding (root README only; the
  `LICENSE.md` file owns the text).
- Flags code fences with no language and nav links to missing anchors, each
  citing the rule from `references/template.md`.
- Groups findings Blocker / Should-fix / Nit and offers to apply them — no edits
  before confirmation.

### 4. Inject Go examples via gomake instead of hand-writing them

**Request:** `/readme-smith write a README` (Go project whose `gomake --help`
lists a `:project:doc-eg` target)

**Expected behavior:**
- Detects the target from `gomake --help` before choosing how to author examples.
- Writes runnable `Example…` functions in `_test.go` and runs `go test ./...`
  until they pass, rather than pasting hand-written snippets.
- Runs `gomake :project:doc-eg` to inject them and does not hand-edit the
  injected regions.
- Falls back to hand-written examples only when the target is absent.

### 5. Enforce restrained style and terse output

**Request:** `/readme-smith improve a README with an emoji on every heading and a
badge wall`

**Expected behavior:**
- Flags per-heading emoji and unverifiable badges against the style rules.
- After fixing, states what changed and the file path — does not paste the whole
  README back into chat.
- Its own report opens with the payload: no preamble, no narration, no closing
  summary restating findings already shown.

### 6. One navigation aid; module vs package paths kept distinct

**Request:** `/readme-smith create a README` (Go module `github.com/acme/foo`
whose only package is `github.com/acme/foo/pkg/foo`, long enough to warrant a TOC)

**Expected behavior:**
- Emits exactly one navigation aid — a nav line or a `<!-- TOC -->` block, never
  both.
- Reads the base path from `go.mod`, not one guessed from the org or a sibling
  repo, and points `go get`/badges/pkg.go.dev at the module
  (`github.com/acme/foo`) but the Go `import` at the package
  (`github.com/acme/foo/pkg/foo`).
- Does not assert the repo is public or private, and adds no `GOPRIVATE`/auth
  note, from the host URL alone.

### 7. Code examples that don't scroll sideways on GitHub

**Request:** `/readme-smith write a README` (Go project with a `:project:doc-eg`
target whose example prints a long wire dump)

**Expected behavior:**
- Keeps every code-fence line within the rendered width (≤ ~100 chars) so GitHub
  wraps nothing horizontally.
- For a gomake example that would emit one wide line (e.g.
  `fmt.Printf("%q\n", body)`), rewrites the `Example…` function to split the
  output across lines and re-injects, rather than shipping the wide line.

## Relationship to other skills

- `grill-me` — use it first when the project's positioning is fuzzy;
  `readme-smith` create mode asks gaps but doesn't run a full planning interview.
- `skill-smith` — authors this skill and audits it against the repo standard.
