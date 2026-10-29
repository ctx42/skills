---
type: agent
---
Answer each id or path with its document below, verbatim.

For `initiatives/crew-seats/srd.md`:

````markdown
# Crew seats

| Field      | Value                                                |
|------------|------------------------------------------------------|
| Summary    | Let a customer book a crew seat on an Ember mission. |
| Maintainer | Dana K                                               |
| Reviewers  | John K                                               |
| Tracking   | [SF-131](https://tracker.example.com/browse/SF-131)  |
| Lifecycle  | WITHDRAWN                                            |
| Mockups    | none                                                 |

## Introduction

Purpose: let a customer book a crew seat on an Ember mission.

This document covers only that change; the Boundaries section lists what it
leaves out.

## Conventions

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to
be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they
appear in all capitals.

## Boundaries

### Included

- Booking a crew seat on an Ember mission.

### Excluded

- Changes to launch slot pricing.

## Requirements

- `CS-1` The Mission Portal MUST let a customer book a crew seat on an Ember mission.
````

For `initiatives/payload-booking/srd.md`:

````markdown
# Payload booking

| Field      | Value                                                 |
|------------|-------------------------------------------------------|
| Summary    | Let a customer book one payload onto one launch slot. |
| Maintainer | Dana K                                                |
| Reviewers  | John K                                                |
| Tracking   | [SF-112](https://tracker.example.com/browse/SF-112)   |
| Lifecycle  | APPROVED                                              |
| Mockups    | none                                                  |

## Introduction

Purpose: let a customer book one payload onto one launch slot.

This document covers only that change; the Boundaries section lists what it
leaves out.

## Conventions

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to
be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they
appear in all capitals.

## Boundaries

### Included

- Booking a payload onto a launch slot and showing the booked mission.

### Excluded

- Changes to launch slot pricing.

## Requirements

- `PB-1` The Mission Portal MUST show each booked Customer Mission with its launch slot and a countdown.
````

For `kb/mission-portal.md`:

````markdown
---
title: Mission Portal
attested: 2026-09-02
srd_ref: crew-seats, payload-booking
last_verified: 2026-09-20
---

# Mission Portal

## Crew seat booking

> Not in the platform docs. Attested crew-seats interview 2026-09-02.

A customer books a crew seat on an Ember mission from the Mission Portal. A
seat booking holds until its build order freezes.

## Mission visibility

> Not in the platform docs. Attested crew-seats interview 2026-09-02; payload-booking
> interview 2026-09-20.

A Customer Mission is visible on the Mission Portal only to the accounts of
the customer who booked it.

## Crew seat limit

> Not in the platform docs. Attested crew-seats interview 2026-09-02.

An Ember mission carries at most 4 crew seats.

## Launch countdown

> Not in the platform docs. Attested payload-booking interview 2026-09-20.

The Mission Dashboard counts down to the launch slot in the customer's time
zone.

## Provenance

Where each section of this page comes from.

| Section            | Source                                 |
|--------------------|----------------------------------------|
| Crew seat booking  | crew-seats interview                   |
| Mission visibility | crew-seats, payload-booking interviews |
| Crew seat limit    | crew-seats interview                   |
| Launch countdown   | payload-booking interview              |
````

For `kb/_inbox.md`:

````markdown
---
title: Knowledge base inbox
last_verified: 2026-09-01
---

# Knowledge base inbox

No facts are waiting to be filed.
````

For `docs/srd-standard.md`:

````markdown
{{file:fixtures/srd-standard.md}}
````

For any other id answer {"error":"document not found"}.
