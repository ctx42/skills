<!-- Eval fixture: deliberately defective, written to the neutral eval
     standard (srd/evals/mocks/srd/fixtures/srd-standard.md). Its planted
     defects are the regression baseline of srd:review's fixture scenario; see
     CONTRIBUTING.md before changing it. -->

# Widget Export

| Field      | Value                               |
|------------|-------------------------------------|
| Summary    | Define rules for exporting widgets. |
| Maintainer | @alice                              |
| Reviewers  | @alice                              |
| Tracking   | none                                |
| Lifecycle  | APPROVED                            |
| Mockups    | <TODO: link to the mockup set>      |

## Introduction

This document MUST be read by every engineer. It describes how the system
exports widgets.

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in RFC 8174.

## Boundaries

### Included

- Exporting widgets to CSV.
- Scheduling recurring exports.

### Excluded

- Importing widgets.

## Terms

### Export Job

A background task that writes widgets to a file. The system MUST delete each
job after seven days.

## Requirements

### Export (EXP)

- `EXP-1` The system MUST validate the export request and log every
  validation failure.
- `EXP-3` The export MUST be fast.
- `EXP-3` The system MUST colourise the status badge in the export dialogue.
- `EXP-4` The system MUST import widgets from CSV before every export run.
