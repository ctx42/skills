# Requirements Specification Standard

<!-- EVAL TEST DATA ONLY — never a runtime source. The srd skills read the
     project's standard through the MCP server (`get_doc` with the
     `srd-standard` id from project-config.md). This neutral standard was
     written for these evals and belongs to no organization. It deliberately
     differs from real standards in its identifiers, fields, values, and
     layout, so a skill that hardcodes rules instead of reading them fails.
     Change it only together with the scenarios graded on it. -->

This standard defines what a Software Requirement Document (SRD) must contain
and how its requirements are written. Every rule below is a checkable
statement with a stable identifier, so a finding can name the rule it breaks.
Check a document in layout order: header, Introduction, Conventions,
Boundaries, Terms, Requirements.

## Contents

- Terms
- Rules: Document Layout (`DOC`), Lifecycle (`LIF`), Clarity (`CLR`),
  Requirement Shape (`RQT`), Terminology (`TRM`), Boundaries (`BND`)
- Acceptance Gate

The identifiers of these rules (`DOC-*`, `RQT-*`, and so on) belong to this
standard. An SRD never quotes them as its own requirements, and it never
contains worked examples of good or bad wording.

# Terms

## Specification

An SRD: a document that states what a system or feature must do, precisely
enough to build and to check.

## Requirement

One identified statement of a behavior, rule, or limit the system must meet.

## Single-Rule Requirement

A requirement that states one behavior, rule, or limit and nothing else.

## Obligation Word

One of the words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD
NOT, RECOMMENDED, MAY, and OPTIONAL, with the meaning RFC 2119 and RFC 8174
give it when written in capitals.

## Checkable

Able to be confirmed by a test, an inspection, a demonstration, or an
analysis.

## Acceptance Signal

A measurable condition that turns a quality into a pass-or-fail check.

## Included Item

One line in the Boundaries section naming a change the SRD delivers.

## Excluded Item

One line in the Boundaries section naming a change the SRD deliberately does
not deliver.

## Shared Terms

The term list shared by every specification of the organization. It lives
outside any single SRD.

## Acceptance Gate

The checks an SRD must pass before it can be approved.

# Rules

## Document Layout

**DOC-1:** An SRD MUST open with a header table of two columns, "Field" and
"Value", holding the fields "Summary", "Maintainer", "Reviewers", "Tracking",
"Lifecycle", and "Mockups".

**DOC-2:** "Maintainer" MUST name exactly one person, and "Reviewers" MUST name
at least one person other than the maintainer.

**DOC-3:** "Tracking" MUST link to the SRD's work item in the issue tracker.

**DOC-4:** The work item MUST link back to the SRD.

**DOC-5:** When the SRD changes what users see, "Mockups" MUST link to the
mockup set for the change.

**DOC-6:** The mockup set MUST link back to the SRD.

**DOC-7:** When the SRD changes nothing users see, "Mockups" MUST hold the value
"none".

**DOC-8:** An "Introduction" section MUST follow the header and state the
document's purpose and, in outline, what the system will and will not do.

**DOC-9:** A "Conventions" section MUST follow the Introduction and quote the
RFC 2119 and RFC 8174 notice on obligation words.

**DOC-10:** An SRD MUST have exactly one "Boundaries" section, holding an
"Included" list and an "Excluded" list.

**DOC-11:** An SRD MUST have a "Terms" section when it uses a term that needs a
definition and is missing from Shared Terms.

**DOC-12:** An SRD MUST have a "Requirements" section holding every requirement.

**DOC-13:** The sections MUST appear in this order when present: header,
Introduction, Conventions, Boundaries, Terms, Requirements.

**DOC-14:** Additional sections MAY appear only after the Requirements section.

## Lifecycle

**LIF-1:** "Lifecycle" MUST hold one of "DRAFT", "IN REVIEW", "APPROVED", or
"WITHDRAWN".

**LIF-2:** An SRD whose "Mockups" is not "none" MUST NOT be "APPROVED" before
its mockup set is signed off.

**LIF-3:** An SRD MUST NOT be "APPROVED" before it passes the Acceptance Gate.

**LIF-4:** While an SRD is "DRAFT", its requirement identifiers MAY be
renumbered.

**LIF-5:** Once an SRD is "IN REVIEW" or later, its requirement identifiers
MUST NOT be renumbered.

**LIF-6:** Once an SRD is "APPROVED", a change to the meaning of a requirement
MUST be signed off by its reviewers and recorded in a "Change Log" section.

**LIF-7:** Once an SRD is "APPROVED", a wording fix that keeps every
requirement's meaning MAY be made without sign-off.

**LIF-8:** A requirement removed once the SRD is "IN REVIEW" or later MUST keep
its identifier, and its text MUST start with "(withdrawn)".

## Clarity

**CLR-1:** A requirement MUST be in the present tense and active voice, with
the acting component as its subject.

**CLR-2:** A requirement SHOULD be one sentence of at most 30 words.

**CLR-3:** Obligation words MUST carry their RFC meaning only in the
Requirements section; elsewhere they are written in lowercase, except in the
Conventions notice.

**CLR-4:** An obligation word MUST be in capitals when it carries its RFC
meaning.

**CLR-5:** A requirement SHOULD state behavior, not layout or color, unless the
layout or color is itself the requirement.

**CLR-6:** A requirement MUST NOT use a double negative.

**CLR-7:** A requirement MUST NOT end a list with an open phrase such as "etc.",
"and so on", or "including but not limited to".

## Requirement Shape

**RQT-1:** A requirement MUST state exactly one behavior, rule, or limit.

**RQT-2:** A requirement MUST be a list item that starts with its identifier in
backticks followed by one space, as in "- `PAY-3` The service …".

**RQT-3:** A requirement identifier MUST be unique in the document.

**RQT-4:** Identifiers in a group MUST increase by one, with no gaps.

**RQT-5:** A requirement MUST be checkable.

**RQT-6:** A requirement MUST NOT rest on a vague quality such as "fast",
"robust", or "intuitive"; it MUST give an acceptance signal instead.

**RQT-7:** A requirement MUST NOT contain an example or a note. Reasons go in a
"Rationale" list placed after the requirement group.

**RQT-8:** An identifier's group code MUST be two to five capital letters.

## Terminology

**TRM-1:** A Terms entry MUST only define its term and MUST NOT state behavior
or obligations.

**TRM-2:** A behavior found in a Terms entry MUST move to the Requirements
section, or be deleted when a requirement already states it.

**TRM-3:** Every term in a requirement that needs a definition MUST be defined,
in the Terms section or in Shared Terms. Product, service, and device names
need no definition.

**TRM-4:** The first use of a term defined in Shared Terms MUST link to its
Shared Terms entry.

**TRM-5:** A link to Shared Terms MUST point at the term's own entry, not at the
list as a whole.

**TRM-6:** A product, service, or device name MAY appear without a link, even
when Shared Terms lists it.

**TRM-7:** A term defined in the SRD's own Terms section needs no link.

## Boundaries

**BND-1:** Each Included and Excluded item MUST name one change in one line.

**BND-2:** Every Included item MUST be covered by at least one requirement.

**BND-3:** No requirement MAY contradict an Excluded item.

# Acceptance Gate

An SRD passes the gate when all of these hold:

1. A reader new to the topic can read the Introduction, Boundaries, Terms, and
   one requirement group, and then explain correctly what the system must do.
2. Every Included item is covered, and no requirement contradicts an Excluded
   item.
3. A tester can write a check for every requirement without asking the
   maintainer.
4. No rule hides in the header or in the Terms section.
5. Identifiers are unique and run without gaps in every group.
