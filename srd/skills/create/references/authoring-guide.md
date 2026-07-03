# SRD Authoring Guide — House Extensions and Defect Classes

Practical guidance that extends the SRD standard in
[srd-standard.md](srd-standard.md). The standard's rules are normative; the
items here are this project's additions plus worked examples that help the agent
draft well and recognize defects during the self-check.

**These examples never go into an SRD.** Every `Bad`/`Good` pair below is
authoring guidance only. A real SRD carries the rule and nothing more (REQ-7).

## Contents

- House additions to the rules
- Consistency pass
- Defect classes (Bad → Good)
- Good atomic requirements

## House additions to the rules

- **US English.** Write SRDs in US English: `color`, `behavior`, `standardize`,
  `analyze`, `center` — not `colour`, `behaviour`, `standardise`. The self-check
  flags British spellings. (This governs the SRD artifact only.)
- **Sub-numbering allowed.** Within a group, tightly-coupled requirements MAY use
  letter suffixes — `**GR-1a:**`, `**GR-1b:**` — when it aids readability. Keep
  it shallow; do not nest deeper than one letter. Plain `**GR-1:**`, `**GR-2:**`
  remains the default; reach for suffixes only when several rules form one tight
  cluster.
- **Terminology consistency.** Use one term per concept throughout. Do not mix
  synonyms for the same thing (e.g. `MFA` / `2FA` / `two-factor`); pick one and
  define it once.

## Consistency pass

After every significant addition or change, re-read the whole draft from the top
and confirm:

- No earlier requirement was invalidated or contradicted by a later one.
- Every `In Scope` item is still covered by ≥ 1 requirement (SCO-2); no
  requirement contradicts `Out of Scope` (SCO-3).
- Numbering is still unique and in order, with no collisions or large gaps.
- Each term is used consistently and is still defined (locally or in the company
  glossary).

This pass is the self-check's feedback loop — repeat it until it is clean.

## Defect classes (Bad → Good)

### Glossary pollution — behavior hidden in a definition (GLO-1/2)

Bad:
> **Recovery Codes** — One-time codes that let a user regain access when their
> primary method is unavailable. The system MUST generate ten codes at setup and
> invalidate each after first use.

Good — definition only; the behavior moves to a requirement:
> **Recovery Codes** — One-time codes that let a user regain access when their
> primary authentication method is unavailable.

### Non-atomic requirement — several rules in one (REQ-1)

Bad:
> **GR-5:** The QR code MUST be 300×300 px, the user MUST be told to scan it, and
> setup MUST complete only after the device confirms registration.

Good — one rule each (sub-numbered because they form one cluster):
> **GR-5a:** The setup QR code MUST be rendered at 300×300 pixels.
> **GR-5b:** The instruction text MUST tell the user to scan the code with a
> compatible mobile device.
> **GR-5c:** The setup step MUST be marked complete only after the device
> registers the passkey.

### Vague / unverifiable quality (REQ-6)

Bad:
> **GR-7:** The system SHALL use strong authentication appropriate to the data.

Good — concrete, testable:
> **GR-7:** The system MUST require multi-factor authentication for every
> administrative action on data classified `Restricted`.

### Scope gap — In Scope item with no requirement (SCO-2)

Bad: `In Scope` declares "file handling" but no requirement addresses it.
Good: either add a requirement that covers file handling, or narrow the scope
item to what the requirements actually deliver.

### Duplicate / overlapping requirements (Quality Bar 2, consistency)

Two numbered requirements stating the same rule in different words. Keep the
clearer one; remove or merge the other so a reviewer never has to reconcile them.

### Terminology inconsistency

Using `MFA`, `2FA`, and `two-factor authentication` interchangeably when the
feature is specifically one of them. Choose one term, define it, and use it
everywhere.

## Good atomic requirements

Each states one rule, names `the system` (or a defined subject), uses an
all-capitals normative keyword, and is verifiable:

> **GR-2a:** A user account's Session Timeout MUST default to the Default Session
> Timeout of the Security Policy assigned to that account.
> **GR-2b:** The Session Timeout MUST NOT be longer than the Security Policy's
> Maximum Session Timeout.
> **GR-4b:** When a request arrives after the Session Timeout has elapsed, the
> system MUST reject the request and MUST NOT reveal whether the session ever
> existed.
