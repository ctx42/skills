# SRD Validation Checklist

The single action-neutral list of checks for an SRD. Each check is a yes/no
question tied to a rule id in [srd-standard.md](srd-standard.md). This file says
nothing about who fixes what or when: `create` self-checks against it,
`review` reviews against it, and `edit` re-validates against it — each
skill applies its own action policy on a finding.

Run the checks in document order. For the cross-cutting consistency checks, defer
to the consistency pass in [authoring-guide.md](authoring-guide.md); it is the
feedback loop, repeated until clean.

## Contents

- Metadata
- Introduction
- Glossary
- Scope
- Requirements
- Section order and Markdown
- House style
- Consistency
- Quality Bar

## Metadata

- Metadata block present with at least Objective, Owners, Initiative, Status,
  Designs? (STR-1)
- Owners lists >= 2 owners — a primary and a secondary? (STR-2)
- Initiative links to the matching initiative in the ticketing system? (STR-3)
- That initiative links back to the SRD? (STR-4)
- If the SRD changes the UI, Designs links to the approved design? (STR-5)
- That design links back to the SRD? (STR-6)
- If the SRD does not change the UI, Designs is `N/A`? (STR-7)
- Status is one of `In Progress`, `Proposed`, `Accepted`, `Rejected`? (STA-1)
- If UI-changing, not `Accepted` unless the linked design is approved? (STA-2)
- Not `Accepted` unless the Quality Bar is met? (STA-3)
- Keyword notice sits directly below the metadata block? (STR-8)
- No normative keyword used inside metadata? (LANG-3)

## Introduction

- Introduction present? (STR-9)
- States the purpose and, at a high level, what the system will and will not do?
  (STR-9)
- No normative keyword used here? (LANG-3)

## Glossary

- Every term that needs defining and is not in the shared glossary is defined
  here? (STR-10)
- Each entry only defines a term — no behavior, rule, or required action?
  (GLO-1)
- No behavior statement hidden in an entry — moved to Requirements, or removed
  if it duplicates a rule? (GLO-2)
- No normative keyword except inside a definition? (LANG-3)

## Scope

- Exactly one Scope section, with an `In Scope` part and an `Out of Scope` part?
  (STR-11)
- Each scope item is atomic and verifiable? (SCO-1)
- Every `In Scope` item is covered by >= 1 requirement? (SCO-2)
- No requirement contradicts an `Out of Scope` item? (SCO-3)

## Requirements

- A Requirements section contains every numbered requirement? (STR-12)
- Each requirement states exactly one rule, behavior, or limit (atomic)? (REQ-1)
- Each requirement starts with a bold identifier `**PFX-1:**` then a space?
  (REQ-2)
- Each identifier is unique in the document? (REQ-3)
- Identifiers run in number order within their group? (REQ-4)
- Each requirement is verifiable by test, inspection, demonstration, or
  analysis? (REQ-5)
- No vague quality (`secure`, `fast`, `user-friendly`) — verifiable criteria
  instead? (REQ-6)
- No example, note, or extra text in a requirement — the rule and nothing more?
  (REQ-7)
- Active voice, `the system` as the subject of most requirements? (LANG-1)
- Sentences as short and direct as the meaning allows? (LANG-2)
- Normative keyword appears only here, outside the notice and glossary? (LANG-3)
- Normative keyword is all-capitals when it carries its RFC 8174 meaning?
  (LANG-4)
- Describes what the system does, not how the UI looks or is laid out — unless
  that detail is itself the rule? (LANG-5)
- States the rule positively, not as a double negative? (LANG-6)
- No open-ended phrase ("including but not limited to"), unless the list is meant
  to grow and the test method allows it? (LANG-7)
- For an `Accepted` SRD: existing ids are not renumbered, and a removed
  requirement is shown struck through keeping its id? (STA-7, STA-8)

## Section order and Markdown

- Required sections in order: metadata, Introduction, Glossary, Scope,
  Requirements? (STR-13)
- Valid Markdown? (MD-1)
- No line longer than 80 columns? (MD-2)

## House style

- US English throughout (`color`, `behavior`, `standardize`)? (authoring-guide)
- One term per concept — no mixed synonyms for the same thing?
  (authoring-guide)

## Consistency

Run the consistency pass in [authoring-guide.md](authoring-guide.md):

- No requirement invalidates or contradicts another?
- Every `In Scope` item still covered; no requirement contradicts `Out of
  Scope`? (SCO-2, SCO-3)
- Identifiers still unique and in order, no collisions or large gaps? (REQ-3,
  REQ-4)
- Each term used consistently and still defined locally or in the company
  glossary? (GLO-3)

## Quality Bar

- All six Quality Bar items hold? (see the Quality Bar in
  [srd-standard.md](srd-standard.md))
