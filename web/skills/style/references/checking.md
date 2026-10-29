# style pass

Read when `style` is invoked as a command (`/web:style ...`). The pass checks
code against the style rules only — structure, naming, TSDoc, test shape, the
Biome config; bugs, edge cases, and logic errors are `web:review`'s job.

Read the invocation from `$ARGUMENTS`, by the token rules in `SKILL.md`.

## Contents

- Frontend root
- Target
- Budget & scope
- Principles
- Workflow
- Offense list
- Fixing
- Scale
- Delegated by web:review

## Frontend root

The directory holding the `package.json` that depends on `vue` — the working
directory, or the one subdirectory below it that has one (`web/`). Paths in
the target resolve against the working directory first, then this root. No
such directory, or several: say so and ask; never guess.

## Target

The target selects what to check:
- empty — `git diff HEAD` restricted to `*.vue`, `*.ts`, and `biome.json`
  under the root; if that is empty, the diff vs the base branch (staged +
  unstaged).
- not a path at all — `add`, `change`, `remove`, or prose about the rules
  themselves is a rulebook edit, not a target: redirect to `web:review` rather
  than resolving it as a directory that does not exist.
- a directory (`src/pages`) — its `.vue` and `.ts` files, recursively.
- a file — that file.
- `component=<Name>` — the one `<Name>.vue` under the root (and its
  `<Name>.test.ts`); `func=<name>` — the one exported function, composable, or
  store of that name, with its `describe("<name>")` tests. None or several
  matches: list them and ask.
- `FILE:LINE` (`src/pages/DevicesPage.vue:42`) — the unit enclosing that
  line, as `func=` or `component=` would name it: the exported function,
  composable, or store around it, or, in a `.vue` file, the component. A line
  in no unit: say so and ask.
- `all` — every `.vue` and `.ts` file under the root (dependency, build, and
  coverage directories excluded), plus `biome.json`.

The Biome config check (the Tooling rule) runs for every target that includes
`biome.json` — `all`, the root directory, and a diff touching it — and never
for a narrower one.

State the resolved root, target, and exact file set before checking.

## Budget & scope

Read these controls and flags:
- `dirs=a,b` — restrict to these directories under `src/` (`pages`,
  `stores`, `components`; `src` itself means its top-level files).
- `max=N` — cap on offenses reported (default 25).
- `depth=light|standard|full` — default `standard`. `light` reports only
  Blocker and Should-fix offenses, counts the Nits it leaves out in the
  unreported total, and skips `comments-fit-biomes`, saying both in one line;
  `full` checks every rule exhaustively.
- `plan_first` — propose the budget and the directory list, then stop for
  the user's answer, checking nothing until it comes.
- `fix` — apply every listed offense's fix without asking: it skips the pick
  step, never the plan-first stop below.

Default to plan-first for a broad target with no budget: propose defaults (the
caps above, the directory list) and ask before applying anything. Either
`dirs=` or `max=` is a budget; `depth=` alone is not. Broad means more than
~40 files or ~3000 lines of `.vue`/`.ts` in scope. Plan-first is
propose-then-stop: no check until the user answers.

## Principles

Reason from these while checking; they generalize the `SKILL.md` rules to
cases no single line spells out.

1. One way to do each thing: where the project has a shared helper (reads,
   query guards, error text, test fakes), a hand-rolled copy is the offense.
2. Earn every token: flag TSDoc that paraphrases the name or the types, a
   helper wrapping one expression, a `want` that saves nothing.
3. State lives where its lifetime does: a page's own read in the page, a
   shared one in a store, a non-reactive handle in a `let`, list state in the
   URL.
4. The boundary checks, the inside trusts: untyped data becomes typed once,
   at the client or the storage read, and nowhere else.
5. An assertion must be able to fail: pin the text or value unique to the
   wanted branch, never one shared across sibling paths.
6. A tool's rule is the tool's: never re-report what the reference Biome
   config enforces; report the config that fails to enforce it.

## Workflow

1. Resolve the root, the target, the budget, and Biome's `lineWidth` (from
   the project's `biome.json`, else 80). List the files in scope.
2. Biome config check, when in scope: compare the project's `biome.json` with
   [biome.json](biome.json) — every rule the reference sets, with its level
   and options, the `html.formatter`, and the overrides. Each rule missing or
   weaker is one site of the Tooling offense; quote its absence as
   `<group>/<rule>: absent` or the weaker setting.
3. Check each file against the rules in `SKILL.md` — Production for `.vue`
   and `.ts`, Test for `*.test.ts` and `e2e/*.spec.ts` — reasoning from the
   Principles. Read a whole SFC: script, template, and style each carry rules.
4. Before reporting an offense whose truth reaches beyond the file (a
   duplicated helper, a rename's call sites, an unused export), confirm it with
   the `LSP` tool or grep across the root rather than asserting from the
   visible code. Skip at `depth=light`.
5. Judge by reading; never run Biome, `vue-tsc`, or the tests to detect —
   they enforce the mechanical half, and the gate in Fixing runs them. The
   exception is `comments-fit-biomes`: measure every comment line by script,
   read-only, in characters (not bytes).
6. List the offenses (below), then fix per Fixing.

## Offense list

Open with one line naming the resolved root, target, files in scope, and line
width (`width N (from <path>|default)`), then the offenses. That line is the
report's first fact, not preamble: without it a reader cannot tell an empty
result from an unresolved target.

Group by severity Blocker / Should-fix / Nit. Severity is a property of the
rule, not of the instance or the reader's taste: the same rule broken in two
directories is the same severity in both. Decide it from the fix the rule
prescribes in general, by the first of these that matches:

1. Blocker — the code is wrong or will mislead: an unchecked `as T` on a
   response, a superseded answer written to state, a listener or timer never
   torn down, a `fetch` outside the client, a swallowed error with no comment,
   a count or empty message shown before its read finished, an assertion that
   passes on the wrong branch, a project Biome config missing a reference rule.
2. Nit — Biome's formatter would produce the fix, or the fix only inserts,
   removes, or rewraps whitespace or inserts, rewords, or deletes a comment,
   leaving every identifier, statement, and declaration where it is.
3. Should-fix — everything else: the fix renames, moves, regroups, or
   restructures.

First match wins; 3 is the residue. A rule whose prescribed fix moves any code
fails 2 and lands in 3, even at a site needing only a blank line.

Each offense:
- `file:line` — the offense in one line; an offense about a whole file cites
  `file:1`, and a missing Biome setting cites `biome.json` alone.
- the rule id (below).
- the trigger: the source text that makes it an offense, quoted — not the fix
  and not the rule. An offense whose trigger cannot be quoted was not located.
- the minimal fix, opening with exactly one of `insert`, `delete`, `rename`,
  `move`, `replace`, `reword` — adding anything is `insert`; never another
  verb or prose first.

Rule ids are derived, never coined, in these steps:

1. Take the rule's whole `SKILL.md` bullet; one bullet is one id, never split
   on `;`.
2. Drop backticks; split a backtick span on whitespace, cut each token at its
   opening parenthesis, then: a token with a file extension contributes
   nothing; a dotted identifier contributes the part before the first dot;
   a token that is letters once its outer punctuation is stripped contributes
   those letters; anything else contributes nothing.
3. Split into words: a hyphen inside a word keeps it one word, an apostrophe
   is deleted, any other run of non-alphanumerics separates words.
4. Drop *a an the is are be to of in on at by with for from and or its it
   this that*; nothing else (negations stay).
5. Collapse a word repeating the one before it, take the first three words,
   lowercase, join with hyphens. Two bullets on one id: extend both to the
   first word that tells them apart.

*Comments fit Biome's `lineWidth`…* → `comments-fit-biomes`. *Bind
`defineProps` to `props` only…* → `bind-defineprops-props`. *Send every
request through the one client module…* → `send-every-request`. *The
project's `biome.json` turns on every rule…* → `projects-turns-every`.

One offense is one rule broken in one file, however many times; list every
site on it. Stop at `max`, highest severity first; say how many offenses went
unreported. End with a one-line verdict (clean / fix-first) and per-severity
counts.

## Fixing

Style fixes are non-behavioral, so no failing-test reproduction is needed —
the gate is the proof.

- Default: present the offenses as a numbered list — one number per offense,
  its sites beneath — and ask which to apply; apply only the picked ones,
  every site of a picked number. `fix` applies all. A plan-first run reaches
  here only after the user answered the plan; the pick step still runs.
- Run `bun run check` in the root (Biome, `vue-tsc`, Vitest) for a green
  baseline before editing; if already red, or it cannot run, stop and report
  why — a gate that never ran verifies nothing. Run it again after; the job is
  not done until it passes.
- A Biome config fix adds the reference's settings to the project's
  `biome.json`; the code the new rules then flag is part of that fix — `bunx
  biome check --write` for what Biome fixes itself, by hand for the rest —
  and the gate must pass with it.
- Measure every comment line a fix writes against the width before applying
  it.
- For a rename or a moved export, enumerate the references with `LSP` or grep
  before editing so definition and users change together.
- Never print diffs: report each applied fix as one line (`file:symbol — what
  changed`) plus the gate result. Never `git commit`.
- Big job (many changed lines or restructuring edits): write an ordered plan to
  a scratch file kept out of git (`tmp/style-fix-plan.md`), one chunk per
  directory with status boxes; the pick answer is the go-ahead; gate per chunk,
  and after each changed chunk report it and ask before the next.

## Scale

- Up to ~40 files or ~3000 lines in scope: check in this context.
- Larger: fan out one subagent per directory (`components`, `pages`,
  `stores`, top-level `src`, `e2e`), each given the paths of `SKILL.md` and
  this file — not their text — the `depth`, and the parent's list of rule ids
  and severities, derived once for every rule in scope. Workers neither coin
  an id nor grade a tier; a rule missing from the list comes back with the line
  quoted, no id, no severity. Workers get no share of `max`: the cap applies
  once, at the merge.
- The parent runs the Biome config check itself and merges only once every
  worker has returned. The merge folds by rule id (one rule broken in four
  directories is one finding listing four), then, for every rule flagged in
  some directories but not all, greps the others for the quoted trigger and
  reports the reconciled count. Then it sorts by severity and id and cuts at
  `max`. The verdict line carries the raw total, summed from the worker
  reports, and the unreported count, zero included.

## Delegated by web:review

Delegation is recognized from the invocation, never guessed: `review` says it
is invoking for offenses only and passes the target and budget. A delegated
run never stops for plan-first — the budget is `review`'s. Run Workflow
steps 1–5 and output the offense list, then stop — no Fixing. `review` merges
these offenses with its correctness findings and owns fix application.
