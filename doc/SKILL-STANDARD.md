# SKILL-STANDARD

**The craft of authoring excellent agent skills.**

This is a textbook, not a checklist you skim once. Read it start to finish and you
will understand not just *what* the rules are but *why* they hold — which is what
lets you make the right call in the 5–10% of situations no rule anticipates. It
is written to be the durable basis for skills that run reliably, cost little, and
degrade gracefully as models and tasks change.

The scope is deliberately narrow: **the craft of writing the skill artifact
itself.** Not the surrounding product decisions, not the marketplace mechanics —
the words, the structure, and the discipline that separate a skill an agent
actually uses well from one that sits inert or, worse, quietly misleads it.

---

## Contents

1. [What a skill is](#1-what-a-skill-is)
2. [The one mental model: on-demand expertise](#2-the-one-mental-model-on-demand-expertise)
3. [When a skill is the right tool](#3-when-a-skill-is-the-right-tool)
4. [Anatomy of a skill](#4-anatomy-of-a-skill)
5. [The description: the highest-leverage field](#5-the-description-the-highest-leverage-field)
6. [Naming](#6-naming)
7. [The body: writing for a capable reader](#7-the-body-writing-for-a-capable-reader)
8. [Degrees of freedom](#8-degrees-of-freedom)
9. [Progressive disclosure in practice](#9-progressive-disclosure-in-practice)
10. [Workflows, checklists, and feedback loops](#10-workflows-checklists-and-feedback-loops)
11. [Output discipline](#11-output-discipline)
12. [Scripts and bundled files](#12-scripts-and-bundled-files)
13. [Content hygiene and maintainability](#13-content-hygiene-and-maintainability)
14. [Portability](#14-portability)
15. [Evaluation-driven authoring](#15-evaluation-driven-authoring)
16. [Anti-patterns catalog](#16-anti-patterns-catalog)
17. [The scorecard](#17-the-scorecard)
18. [Worked example: bad → good](#18-worked-example-bad--good)
19. [The authoring checklist](#19-the-authoring-checklist)
20. [Sources and further reading](#20-sources-and-further-reading)

---

## 1. What a skill is

A skill is a folder with a Markdown file in it. That is the whole idea, and its
plainness is the point. The file — `SKILL.md` — is a piece of instruction the
agent loads *only when a task needs it*, telling it how to do something it would
otherwise do worse or not at all. Optionally the folder carries more: reference
documents, runnable scripts, templates, data.

Think of a skill as a **specialist you hire the moment a job appears and dismiss
the moment it's done.** The agent already knows a great deal; the skill supplies
the narrow, situational expertise it lacks — your team's review conventions, the
exact incantation your migration needs, the shape your commit messages must take.
When no such job is on the table, the specialist isn't in the room taking up space.

Everything that makes a skill *good* follows from two facts about that specialist:

- It must be **findable** at the exact moment it's relevant, from among possibly
  a hundred others, on the strength of a one-line self-description.
- Once summoned, it competes for the agent's finite attention with everything
  else in the conversation, so it must earn every token it costs.

Hold those two facts in mind. The rest of this document is their consequences.

---

## 2. The one mental model: on-demand expertise

If you internalize one thing, make it **progressive disclosure**. A skill is not
loaded all at once. It reveals itself in three tiers, each paid for only when
reached:

| Tier          | What loads                                    | When                                       | Rough cost                  |
|---------------|-----------------------------------------------|--------------------------------------------|-----------------------------|
| **Metadata**  | `name` + `description` only                   | always, for *every* skill                  | ~a few dozen tokens each    |
| **Body**      | the full `SKILL.md` instructions              | only when the skill triggers               | up to a few thousand tokens |
| **Resources** | files in `references/`, `scripts/`, `assets/` | only when the body sends the agent to them | zero until touched          |

This is the same shape as a well-made manual: a table of contents you always see,
chapters you open when relevant, an appendix you consult only for the one detail
you need. It is why a skill library can hold vast knowledge cheaply — the metadata
is the only thing that is *always* on, so a hundred dormant skills cost a hundred
one-liners, not a hundred manuals.

Every architectural rule later in this document — keep the body lean, push detail
to references, name files for their content, write a razor-sharp description — is
an instruction for exploiting these three tiers. When you're unsure where a piece
of content belongs, ask: *at which tier does the agent actually need this?* Put it
there and nowhere earlier.

### Why the always-loaded surface must stay small

The metadata tier is loaded on every request whether your skill fires or not, and
the body, once loaded, stays resident for the rest of the session. Both are
recurring costs, and they are not free in a subtler way than money: they consume
the model's **attention budget.**

A transformer relates every token to every other token. Add tokens and you stretch
that web of relationships thinner. This is not a theoretical worry — it is measured.
Across frontier models, retrieval and reasoning reliability *decline as input
length grows*, well before any hard context limit is reached. The comforting
assumption that the ten-thousandth token is handled as sharply as the hundredth
simply does not hold. Worse, irrelevant-but-plausible content is not neutral
padding: a single distractor measurably lowers accuracy, and several compound.
Information sitting in the middle of a long context is recalled far less reliably
than material at the start or end.

The lesson is blunt and it governs the entire craft: **a bloated skill is not a
generous skill; it is a distractor field that degrades the very task it means to
help.** Aim, always, for the smallest set of high-signal tokens that reliably
produces the outcome you want. "Smallest" is the operative word — but read
[§8](#8-degrees-of-freedom) before you mistake it for "shortest."

---

## 3. When a skill is the right tool

Before you write a skill, be sure a skill is what you want. The artifact is cheap,
but a library full of skills that should have been something else is a liability.

- **Skill vs. a one-off prompt.** If you find yourself giving the agent the same
  context, corrections, or conventions *repeatedly*, that recurring context is a
  skill waiting to be extracted. A single instruction you'll never reuse is just a
  prompt; don't ceremonially wrap it. The strongest skills are *codified repetition*
  — the practice you coached the agent through three times, captured so you never
  coach it a fourth.
- **Skill vs. a tool or MCP server.** Tools and MCP connections often front-load
  large schemas into context whether or not you use them. A skill costs a one-line
  description until it fires. So when a capability can be expressed as *"here is how
  to drive a command-line tool"* rather than *"here is a permanent API surface,"*
  the skill is usually the leaner choice — the agent already knows how to read a
  tool's `--help`. Reserve tools/MCP for genuine live integrations (auth, state,
  real-time data) that instruction alone cannot provide.
- **Skill vs. a subagent.** These are not rivals; they compose. A skill is the
  *methodology* — the how; a subagent is an *executor* with its own context window.
  A skill can instruct the agent to dispatch subagents, and a subagent can operate
  under a skill. Choose a subagent when you need isolation or parallelism; choose a
  skill when you need shared know-how. Often you want both.

A skill earns its place when the knowledge is **reusable, situational, and not
already in the model.** If any of those three is missing, reach for something else.

---

## 4. Anatomy of a skill

A skill is a directory whose name *is* the skill's name:

```
processing-invoices/
├── SKILL.md            # required — the only mandatory file
├── references/         # docs the agent reads on demand
│   ├── tax-rules.md
│   └── formats.md
├── scripts/            # code the agent runs (not read into context)
│   └── validate.py
└── assets/             # templates, schemas, sample data
    └── invoice-template.md
```

`SKILL.md` itself is two parts: **YAML frontmatter** (structured metadata) and a
**Markdown body** (the instructions).

```markdown
---
name: processing-invoices
description: >
  Extracts totals, tax, and line items from PDF and image invoices and validates
  them against company tax rules. Use when the user uploads an invoice, mentions
  invoices, receipts, or accounts-payable, or asks to check invoice totals.
---

# Processing invoices

[the body: how to do the job]
```

The frontmatter conventions worth committing to memory, because they hold across
every runtime that reads this format:

| Field         | Required | Constraints                                                                                                         |
|---------------|----------|---------------------------------------------------------------------------------------------------------------------|
| `name`        | yes      | lowercase letters, digits, hyphens; ≤ 64 chars; no leading/trailing hyphen; no `--`; **matches the directory name** |
| `description` | yes      | non-empty; ≤ 1024 chars; states *what* and *when*; no angle brackets                                                |
| `license`     | no       | a license name or a pointer to a bundled license file                                                               |
| `metadata`    | no       | a flat map of string→string for things like `author`, `version`                                                     |

Two rules on that table are load-bearing. First, **keep the field set minimal.**
The two required fields plus, at most, `license` and `metadata` are the portable
core. Everything else you may have seen — tool restrictions, invocation toggles,
argument declarations, model pins — is a runtime-specific extension that other
agents silently ignore ([§14](#14-portability)). Second, **avoid a bare colon or
a leading `>`/`<` inside a plain scalar** — they break YAML parsing. When a
description spans lines or contains a colon, use a folded block scalar
(`description: >`), as above. It is valid, portable, and the safe default.

The body has no required format, but the good ones share a spine: a short
orientation, then the steps, examples, and edge cases, with heavy detail pushed
out to `references/`. Treat `SKILL.md` as the table of contents that points to the
chapters, not as the encyclopedia itself.

---

## 5. The description: the highest-leverage field

Nothing else you write matters if this fails. The description is the **only** part
of your skill (with the name) that is always in the agent's context, and it is the
sole basis on which the agent decides — from among every skill available — whether
to open yours at all. A flawless body behind a vague description is a specialist no
one thinks to call. This one field deserves more of your revision time than any
paragraph of the body.

Six rules produce a great description.

**1. Write in the third person.** The description is injected into the system
prompt, and a shift in point of view muddies discovery.

> ✓ `Generates release notes from merged pull requests.`
> ✗ `I can help you write release notes.` / `You can use this to write release notes.`

**2. State both what it does *and* when to use it — with concrete triggers.** Name
the file types, the user phrasings, the situations. The agent is pattern-matching
your description against a real task; give it surfaces to match on.

> ✓ `Extract text and tables from PDF files, fill forms, and merge documents. Use
> when the user works with PDFs or mentions forms, extraction, or merging.`
> ✗ `Helps with documents.`

**3. Lead with the primary use case.** Downstream, description text can be
truncated to fit a listing budget. Put the sentence that most distinguishes your
skill first; put the marginal triggers last.

**4. Be specific, never generic.** "Processes data," "does stuff with files,"
"helps with tasks" — these match everything and therefore trigger on nothing
reliably. Specificity is what makes the match land.

**5. Lean slightly *toward* triggering.** Agents have a measured tendency to
*under*-trigger skills — to press on without the help that was right there. A short
nudge earns its keep: *"…even if the user does not explicitly ask for a chart."*
Push a little; the cost of a skill that fires when marginally relevant is far
lower than the cost of one that never fires.

**6. Do not smuggle the workflow into the description.** This is the subtle one,
and the most common way a good skill quietly fails. If the description *summarizes
how the skill works*, the agent may act on that summary and never open the body —
skipping the very steps the skill exists to enforce. A description that says
`…dispatches a subagent per task with code review between tasks` invites the agent
to do a single review and move on. Say *when to use it*, not *what it does
step-by-step*. Include only enough "what" to disambiguate from neighboring skills;
let the body own the procedure.

> ✓ `Use when executing an implementation plan with independent tasks.`
> ✗ `Use when executing plans — dispatches a subagent per task with code review
> between tasks.`

Rules 2 and 6 are in slight tension — enough "what" to be found, not so much that
the agent shortcuts. Resolve it this way: **the description's job is discovery, not
instruction.** Every clause should help the agent decide *whether this is the
right skill*, never teach it *how to do the work*. If a clause reads like a step,
it belongs in the body.

---

## 6. Naming

The name is a small field with outsized ergonomics. It must equal the directory
name, stay within lowercase letters, digits, and hyphens, and avoid reserved
vendor words. Beyond the hard rules:

- **Prefer a gerund or a short verb phrase:** `processing-invoices`,
  `reviewing-go-code`, `writing-commit-messages`. The gerund reads as a capability
  ("this skill does X"), which is exactly how the agent should think of it.
- **Never use vague fillers:** `helper`, `utils`, `tools`, `stuff`, `misc`. They
  tell neither human nor agent anything, and they collide conceptually with every
  other skill.
- **Name for the job, not the mechanism.** `migrating-database`, not
  `run-migrate-script`. The job is stable; the mechanism may change.

A good name and a good description reinforce each other: the name is the label on
the folder, the description is the sentence that makes the agent open it.

---

## 7. The body: writing for a capable reader

The reader of your body is not a novice. It is a highly capable model that already
knows what a PDF is, how HTTP works, what JSON looks like, and how to write a loop.
Your one and only job is to supply **what it does not and cannot know**: your
conventions, your constraints, your hard-won gotchas, the specific shape you want.

This single reframing — *assume the reader is smart; add only the gap* — prevents
most bad skill bodies. Before every sentence, ask: **does the model already know
this?** If yes, cut it. A paragraph explaining that "PDF stands for Portable
Document Format and is a common way to store documents" is pure distractor tokens:
it costs budget, dilutes attention, and teaches nothing. Multiply that waste across
a library and you have burned half the context window before the user has asked
anything.

Compare:

> **Bloated (~150 tokens)**
> "PDF (Portable Document Format) files are a common file format that contains
> text, images, and other content. To work with them in Python, you'll need a
> library. There are several options, but a good one is pdfplumber, which you can
> install and then use to open a file and extract its text page by page…"

> **Lean (~50 tokens)**
> "Extract text with `pdfplumber`:
> ```python
> import pdfplumber
> with pdfplumber.open(path) as pdf:
>     text = "\n".join(page.extract_text() for page in pdf.pages)
> ```"

The lean version assumes competence and spends its tokens only on the choice the
model couldn't make on its own (*which* library) and the exact call. That is the
target density for every line you write.

Four more habits make a body sharp:

**Be imperative and concrete.** State what to do. "Validate the total against the
line items before saving," not "It might be a good idea to consider validating."
Directness removes the model's need to infer your intent.

**Use one term per concept, everywhere.** If it's a "field," it is always a
"field" — never sometimes a "box," a "control," or an "element." Synonyms read to
the model as *different things*, forcing it to reconcile references that were meant
to be identical. Internal inconsistency — telling the model to "score" a response
while your example labels the output "value" — is a reliability leak. Pick the
word once and hold it.

**State the rule, then the reason.** This is the highest-leverage habit in the
whole body, because reasoning generalizes and bare commands do not. An all-caps
`ALWAYS`/`NEVER`/`MUST` with no rationale gives the model a rigid edge it will
follow to the letter and miss around. Give it the *why* and it can extend your
intent to the cases you never spelled out:

> ✗ `NEVER use field injection.`
> ✓ `Use constructor injection. Field injection can't be mocked without a full
> framework context, so it breaks unit testing — which is why we avoid it.`

The reasoning becomes the rubric for the unforeseen case. There is one deliberate
exception: for genuinely fragile, one-right-way steps, a bare imperative is
correct and cheaper — save the emphatic, unexplained command for the cliff edges
([§8](#8-degrees-of-freedom)). And when a real rule is being *missed* in practice,
escalating the language ("MUST filter test accounts," not "always filter") is a
legitimate reliability dial, not a contradiction of this advice. Emphasis is a
tool; reflexive all-caps is a smell.

**Keep the body lean and roughly bounded.** As a rule of thumb, keep `SKILL.md`
under about 500 lines (a few thousand tokens); when it strains that, the body is
carrying detail that belongs in a reference. This is not an arbitrary cap — it is
the attention budget of [§2](#2-the-one-mental-model-on-demand-expertise) made
concrete. But judge by *tokens-to-outcome*, not line count: a padded 300-line body
can cost more and perform worse than a dense 480-line one.

---

## 8. Degrees of freedom

Here is where authors most often go wrong, and almost always in the same direction:
they over-constrain out of fear. The core decision in every instruction you write
is **how much latitude to give the model**, and the right answer depends entirely
on how fragile the task is.

Picture the model as something moving toward a goal across terrain:

- **An open field, no hazards — high freedom.** Many routes succeed and the best
  one depends on context the model can see and you can't. Give direction and
  trust it. A code review is like this: *"Assess structure, find likely bugs,
  check error handling, suggest improvements"* — prose heuristics, no rigid script.
- **A path with some soft edges — medium freedom.** A preferred pattern exists but
  variation is fine. Give a parameterized template or pseudocode: a report
  generator with `format=` and `include_charts=` knobs.
- **A narrow bridge over a cliff — low freedom.** One wrong step is catastrophic
  or the operation must be perfectly consistent. Give the exact command and
  forbid improvisation: *"Run exactly `python scripts/migrate.py --verify
  --backup`. Do not add or change flags."*

The two failure modes sit at the extremes. **Over-specify** and you hardcode
brittle logic that breaks the moment reality deviates from your script, and that
you must maintain forever. **Under-specify** and you leave the model with vague
gestures and no concrete signal, so it guesses. The target is the middle: specific
enough to steer behavior, loose enough to leave the model strong heuristics for
what you didn't foresee.

The most important nuance, and the one that reconciles this section with the
relentless "cut tokens" drumbeat of the rest: **minimal does not mean short.** The
goal is the *minimal set of information that fully specifies the behavior you
want* — which sometimes means more words, not fewer. Cutting a necessary
constraint to save tokens is not economy; it's under-specification wearing
economy's clothes. Spend tokens freely on what the model genuinely needs and can't
infer; spend none on what it already knows. That distinction — not raw length — is
the whole game.

---

## 9. Progressive disclosure in practice

[§2](#2-the-one-mental-model-on-demand-expertise) gave you the model; here is how
to build with it. The move is always the same: **keep `SKILL.md` as the lean index
and push weight outward into files the agent opens only when it needs them.**

**References go one level deep — never chain them.** Link every reference directly
from `SKILL.md`. Do not make `SKILL.md` point to `advanced.md`, which points to
`details.md`, where the real answer lives. Agents frequently *preview* a linked
file rather than reading it whole — glancing at the first hundred lines — so
information buried two hops away arrives partial or not at all. One hop, always.

**Give any reference over ~100 lines a table of contents.** Because the agent may
only preview a long file, a ToC at the top guarantees that even a partial read
reveals the file's full scope, so the agent knows what's there and can decide to
read the relevant part in full.

**Organize references by domain so irrelevant context never loads.** If a data
skill splits its schema into `references/finance.md`, `sales.md`, and `product.md`,
a question about revenue pulls in only `finance.md` — the other two cost nothing.
A single monolithic `reference.md` forces the whole thing into context for any
question. Split along the lines the tasks actually divide on.

**Name files for their content.** `tax-rules.md`, `form-validation.md` — never
`doc2.md` or `notes.md`. The name is how the agent (and you) decide whether to
open it. Use forward slashes in every path, always, regardless of the platform you
authored on.

**Distinguish "run this" from "read this."** A script in `scripts/` can be
*executed* — in which case only its output enters context, and the file itself can
be arbitrarily large for free — or *read* as a reference algorithm, in which case
its whole text is loaded. Tell the agent which you mean, in words:

> "Run `scripts/validate.py` to check the plan." *(execute — cheap)*
> "See `scripts/scoring.py` for the exact weighting algorithm." *(read — costs the file)*

Because resources load only on demand, the *total* size of a skill is effectively
unbounded — you can bundle complete API references, large datasets, exhaustive
examples — as long as the always-loaded surface stays tiny. That asymmetry is the
gift of progressive disclosure. Use it: move everything you can out of the body,
and let the agent reach for it precisely when the task calls.

---

## 10. Workflows, checklists, and feedback loops

For anything with more than a couple of steps, structure beats prose. Three
patterns cover almost every case.

**Numbered steps, and a copyable checklist for complex jobs.** Break a multi-step
task into an explicit ordered sequence. For genuinely involved work, give the agent
a checklist it copies into its working output and ticks off as it goes — the act of
tracking keeps it from skipping or reordering steps under load:

```markdown
Copy this checklist and check off each item as you complete it:
- [ ] Extract all line items from the invoice
- [ ] Match each line item to a purchase-order entry
- [ ] Validate the computed total against the stated total
- [ ] Flag any mismatch over the tolerance; do not auto-correct
- [ ] Write the reconciled record
```

**Validate → fix → repeat.** For anything where quality matters, build a feedback
loop into the instructions. The "validator" can be a script or simply a reference
doc the agent re-checks its work against, but the shape is constant: produce, check,
correct, and *only proceed when the check passes.* A loop like this lifts output
quality more than any amount of extra prose, because it turns a one-shot into a
self-correcting process.

**Plan → validate the plan → execute.** For risky, batch, or irreversible work,
don't let the agent act directly. Have it emit a *verifiable intermediate
artifact* — a `changes.json`, a list of edits, a migration plan — then validate
that artifact (by script or by review) *before* anything is applied. This catches
errors while they're still cheap and reversible. Make the validators loud and
specific when they fail: *"Field 'signature_date' not found. Available fields:
customer_name, order_total, vendor."* A verbose failure message is itself an
instruction — it tells the agent exactly how to recover.

The through-line: reliability comes from *loops and checkpoints*, not from a
longer list of hopeful imperatives.

---

## 11. Output discipline

A skill that produces chatty output is not merely annoying — it is *actively
harmful* in an agent loop, because this turn's output becomes next turn's input.
Verbose responses poison the agent's own future context (compounding the attention
decay of [§2](#2-the-one-mental-model-on-demand-expertise)) and cost tokens twice:
once to generate, once to re-read. Terseness is context hygiene, and every skill
that produces a running report should enforce it.

Bake these into any skill that talks back:

- **Cut the framing.** No preamble ("I'll now analyze…"), no narration ("Let me
  read the file…"), no closing filler ("Hope this helps!"). Open with the payload.
- **State each fact once.** Don't restate output the user can already see — no
  closing summary that re-lists findings, re-prints a diff, or re-describes an
  artifact just produced. A short pointer ("wrote `report.md`") is fine; re-dumping
  its contents is not.
- **Never cut the payload itself.** Terseness governs framing and repetition, not
  substance. A review still names every finding; a status table still shows every
  row. Compress the packaging, never the goods.

Two mechanisms give you *controlled* output rather than just less of it:

- **Templates** for strict structure — ship the exact skeleton with placeholders
  when the shape must be consistent.
- **Examples** for calibrated style — two or three input→output pairs teach tone
  and level of detail more precisely than any description. Examples are the
  pictures worth a thousand words; prefer a few canonical ones to an exhaustive
  catalog of edge cases.

And put the output-discipline expectation *in the skill's own body*, in plain
words, so it bites at runtime and not only while you're authoring. A canonical
line: *"Report tersely: no preamble or narration; state each fact once; don't
restate output the user can already see."*

---

## 12. Scripts and bundled files

Scripts are the most powerful thing you can bundle, because they move work *out*
of the probabilistic model and into deterministic code — and because an executed
script costs only its output in tokens. When you include them, hold them to real
engineering standards; a sloppy script is worse than none, since the agent will
trust it.

- **Solve, don't punt.** Handle the error inside the script instead of letting it
  fail out to the agent to puzzle over. `try/except` around the file read with a
  clear message beats a bare `open(path).read()` that throws a stack trace the
  agent then has to interpret. The script's job is to be *reliable*, so the agent
  can lean on it.
- **No voodoo constants.** Every magic number gets a comment justifying it.
  `TIMEOUT = 47` is a landmine: if *you* don't know why 47, the agent certainly
  can't reason about it. `REQUEST_TIMEOUT = 30  # p99 latency is 8s; 30 gives
  headroom without hanging the run` is a value the agent can trust and adjust.
- **Declare dependencies; assume nothing is installed.** State the packages and
  the install command. And know your runtime: some environments can install
  packages and reach the network, others cannot — design for the stricter case
  when in doubt.
- **Make intent explicit** — run vs. read, as in [§9](#9-progressive-disclosure-in-practice).

The same care extends to assets: name templates and data files for what they are,
keep them where the body says they'll be, and reference them one level deep.

---

## 13. Content hygiene and maintainability

A skill is a living document, and the most common way it rots is by encoding
*facts and dates* where it should encode *state and reasoning.*

**Never write time-conditional instructions.** The classic trap:

> ✗ "If you're doing this before August 2025, use the old API; after, use the new
> one."

This forces the model to re-litigate a decision every run and silently goes wrong
the moment the date passes. Structure by *state* instead:

> ✓ A **Current method** section stating the present truth, with any legacy detail
> quarantined in a collapsed **Old patterns** block tagged with its deprecation
> date.

The current path stays correct without edits; history is available but out of the
way. The same discipline applies to a **Known gotchas** section — often the most
valuable part of a mature skill, because it captures failures discovered through
real runs ("scanned PDFs return an empty list silently — check the page type
first"). Gotchas are gold, but stale gotchas send the agent chasing ghosts, so
prune them as the underlying system changes.

The meta-principle: **prefer durable reasoning and current-state descriptions over
ephemeral facts.** Reasoning ages slowly; dated facts age overnight.

---

## 14. Portability

The skill format is an open standard that many agents now read, and that is a
quiet superpower — a well-authored skill can run unchanged across a whole
ecosystem. But it only holds if you stay within the portable core.

**The portable core, honored everywhere:** the `name` and `description` fields, a
plain-Markdown body, and — as inert documentation only — `license` and `metadata`.
Author to this set and your skill travels.

**Everything else is a platform-specific extension** that other runtimes silently
strip or ignore: tool-permission fields, model-invocation toggles, argument
declarations, model or effort pins, execution-context directives. They may be
genuinely useful on the runtime that supports them — but *never rely on them for
correctness or, especially, for security*, because off-platform they simply vanish
and the skill runs with defaults. A skill whose safety depends on a tool
restriction that another agent ignores is a skill with a hole in it.

Two portability traps worth naming:

- **`SKILL.md` is case-sensitive.** `skill.md` or `Skill.md` will be ignored on a
  case-sensitive filesystem. Get the capitalization exact.
- **Dynamic body features are not portable.** Inline shell execution and argument
  substitution (`$ARGUMENTS`, `$1`, `` !`cmd` ``) are runtime-specific. For a
  portable skill, detect mode and arguments by *reading the user's prose* in the
  body rather than relying on substitution the next runtime won't perform.

For anything with side effects — commits, deploys, file edits, external sends —
don't lean on a platform's invocation-guard field to protect the user. Build the
guardrail into the body: state the irreversible step explicitly and require
confirmation before it. That protection travels; a frontmatter flag does not.

---

## 15. Evaluation-driven authoring

You cannot reason your way to a reliable skill. Instructions are non-deterministic
artifacts; the only way to know one works is to *watch it run.* Treat skill
authoring the way you'd treat test-driven development — in fact, treat it as
exactly that.

**Write the test before the skill.** The discipline in one line: *no skill without
a failing test first.* Run the agent on a representative task **without** your
skill and watch it fail — actually observe the specific way it goes wrong. That
failure is your specification. If you never saw the agent fail unaided, you don't
know whether your skill teaches the *right* thing or merely a plausible thing.

The loop:

1. **Find the gap.** Run the real task with no skill; document exactly where and
   how the agent stumbles.
2. **Write evaluations.** Encode those failures as at least three concrete
   scenarios — a representative request plus 2–4 checkable expectations of correct
   behavior. These evals are your source of truth from here on.
3. **Baseline.** Confirm the agent fails (or underperforms) the evals without the
   skill.
4. **Write the minimum.** Add only enough instruction to pass — nothing
   speculative, nothing "just in case."
5. **Iterate against the evals**, not against your imagination.

**Use pressure, not quizzes.** Test with realistic, high-stakes scenarios — the
production incident, the sunk-cost trap, the deadline — not gentle comprehension
checks. A skill that holds only when nothing is at stake hasn't been tested. And
close the loopholes: violating the *letter* of a rule to escape its *spirit* is a
failure your evals should try to provoke.

**Two-agent iteration.** Author and refine with one agent instance ("A"), then
test with a *fresh* instance ("B") that has none of the authoring context. B
reveals what a real user's agent will actually do; feed B's specific stumbles back
to A. You don't need a special "skill-writing" mode to do this — the format is
native to the model.

**Watch the trajectory, not just the result.** How the agent *navigates* your
skill is diagnostic:

| Observation                         | What it means                      | Fix                                                                                |
|-------------------------------------|------------------------------------|------------------------------------------------------------------------------------|
| Reads files in an unexpected order  | your structure isn't intuitive     | reorganize; make the entry path obvious                                            |
| Misses a reference link             | the link isn't prominent enough    | surface it earlier / more explicitly                                               |
| Re-reads one file every run         | that content belongs in the body   | promote it into `SKILL.md`                                                         |
| Never opens a file                  | it's dead weight                   | cut it, or signal its value better                                                 |
| Follows the description, skips body | the description leaks the workflow | trim it to *when*, not *how* ([§5](#5-the-description-the-highest-leverage-field)) |

**Test across the models you'll deploy on.** A skill is an *addition* to a model's
own ability, so the gap it must fill differs by model — what a stronger model
infers from a hint, a smaller one needs spelled out. Author for the weakest target
you support.

---

## 16. Anti-patterns catalog

A consolidated list of the failure modes named throughout, for fast reference.

| Anti-pattern                                  | Why it fails                                    | Do instead                                   |
|-----------------------------------------------|-------------------------------------------------|----------------------------------------------|
| Vague description ("helps with documents")    | never triggers reliably                         | specific *what* + *when* + trigger terms     |
| Description that summarizes the workflow      | agent acts on the summary, skips the body       | say *when to use*, not *how it works*        |
| First-person / mixed POV in the description   | hurts discovery                                 | third person, always                         |
| Explaining what the model already knows       | distractor tokens; dilutes attention            | assume competence; add only the gap          |
| "Just in case" bloat                          | measurably degrades the task (context rot)      | minimal high-signal tokens                   |
| Over-constraining out of fear                 | brittle; fails on any deviation                 | match freedom to fragility                   |
| Under-specifying                              | model guesses; inconsistent results             | give concrete signals and constraints        |
| Bare `ALWAYS`/`NEVER` with no reason          | followed to the letter, missed around the edges | state the rule, then the *why*               |
| Inconsistent terminology                      | synonyms read as distinct concepts              | one term per concept                         |
| Deeply nested references                      | partial previews → incomplete reads             | one level deep from `SKILL.md`               |
| Long reference with no ToC                    | preview reveals only the top                    | table of contents at the head                |
| Monolithic reference file                     | loads everything for any question               | split by domain                              |
| Vague filenames (`doc2.md`)                   | agent can't tell what to open                   | name for content                             |
| Offering many options ("use X or Y or Z…")    | forces the agent to spend reasoning choosing    | one default + an escape hatch                |
| Chatty runtime output                         | self-poisons context; double token cost         | terse framing, full payload                  |
| Scripts that punt errors to the agent         | agent must interpret raw failures               | solve in the script; clear messages          |
| Voodoo constants                              | agent can't reason about unexplained values     | justify every magic number                   |
| Time-conditional instructions ("before Aug…") | silently wrong once the date passes             | structure by state: current vs. old patterns |
| Relying on non-portable frontmatter           | silently ignored off-platform; security holes   | portable core; guardrails in the body        |
| Windows-style backslash paths                 | break on other systems                          | forward slashes always                       |
| Shipping untested                             | deploying untested code                         | eval-driven; watch it fail first             |

---

## 17. The scorecard

Principles teach judgment; a rubric makes judgment *checkable*. Score any skill
against these ten dimensions to catch the great majority of quality problems
before it ships. Each is worth up to the points shown; a skill scoring **90+**
with **no zero in any Critical row** is in excellent shape.

| #  | Dimension              | Tier     | Max | What full marks looks like                                                            |
|----|------------------------|----------|-----|---------------------------------------------------------------------------------------|
| 1  | Description — triggers | Critical | 15  | Third person; states *when*; concrete trigger terms; leads with the primary case      |
| 2  | Description — no leak  | Critical | 10  | Describes *when to use*, not the step-by-step workflow                                |
| 3  | Frontmatter validity   | Critical | 10  | Portable core only; `name` matches dir; valid YAML; within limits                     |
| 4  | Body density           | Critical | 15  | Assumes a capable reader; no explaining the known; every line earns its tokens        |
| 5  | Degrees of freedom     | Standard | 10  | Specificity matches task fragility; neither brittle nor vague                         |
| 6  | Progressive disclosure | Standard | 10  | Lean body; detail in references one level deep; ToCs; domain-split; run-vs-read clear |
| 7  | Rule + reasoning       | Standard | 8   | Rules carry their *why*; bare imperatives reserved for fragile steps                  |
| 8  | Output discipline      | Standard | 8   | Body mandates terse output; payload always stated in full                             |
| 9  | Maintainability        | Standard | 6   | No time-conditional content; state-based structure; gotchas current                   |
| 10 | Evaluations            | Critical | 8   | ≥ 3 real scenarios built from observed failures; ≥ 1 asserts terse output             |

**How to use it.** Score honestly, not generously — the scorecard is worthless if
you talk yourself past a weak row. A **zero in any Critical row is a blocker
regardless of total**, because those five dimensions are the ones that make a skill
fail *silently*: it won't error, it just won't be found, won't be read, or won't
be trusted. Fix Critical rows first, then climb the Standard rows toward 90.

The scorecard is downstream of the principles, not a substitute for them. It will
catch the routine 90–95% of quality problems. The remaining few — the genuinely
novel situation — is exactly why you read the reasoning in §§2–15 rather than only
this table.

---

## 18. Worked example: bad → good

The same skill, first as commonly written, then repaired. Read the two side by
side; every change traces to a section above.

### Before

```markdown
---
name: Commit Helper
description: I can help you with git commits and other git stuff.
disable-model-invocation: false
allowed-tools: Bash
---

# Commit Helper

Git is a version control system used by developers to track changes in their
code. A commit is a snapshot of your changes. This skill helps you write good
commit messages.

When writing a commit, you should ALWAYS follow conventional commits. NEVER write
a bad commit message. You can use many formats — you could use conventional
commits, or gitmoji, or just a plain summary, whatever seems best.

Steps:
1. Look at the changes.
2. Write a message.
3. Commit it.

If you are working after 2024, remember the team switched to requiring a scope in
every commit.
```

What's wrong: name has a space and capitals and doesn't match a valid directory
([§6](#6-naming)); description is first person, vague, and non-triggering
([§5](#5-the-description-the-highest-leverage-field)); frontmatter carries
non-portable fields ([§14](#14-portability)); the body explains what git and
commits are ([§7](#7-the-body-writing-for-a-capable-reader)); bare `ALWAYS`/`NEVER`
with no reasoning ([§7](#7-the-body-writing-for-a-capable-reader)); offers a menu
of formats instead of one default ([§16](#16-anti-patterns-catalog)); the steps
are hollow; and it encodes a dated conditional ([§13](#13-content-hygiene-and-maintainability)).

### After

```markdown
---
name: writing-commit-messages
description: >
  Writes Conventional Commits messages from staged changes, with a required
  scope and an imperative subject. Use when the user asks to commit, write or
  amend a commit message, or review staged changes.
---

# Writing commit messages

Produce a Conventional Commits message for the staged diff. Use the format
`type(scope): subject`, where `scope` is required — our history is filtered by
scope, so a scopeless commit is invisible to release tooling.

## Steps

1. Read the staged diff (`git diff --cached`). If nothing is staged, say so and
   stop — do not stage files yourself.
2. Choose the `type` from: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`.
3. Derive the `scope` from the primary package or component touched.
4. Write the subject in the imperative mood, ≤ 50 chars, no trailing period.
   Imperative because it completes the sentence "This commit will…".
5. If the change is non-obvious, add a body explaining *why*, wrapped at 72
   chars. Skip the body for trivial changes.
6. Show the full message and ask for confirmation before running `git commit`.

## Examples

    feat(auth): add refresh-token rotation

    fix(parser): handle empty header rows without panicking

    Empty header rows produced a nil map access downstream. Guard the
    header parse and treat a blank row as "no headers".

Report tersely: show the message and the confirmation prompt, nothing else.
```

What changed and why: valid gerund name matching its directory; a third-person
description that states *when* and carries triggers without leaking the procedure;
portable frontmatter, folded scalar for the colon-bearing description; a body that
assumes git fluency and spends its tokens only on *this team's* rule (required
scope) — with the reasoning attached, so the model generalizes; one format, no
menu; concrete steps including a confirmation gate before the irreversible commit
([§14](#14-portability)); real examples that calibrate style
([§11](#11-output-discipline)); a state-based rule instead of a dated conditional;
and an explicit terse-output line.

---

## 19. The authoring checklist

The fast pre-flight. Every box should be tickable before a skill ships.

- [ ] `name` is lowercase-hyphen, ≤ 64 chars, equals the directory name, no
      reserved words.
- [ ] Frontmatter is the portable core (`name` + `description`, plus `license`/
      `metadata` only if needed); no runtime-specific fields relied on.
- [ ] `description` is third person, states *what* + *when*, leads with the
      primary case, carries concrete triggers, and does **not** leak the workflow.
- [ ] YAML is valid — folded scalar (`description: >`) for any colon or multi-line.
- [ ] Body assumes a capable reader; nothing explains what the model already knows.
- [ ] Body is lean (~≤ 500 lines / a few thousand tokens); heavy detail is pushed
      to references.
- [ ] Degrees of freedom match task fragility — neither brittle nor vague.
- [ ] Rules carry their reasoning; bare imperatives reserved for fragile steps.
- [ ] One term per concept throughout.
- [ ] References are one level deep; long ones have a ToC; files split by domain
      and named for content; forward slashes only.
- [ ] Scripts (if any) solve rather than punt, justify every constant, declare
      dependencies, and say run-vs-read.
- [ ] Multi-step work has numbered steps / a checklist; quality-critical work has a
      validate→fix loop; risky work validates a plan before executing.
- [ ] Body mandates terse output; payload is always stated in full.
- [ ] No time-conditional content; legacy detail is quarantined and dated.
- [ ] Irreversible steps confirm in the body, not via a non-portable flag.
- [ ] ≥ 3 evaluations built from observed failures; ≥ 1 asserts terse output; the
      skill was watched failing *without* it first.
- [ ] Scores 90+ on [the scorecard](#17-the-scorecard) with no zero in a Critical
      row.

---

## 20. Sources and further reading

This document synthesizes primary guidance and practitioner experience rather than
quoting it; the sources below are where to go deeper on any one thread.

- **Anthropic — Skill authoring best practices.** The single densest official
  source: frontmatter rules, progressive disclosure, degrees of freedom, the
  anti-patterns, and the evaluation loop.
  `platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices`
- **Anthropic Engineering — Equipping agents for the real world with Agent
  Skills.** The design rationale and the three-tier loading model.
  `anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills`
- **Anthropic Engineering — Effective context engineering for AI agents.** Why the
  always-loaded surface must stay small; the attention-budget argument.
  `anthropic.com/engineering/effective-context-engineering-for-ai-agents`
- **Anthropic Engineering — Writing effective tools for agents.** Token-efficient
  interfaces; how output becomes next-turn input.
  `anthropic.com/engineering/writing-tools-for-agents`
- **The Agent Skills open specification.** The portable field set, naming rules,
  and directory layout that make a skill travel across runtimes.
  `agentskills.io/specification`
- **Chroma — Context Rot.** The empirical backbone for "bloat degrades
  performance": measured reliability decline as input grows.
  `trychroma.com/research/context-rot`
- **Jesse Vincent (obra) — the `superpowers` skills and "Superpowers" post.** The
  sharpest practitioner doctrine: description-as-trigger, test-driven skills, and
  closing loopholes. `github.com/obra/superpowers` · `blog.fsck.com`
- **Simon Willison — "Claude Skills are awesome…"** The clearest statement of the
  token economics that make skills beat heavier alternatives.
  `simonwillison.net/2025/Oct/16/claude-skills/`

---

*Write skills the way you'd want a specialist to work: findable when needed,
silent when not, precise about the one thing you can't do yourself, and honest
about where the edges are. Everything above is in service of those four.*
