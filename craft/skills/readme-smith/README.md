# readme-smith

Forge and repair a project's `README.md`. One skill, two modes, chosen from how
you ask:

- **Create** — no usable README exists, or you want a new/rewritten one. It scans
  the repo, asks only for the gaps code can't reveal, and drafts to a distilled
  house structure.
- **Improve** — name an existing README and it audits against the same rules,
  reports findings by severity, then fixes them on your confirmation.

**The rules it lives by:** structure and style come from
[references/template.md](references/template.md) — GFM, GitHub admonitions,
restrained emoji, a logo only if the repo has one, and no fabricated facts. It
never authors License/Contributing/Changelog sections (dedicated files own
those), and it runs the install/quickstart commands it ships to prove they work.

## Usage

```
/readme-smith create a README for this project      # create mode
/readme-smith improve the README                    # audit + fix existing
/readme-smith review README.md                       # audit by path
```

You don't need a mode keyword — it infers create vs improve from the request. No
usable README → CREATE. Point at an existing one → IMPROVE.

- **Create** grounds everything in a repo scan, asks positioning/audience gaps in
  one batched round, drafts, verifies, and writes `README.md`.
- **Improve** reports before it edits: findings grouped Blocker / Should-fix /
  Nit, each citing the rule it breaks.

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

**Request:** `/readme-smith improve README.md`

**Expected behavior:**
- Reports a `## License` section duplicating `LICENSE.md` as a finding (excluded
  section — dedicated file owns it).
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
  repo, and points `go get`/badges/pkg.go.dev at the **module**
  (`github.com/acme/foo`) but the Go `import` at the **package**
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
