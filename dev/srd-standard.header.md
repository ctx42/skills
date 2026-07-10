# SRD Standard

<!-- Hand-maintained frame; the srd-sync skill copies this file into
     srd-standard.md and prepends the generated-file banner. This note is
     dropped at assembly and never appears in the artifact. -->

The rule set every SRD must satisfy. An SRD states what a system or feature
must do — clearly enough that an engineer can build it and a reviewer can
verify it. `create` authors against these rules, `edit` edits against them,
and `review` reviews against them; each rule is a checkable statement and
keeps its identifier so a finding can cite it, and each skill applies its own
action policy on a finding. Check in document-section order (metadata,
Introduction, Glossary, Scope, Requirements); for cross-cutting checks run the
consistency pass in [authoring-guide.md](authoring-guide.md), which also holds
the house additions (US English, sub-numbering, one term per concept).

## Contents

- Glossary
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
