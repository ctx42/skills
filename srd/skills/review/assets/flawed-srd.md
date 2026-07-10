<!-- Eval fixture: deliberately defective. Expected findings: README.md. -->

# Widget Export

|                |                                     |
|----------------|-------------------------------------|
| **Objective**  | Define rules for exporting widgets. |
| **Initiative** | N/A                                 |
| **Owners**     | @alice                              |
| **Status**     | Accepted                            |
| **Designs**    | <TODO: link to the design>          |

> [!INFO]
> The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
> "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
> document are to be interpreted as described in
> [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
> appear in all capitals, as shown here.

## Introduction

This document MUST be read by every engineer. It describes how the system
exports widgets.

## Glossary

### Export Job

A background task that writes widgets to a file. The system MUST delete each
job after seven days.

## Scope

### In Scope

**SC-1:** Exporting widgets to CSV.

**SC-2:** Scheduling recurring exports.

### Out of Scope

**OSC-1:** Importing widgets.

## Requirements

### General (GR)

**GR-1:** The system MUST validate the export request and log every
validation failure.

**GR-3:** The export MUST be fast.

**GR-3:** The system MUST colourise the status badge in the export dialogue.

**GR-4:** The system MUST import widgets from CSV before every export run.
