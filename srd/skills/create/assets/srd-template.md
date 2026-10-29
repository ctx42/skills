# SRD skeleton

<!-- How to build a new SRD's skeleton. The SRD standard, fetched through the
     server (project-config.md), sets the metadata fields, the sections,
     their names and order, where the keyword notice goes, and the
     requirement-identifier format; this file fixes none of them. Build the
     skeleton from the standard, then fill it. -->

## Build it from the standard

1. Title: `# <SRD title>`.
2. Metadata: every field the standard requires, in the layout and order it
   sets (a table when it says so). The summary field takes the interview's
   purpose; the status field the standard's initial status; each field that
   names people or links outside the SRD a marked `<TODO: …>` placeholder; the
   design-link field the standard's no-UI value when the UI does not change.
3. Sections: every section the standard requires, under the names it gives,
   in the order it sets. A section the standard makes conditional (a local
   terms section, for one) only when its condition holds.
4. Keyword notice: where the standard places it, as its own section when the
   standard gives it one. Its text is the one the standard fixes for an SRD;
   when it fixes none, the default below.
5. Scope: the in-scope and out-of-scope lists the standard requires. The
   in-scope list MAY hold a single `--- TODO ---` marker line until the
   requirements settle (authoring guide).
6. Requirements: one entry per requirement, in the identifier format the
   standard sets, grouped under group headings fenced by `---` dividers
   (authoring guide).
7. `## TODO`: optional, last, only where the standard lets extra sections go;
   a numbered list of open authoring issues, no normative keywords. Empty or
   removed before the SRD reaches the standard's approval status.

Placeholders in angle brackets (`<field>`, `<TODO: …>`) mark what the
interview fills or a human supplies later.

## Default keyword notice

```markdown
> [!INFO]
> The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
> "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
> document are to be interpreted as described in
> [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
> [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
> appear in all capitals, as shown here.
```
