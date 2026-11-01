# Project config and the gate

Every srd skill runs this gate first, in every mode, before reading the SRD,
probing anything, or asking the user anything. A delegate invoked by an srd
skill that passed the gate this session reuses that result. `srd:init` and
`srd:check` alone skip it: one writes keys the gate reads, the other reports
every problem the gate would stop on.

The docket plugin owns `project-config.md` at the vault root, the doc server
it runs, and `.mcp.json`; it refuses to start the server on a key the server
cannot use. `srd:init` adds the keys only the skills read. The gate trusts a
running server for the server's own rules and checks only what the server
cannot know.

## Contents

- 1. Find the config
- 2. Check the server
- 3. Stop on any failure
- 4. Use what it names
- 5. Working files

## 1. Find the config

1. Walk up from the SRD's directory (the working directory when no SRD is
   named) to the first directory holding `project-config.md`; that directory
   is the **project root**.
2. Read the file's YAML front matter; keys are flat. Ignore keys not listed
   below — they belong to the server.

| Key            | Holds                                                                     | Written by      |
|----------------|---------------------------------------------------------------------------|-----------------|
| `mcp-server`   | server name; its tools are `mcp__<mcp-server>__<tool>`                    | docket plugin   |
| `sources`      | top-level folders the server indexes                                      | docket plugin   |
| `initiatives`  | SRD folder, one folder per SRD; the server gives its documents no `rank`  | docket plugin   |
| `glossary`     | shared glossary location; glossary links must point under it              | docket plugin   |
| `gaps`         | server's gap folder, one `gap-NNNN-<slug>.md` per gap; reach it via tools | docket plugin   |
| `precedence`   | server's trust order: folders, most trusted first; drives each `rank`     | docket plugin   |
| `kb`           | knowledge-base folder; confirmed facts land in `<kb>/_inbox.md`           | `srd:init`      |
| `srd-standard` | identity of the SRD standard, read with `get_doc`                         | `srd:init`      |
| `srd-work`     | folder for SRD working files, or `none` (see "5. Working files")          | `srd:init`      |

SRD work needs every key in the table set: each skill delegates to the
others, and the gap tools, the glossary tool, and `rank` exist only with
theirs. `kb` must also be one of the `sources`, or its facts cannot be
searched; a `srd-work` folder must be no source and lie inside none (the
folder `wiki/notes` lies inside the source `wiki`), or working files are
indexed as documents. Every path is relative to the project root; an
absolute `srd-work`, or one leading out of it (`../`), stops the gate like any
other path key; the gate checks only `srd-work`'s, since the server refuses
such a value in every key it reads and does not start. Never read the gap folder or
the `precedence` list directly — use the gap tools and the `rank` on results.

## 2. Check the server

3. Confirm tools named `mcp__<mcp-server>__*` are in this session. Make no
   MCP call for the gate: a running server has already checked its own keys.

## 3. Stop on any failure

Stop before any other work and say exactly which check failed, in one line:

- `project-config.md` not found in `<start dir>` or any parent.
- `project-config.md` has no `<key>`.
- `<kb>` is not in `sources`.
- `srd-work` `<value>` lies inside source `<source>`.
- `srd-work` is absolute or leaves the project root (`<value>`).
- No `mcp__<mcp-server>__*` tools in this session.

Then add the fix. A missing file: turn on the docket plugin's MCP server in
the vault (it writes the file), then run `/srd:init`. A missing `kb`,
`srd-standard`, or `srd-work`, or a bad `srd-work`: run `/srd:init`. A
missing `mcp-server`, `sources`, `initiatives`, `glossary`, `gaps`, or
`precedence`, or `kb` not in `sources`: set it in the docket plugin's
settings. No tools: turn on the docket plugin's MCP server, run `/mcp` to
connect, then re-run. `/srd:check` reports every problem at once. Never fall
back to a REST call, a local checkout, or offline work.

## 4. Use what it names

- A document's **identity** is its front-matter `id`, else its path from the
  project root; every result carries both as `id` and `path`. A KB page has no
  `id`, so `<kb>/_inbox.md` is both its file and its identity. Store and pass
  identities per `doc-corpus.md` ("Identity").
- Read only the front-matter keys `id`, `title`, `url`, and `aliases` of a
  corpus document. Never add, remove, or change a front-matter key or marker
  no srd skill defines, in any file — a key another tool owns stays as found.
- The SRD standard is `get_doc` on the `srd-standard` identity, fetched once
  per session before the first rule check; it is the only source of SRD
  rules — metadata fields, status values, sections and their order, notice,
  identifier format, wording and term rules, approval checks — and a finding
  cites a rule by the identifier the standard writes. Never use a stored or
  remembered copy, and never apply a rule it does not state. A not-found
  identity stops the run like a gate failure: `srd-standard` names no
  document (`<value>`).
- The shared glossary the standard refers to, under whatever name it gives
  it, is the `glossary` location; its terms come from the server
  (`srd-procedures.md`).
- An SRD reference (gap `srd_ref`, KB `srd_ref`, attestation lines) is the
  SRD's folder name under `initiatives` (`slot-swap`); an SRD outside
  `initiatives` uses its path from the project root. Never a document
  identity, never an invented id.
- Project data lives in the project or on the server — `<kb>/`, server-side
  gaps — never in per-machine state. Only skill lessons live per machine.

## 5. Working files

`<srd>.<kind>.md` names an SRD's working file of one kind: `review`,
`decisions`, or `questions`. Every skill reads and writes a working file at
this path, and only there:

- With `srd-work` naming a folder, for an SRD under `initiatives`:
  `<srd-work>/<srd-folder>/<name>.<kind>.md`. `<srd-folder>` is the SRD's
  folder under `initiatives`; `<name>` is the SRD's whole file name without
  `.md`, never the folder name: `initiatives/login/login-srd.md` gives
  `<srd-work>/login/login-srd.review.md`. Create the folder with the first
  file written there.
- Otherwise, beside the SRD: its path with `.md` replaced. `specs/login.md`
  gives `specs/login.review.md`, never `specs/login.md.review.md`. This covers
  `srd-work: none` and an SRD outside `initiatives`.

Never look for a working file at the other place, and never move one.
