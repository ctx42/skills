# SRD Standard

The rule set every SRD must satisfy. `create` authors against these rules,
`edit` edits against them, and `review` reviews against them. Each rule
keeps its identifier so a finding can cite it. The checks that verify these
rules live in [srd-checklist.md](srd-checklist.md); each skill applies its own
action policy on a finding.

## Contents

- Introduction
- Glossary
- Scope (`SC`, `OSC`)
- Requirements: Document Structure (`STR`), Status and Changes (`STA`),
  Language and Style (`LANG`), Requirement Form (`REQ`), Glossary Discipline
  (`GLO`), Scope Discipline (`SCO`), Markdown Export (`MD`)
- Quality Bar

Two things belong to the standard and MUST NOT be copied into the SRD being
written:

- The rule identifiers (`STR-*`, `REQ-*`, …) name the rules; they are not part
  of a user's document.
- A real SRD carries no `Example` / `Don't` / `Do` annotations. They are a
  teaching device only (REQ-7); the Bad→Good examples live in
  [authoring-guide.md](authoring-guide.md).

> The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
> "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in an
> SRD are to be interpreted as described in
> [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
> [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
> appear in all capitals, as shown here.

# Introduction

A Software Requirement Document (SRD) is a written specification: a document
that states what a system or feature must do. It must be clear enough that an
engineer can build the feature, and a reviewer can confirm it was built
correctly. An SRD is not a design document or a project plan. It records the
rules the work must meet. It does not say how the code is built or when it
ships.

We write SRDs so that the intent is recorded once, in a clear way, and shared
with everyone who works on it. A good SRD lets an engineer start without
guessing. It lets a reviewer write a test for each rule. It lets a new team
member understand the system by reading it. A weak SRD hides decisions behind
vague words. It buries rules inside definitions. It leaves gaps that appear
later as extra work.

This standard is for everyone in that process. This includes product owners and
analysts who capture the intent, engineers who build it, and reviewers who
approve it. It explains the shape every SRD should have, the language to use,
and the common mistakes to avoid.

# Glossary

## SRD (Software Requirement Document)

A written document that states what a system or feature must do. It is organized
so that each rule can be built and checked.

## Requirement

A single numbered statement of one rule, behavior, or limit that the system must
meet.

## Atomic Requirement

A requirement that states exactly one rule, behavior, or limit.

## Normative Keyword

A keyword from the set defined in RFC 2119 and RFC 8174: MUST, MUST NOT,
REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY, and OPTIONAL.
It shows how strong a rule is. It carries this meaning only when written in
capital letters.

## Verifiable

A quality of a requirement that can be checked. A practical method exists to
confirm it: a test, an inspection, a demonstration, or an analysis.

## Verifiable Criteria

Clear, testable conditions that make a quality or behavior measurable, not a
matter of opinion.

## In Scope

A statement of something the document will define or deliver.

## Out of Scope

A statement of something the document does not cover on purpose.

## Design Tool

A software application used to create and review user-interface designs.

## Initiative

A large piece of work, tracked in the ticketing system, that groups related
features and tasks under one goal.

## Ticketing System

The software application used to plan and follow initiatives, features, and
tasks.

## Markdown

A simple text format that uses plain marks, such as # for headings and \* for
lists, to show structure in plain text.

## Status

The current state of an SRD in its life cycle. The status is one of:

- `In Progress`: The SRD is still being written or changed.
- `Proposed`: The SRD is ready for review. It may still change significantly
  until accepted or rejected.
- `Accepted`: The SRD has been reviewed and approved for use. Its requirements
  are now stable.
- `Rejected`: The SRD has been reviewed and turned down.

## User Interface (UI)

The parts of the system that a user sees and works with, such as screens,
buttons, and forms.

## Quality Bar

The lowest standard an SRD must meet to be accepted.

# Scope

## In Scope

**SC-1:** The required sections of an SRD and the order in which they appear.

**SC-2:** The metadata fields an SRD must contain and how they link to the
ticketing system and the design tool.

**SC-3:** The status values and the rules for changing an SRD across its life
cycle.

**SC-4:** The language and style used in an SRD document.

**SC-5:** The form, numbering, and labeling of individual requirements.

**SC-6:** The rules for glossary entries.

**SC-7:** The rules for scope statements.

**SC-8:** The quality bar an SRD must meet to be accepted.

**SC-9:** The Markdown format used when an SRD is exported to Markdown.

## Out of Scope

**OSC-1:** The detailed steps, meetings, and tools used to review and approve an
SRD, beyond the rules in this document.

**OSC-2:** The choice of editor, platform, or tool used to write an SRD.

**OSC-3:** Project management topics such as scheduling, estimates.

**OSC-4:** The subject-specific content of any single SRD.

# Requirements

## Document Structure

**STR-1:** An SRD MUST have a metadata block at the top. A metadata block is a
short list of key facts about the document. It MUST include at least the
"Objective", "Owners", "Initiative", "Status", and "Designs" fields.

**STR-2:** The "Owners" field MUST list at least two owners: a primary owner and
a secondary owner. The secondary owner takes over when the primary owner is
away, for example, during illness or another absence.

**STR-3:** The "Initiative" field in the metadata block MUST link to the
matching initiative in the ticketing system.

**STR-4:** The matching initiative MUST link back to the SRD.

**STR-5:** When an SRD changes the user interface (UI), its "Designs" field MUST
link to the approved design in the design tool.

**STR-6:** The approved design MUST link back to the SRD.

**STR-7:** When an SRD does not change the UI, its "Designs" field MUST contain
the value "N/A" (not applicable).

**STR-8:** Every SRD MUST place the RFC 2119 and RFC 8174 keyword notice
directly below the metadata block.

**STR-9:** An SRD MUST have an introduction. The introduction MUST state the
purpose of the document, and at a high level, what the system will and will not
do.

**STR-10:** When an SRD uses terms that need a definition and are not in the
shared glossary, it MUST have a glossary that defines them.

**STR-11:** An SRD MUST have exactly one Scope section. The Scope section MUST
contain an "In Scope" part and an "Out of Scope" part.

**STR-12:** An SRD MUST have a "Requirements" section. This section MUST contain
every numbered requirement.

**STR-13:** An SRD MUST keep these sections in this order relative to each
other, when they are present: the metadata block, "Introduction", "Glossary",
"Scope", and then "Requirements".

**STR-14:** An SRD MAY add other sections, placed between or after the required
sections.

## Status and Changes

**STA-1:** The "Status" field MUST be one of: "In Progress", "Proposed",
"Accepted", or "Rejected".

**STA-2:** An SRD that requires changes to the UI MUST NOT have a "Status" of
"Accepted" unless the linked design is also approved.

**STA-3:** An SRD MUST NOT have a "Status" of "Accepted" unless it meets the
Quality Bar.

**STA-4:** After an SRD is "Accepted", an edit MUST NOT add, remove, or change a
requirement, unless the approving authority agrees to the change.

**STA-5:** An "Accepted" SRD MAY receive edits that do not change its
requirements, such as fixing a typo or making a statement or requirement
clearer.

**STA-6:** Before an SRD is "Accepted", the author MAY renumber its requirements
freely.

**STA-7:** After an SRD is "Accepted", the author MUST NOT renumber its
requirements.

**STA-8:** After an SRD is "Accepted", the author MUST show a removed
requirement with strikethrough (crossed-out text) and MUST keep its identifier.

## Language and Style

**LANG-1:** An SRD document MUST use active voice with "the system" as the
subject of most requirements.

**LANG-2:** An SRD document SHOULD keep sentences as short and direct as the
meaning allows. The goal is to be succinct.

**LANG-3:** A normative keyword MUST appear only inside the "Requirements"
section, except when it is named in the keyword notice or defined in the
glossary.

**LANG-4:** A normative keyword MUST be written in all capitals when it carries
its RFC 8174 meaning.

**LANG-5:** A requirement SHOULD describe what the system does, not how the user
interface looks or where its elements are placed. It MAY state appearance,
placement, or color only when that detail is itself a requirement.

**LANG-6:** A requirement SHOULD state its rule in a positive form, not as a
double negative.

**LANG-7:** A requirement MUST NOT use open-ended phrases, such as "including
but not limited to", that leave a list unfinished. The only exception is when
the list is meant to grow and the test method allows for it.

## Requirement Form

**REQ-1:** Each requirement MUST state exactly one rule, behavior, or limit.

**REQ-2:** Each requirement MUST start with a bold identifier, for example
`**GR-1:**`, followed by a space.

**REQ-3:** Each requirement identifier MUST be unique within the document.

**REQ-4:** Requirement identifiers MUST run in number order within their group.

**REQ-5:** Each requirement MUST be verifiable by a test, inspection,
demonstration, or analysis.

**REQ-6:** A requirement MUST NOT rely on a vague quality such as "secure",
"fast", or "user-friendly". It MUST state verifiable criteria instead.

**REQ-7:** A requirement MUST NOT carry an example, a note, or any other extra
text. It MUST be the rule and nothing more.

**REQ-8:** A requirement identifier's letter prefix (its code) SHOULD be three
or four letters long. A code of another length MAY be used only when no clear
three- or four-letter code fits the group.

## Glossary Discipline

**GLO-1:** A glossary entry MUST only define a term. It MUST NOT describe system
behavior, rules, or required actions.

**GLO-2:** A behavior statement that appears in a glossary entry MUST be moved
to the "Requirements" section. If it repeats another rule, it MUST be removed
instead.

**GLO-3:** Every term used in a requirement MUST be defined, either in the SRD's
"Glossary" section or in the shared glossary.

## Scope Discipline

**SCO-1:** Each scope item MUST be atomic and verifiable.

**SCO-2:** Every "In Scope" item MUST be covered by at least one requirement.

**SCO-3:** A requirement MUST NOT go against an "Out of Scope" item.

## Markdown Export

**MD-1:** When an SRD is exported to Markdown, the result MUST be valid
Markdown.

**MD-2:** When an SRD is exported to Markdown, a line SHOULD NOT be longer than
80 columns (characters).

# Quality Bar

An SRD is acceptable when all of these are true:

1. An engineer who is new to the topic can read the introduction, glossary,
   scope, and one requirements group, and then describe correctly what the
   system must do.
2. Every "In Scope" item is covered by the requirements, with no conflict.
3. A reviewer can write a test or check for every requirement, without asking
   the author for help.
4. The document hides no rules in its glossary or metadata.
5. The numbering is unique and easy to read, with no repeats and no large gaps.
6. The text reads as clear technical writing: short sentences, active voice,
   defined terms, and exact verbs.
