# Writing guide

The standard `doc-smith` writes and judges against. Terse: one rule per line.
Applies to technical documentation and user manuals in Markdown.

## Contents

- Audience & purpose
- Content shapes
- User-manual structure
- Prose rules
- Procedures
- Formatting
- Defect taxonomy

## Audience & purpose

- Write for one named audience at one skill level; state prerequisites, don't
  assume them.
- Every document has a single purpose — teach a beginner, get a task done, or
  serve as lookup. Mixing them in one section confuses the reader; separate them.
- Lead with what the reader can do or decide, not with history or architecture.

## Content shapes

Match the section to the reader's goal; don't force one shape everywhere.

- Getting-started — a first success, happy path only, no edge cases or options.
- Task / how-to — numbered steps that achieve one stated goal, from a real
  starting state.
- Reference — exhaustive, orderly lookup (options, fields, errors); no narrative.
- Concept / explanation — the why and the model behind the product; no steps.

## User-manual structure

Typical order; include only what the product needs, omit empty sections:

- Overview — what the product is and who it's for, in two or three sentences.
- Prerequisites — accounts, access, versions, prior setup.
- Getting started — first end-to-end success.
- Tasks — the how-to sections, one goal each, ordered by how often they're used.
- Reference — settings, fields, limits, error messages.
- Troubleshooting — symptom → cause → fix.

## Prose rules

- Target clear, fluent professional English — solid CEFR B1 as the floor:
  grammatically complete, idiomatic, logically connected sentences, never
  primer-level fragments. Vocabulary tracks the audience's level; fluency never
  drops below this floor, whatever the audience.
- Present tense, active voice, second person ("you select"), not passive or
  future ("the button will be selected").
- US English spelling and conventions ("color", "canceled", "-ize"). Default for
  fresh docs; when editing a doc that consistently uses another variety, match
  it and flag mixed usage rather than convert wholesale.
- One term per concept, everywhere — pick it once and never vary it for style.
- In task and procedure prose, short sentences, one instruction each. In concept
  and overview prose, vary sentence length and join related ideas with
  conjunctions and transitions so reasoning flows — not staccato fragments.
- Say the condition before the action: "To export, select…", not "Select… to
  export."
- Cut filler ("simply", "just", "in order to", "please note that").
- When cutting filler, keep the sentence grammatically whole — trim the padding,
  don't strip it to a fragment or leave clipped clauses that read as choppy.
- Define an acronym or product term on first use; then use it consistently.
- Headings are specific and parallel in grammar ("Installing X", "Configuring X",
  not "Installation" then "How to configure").

Register example — the same facts, sub-B1 fragments raised to fluent B1:

- ✗ "Open the app. Go to Settings. It has options. You change them there."
- ✓ "Open the app and go to Settings, where you can change the available
  options."

## Procedures

- State the goal and the starting context before step 1.
- One user action per step; describe the result when it's not obvious.
- Number sequential steps; bullet unordered options.
- Name UI elements exactly as they appear, and by their label, not their look
  ("select **Save**", not "click the blue button").

## Formatting

- One H1 (title); nest headings without skipping levels.
- Code, commands, filenames, and literal UI labels in the appropriate inline or
  fenced code style; fenced blocks declare a language.
- Introduce every list, table, and code block with a sentence; none floats
  contextless.
- Alt text on every image; never put information only in an image.
- Wrap prose at ~80 columns; reflow every edited paragraph so no line exceeds
  it. Exempt code fences, table rows, headings, and unbreakable tokens (URLs,
  paths, links).
- Align table columns — pad cells so `|` delimiters line up in the source;
  re-pad the whole table when adding a row.
- Plain, spaced lists — items as plain sentences, no bold-label lead-ins;
  reserve `**bold**` for genuine emphasis. Blank line between prose-step items;
  keep dense enumerations (field/option lists) tight and unspaced.
- Match an existing doc's established convention (wrap width, table style, list
  spacing) when editing; apply these house defaults only when creating fresh or
  when the doc has no clear convention.

## Defect taxonomy

What audit reports and proofread fixes. Detection heuristic per class:

- Contradiction — two claims about the same entity that can't both hold. Detect
  from the ledger's entity/claim list, not by local reading; cite both spots.
- Terminology drift — a concept named two ways, or one name covering two
  concepts. Detect from the ledger's terminology map.
- Repetition — a point restated with no added information. Distinguish from
  deliberate reference restatement; flag only the redundant case.
- Structure defect — sections misordered, missing, empty, or mismatched to their
  content's purpose.
- Completeness gap — a referenced step, term, screen, prerequisite, or section
  that never appears; a task a reader cannot finish from the text.
- Clarity defect — passive/future voice, buried instruction, undefined term,
  filler, or a step with more than one action.
- Formatting defect — prose over the doc's wrap width, misaligned table columns,
  or bold-label list lead-ins. Proofread reflows, re-pads, and rewrites to plain
  items; audit flags. Respect the doc's own convention over the house default.
- Spelling-variety defect — non-US spelling in a US doc, or English varieties
  mixed within one doc. Proofread normalizes to the doc's variety (US default);
  audit flags.
- Flat/choppy prose — grammatical but sub-register: fragmentary or staccato
  sentences, missing connectives, unidiomatic phrasing. Proofread fixes it
  upward to fluent B1; distinct from filler (cut, not rewritten) and from
  vocabulary level (tracks the audience).
- Dubious technical claim — an assertion that looks factually wrong about a
  technology and the doc doesn't settle. Flag as a question; never rewrite.
