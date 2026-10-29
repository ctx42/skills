<!-- Eval fixture: deliberately defective, written to the neutral eval
     standard (srd/evals/mocks/srd/fixtures/srd-standard.md). Its planted
     defects are the regression baseline of srd:review's fixture scenario; see
     craft/skills/skill-eval/references/tiers.md (Two agents) before
     changing it. -->

# Telemetry Replay

| Field      | Value                                        |
|------------|----------------------------------------------|
| Summary    | Define rules for replaying flight telemetry. |
| Maintainer | @noah.t                                      |
| Reviewers  | @noah.t                                      |
| Tracking   | none                                         |
| Lifecycle  | APPROVED                                     |
| Mockups    | <TODO: link to the mockup set>               |

## Introduction

This document MUST be read by every flight engineer. It describes how the
system replays downlink frames.

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in RFC 8174.

## Boundaries

### Included

- Replaying a flight's downlink frames on the Replay Timeline.
- Scheduling replays of recent flights.

### Excluded

- Editing stored downlink frames.

## Terms

### Replay Session

One viewing of a flight's stored downlink frames. The system MUST close each
session after two hours.

## Requirements

### Telemetry Replay (TLM)

- `TLM-1` The system MUST validate the replay request and log every
  validation failure.
- `TLM-3` The replay MUST be fast.
- `TLM-3` The system MUST colour each anomaly in the replay dialogue.
- `TLM-4` The system MUST rewrite stored downlink frames to the current frame
  format before every replay.
