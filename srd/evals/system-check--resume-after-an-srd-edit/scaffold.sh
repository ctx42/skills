#!/usr/bin/env bash
set -euo pipefail
cat > project-config.md <<'EOF_PC'
---
mcp-server: srd-doc
kb: kb
initiatives: initiatives
srd-standard: docs/guidelines_for_software_requirements_documents.md
glossary: docs/glossary
---

# Project configuration (eval fixture)

EVAL TEST DATA ONLY. Copy this file to the root of a scenario's workspace so
the srd skills' gate finds a project; a scenario's `setup` overrides any key.
In an eval run, `srd/evals/mocks/srd-doc/fixtures/srd-standard.md` stands in for the
`get_doc` result of `srd-standard` — see `dev/eval/blind-runner-prompt.md`.
EOF_PC
mkdir -p specs kb
cat > specs/labeling.md <<'EOF_SRD'
# Sound File Labeling

|                |                                                                         |
|----------------|-------------------------------------------------------------------------|
| **Objective**  | Let users attach labels to recordings and record who attached each one. |
| **Initiative** | [INT-512](https://jira.example.com/browse/INT-512)                      |
| **Owners**     | @anna.keller, @marek.nowak                                              |
| **Status**     | IN PROGRESS                                                             |
| **Designs**    | N/A                                                                     |

> [!INFO]
> The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
> "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
> document are to be interpreted as described in
> [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
> [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
> appear in all capitals, as shown here.

## Introduction

This document specifies how the platform stores
[Labels](<../docs/glossary/machine_learning_glossary.md#Label>)
on a [Sound File](<../docs/glossary/main_glossary.md#Sound-File-(SND)>).
The system will let a user assign Labels to a Sound File, remove them, and look
them up. Each Label is kept as a
[Tag](<../docs/glossary/main_glossary.md#Tag-(TAG)>), and every
assignment is written to the Label Audit Log.

## Glossary

### Label Assignment

The association of one Label with one Sound File.

### Label Audit Log

The record of every Label Assignment and every rejected Label Assignment.

### Label Set

The Labels a Project allows its users to assign.

## Scope

### In Scope

**SC-1:** Assigning Labels to Sound Files.

**SC-2:** Removing Label Assignments.

**SC-3:** Auditing Label Assignments.

**SC-4:** Exporting a Project's Label Assignments as a CSV file.

### Out of Scope

**OSC-1:** Training machine learning models on labeled Sound Files.

**OSC-2:** Managing the Label Set of a Project.

## Requirements

### General (GR)

**GR-1:** The system MUST allow a user to assign a Label to a Sound File in a
[Project](<../docs/glossary/main_glossary.md#Project-(PRJ)>) the
user belongs to.

**GR-2:** The system MUST store each Label as a Tag.

**GR-3a:** The system MUST reject a Label Assignment whose Label is not in the
Sound File's Project's Label Set.

**GR-3b:** The system MUST record each rejected Label Assignment in the label
audit log.

**GR-4:** The system MUST write each Tag name as a slash-separated path.

**GR-5:** The system MUST delete every Label Assignment of a Tag when that Tag
is deleted.

**GR-6:** The system MUST NOT delete a Label Assignment that is older than 30
days.

**GR-7:** The system MUST answer a Tag lookup within 300 ms at the 95th
percentile for a Project holding up to 100 000 Tags.

**GR-8:** The system MUST let a user list every Label Assignment of a Sound
File.

**GR-9:** The system MUST limit the Labels offered to a user to the Label Set of
the Sound File's Project.

**GR-10:** Each Label Assignment is written to the Label Audit Log.

**GR-11:** The system MUST allow a user to remove a Label Assignment.

**GR-12:** The system MUST keep the Label Audit Log reliable.
EOF_SRD
cat > specs/labeling.questions.md <<'EOF_Q'
---
cfsync-plugin: ignore-push
---

# SRD Questions — Sound File Labeling

Source: `specs/labeling.md`

Open questions only. Resolved items are removed; durable facts are banked.

**Q1** GR-5 deletes a Tag's Label Assignments with the Tag, while GR-6 forbids
deleting any assignment older than 30 days. What should happen when someone
deletes a Tag that has old assignments?
<!-- review: #5 -->

**Q2** GR-3 both rejects an undefined Label and logs the rejection. Are those
two separate behaviors we test separately, and should a rejection always be
logged?
<!-- review: #3 -->

**Q3** GR-7 asks for Tag lookups to be "fast". What response time are we
committing to, and for what Project size? QA can't test "fast".
<!-- review: #6 -->

**Q4** SC-2 promises removing Label Assignments, but no requirement covers it.
Do we want removal in this SRD, and who may remove an assignment?
<!-- review: #2 -->

**Q5** GR-9 relies on a "Label Set" that nothing defines. What exactly is in a
Project's Label Set?
<!-- review: #8 -->

**Q6** GR-4 has us write Tag names as a slash-separated path, but the Tags
concept document says a Tag name is a comma-separated series of named nodes.
Which separator do Label Tags use?
<!-- review: #4 -->

**Q7** GR-10 writes every Label Assignment to the Label Audit Log, but the SRD
defines it only as a record, and no platform document describes such a log. Is
it an existing platform log, and if so which one, or is this SRD introducing a
new store?
EOF_Q
cat > specs/labeling.review.md <<'EOF_R'
---
prepared: 2026-09-28 10:05
updated: 2026-09-28 10:05
source: specs/labeling.md
cfsync-plugin: ignore-push
---

# SRD Review — Sound File Labeling

## Errata

- [ ] #7 [minor, linguistic] GR-8 uses British spelling: `labelling` →
  `labeling`. (SRD:house)

---

## Metadata

- [ ] #1 [blocker, structure] Metadata (Owners): only one owner is listed —
  add a secondary owner. (SRD:STR-2)

## Scope

- [ ] #2 [blocker, coverage] SC-2: no requirement covers removing a Label
  Assignment — add one or drop the item. (SRD:SCO-2)

## Requirements

- [ ] #3 [blocker, atomicity] GR-3: states two rules ("reject ... and log
  ...") — split into one rule each. (SRD:REQ-1)

- [ ] #4 [major, reference] GR-4: requires Tag names written as a
  slash-separated path, but the Tags concept document states Tag names are a
  comma-separated series of named nodes — align GR-4 with the platform format.
  (SRD:ref docs/concepts/tags.md)

- [ ] #5 [blocker, logical] GR-5 and GR-6: deleting a Tag must delete its
  Label Assignments, but an assignment older than 30 days must never be
  deleted; no rule says which wins — state the precedence. (SRD:consistency)

- [ ] #6 [blocker, verifiability] GR-7: "fast" is a vague quality with no
  criterion — state a measurable limit. (SRD:REQ-6)

- [ ] #8 [blocker, terminology] GR-9: "Label Set" is used but defined neither
  in the Glossary nor in the Company Glossary — define it. (SRD:GLO-3)

- [ ] #9 [major, linguistic] GR-10: passive voice with no subject ("Each Label
  Assignment is written ...") — make "the system" the subject. (SRD:LANG-1)
EOF_R
