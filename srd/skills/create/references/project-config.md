# Project config and the gate

Every srd skill runs this gate first, in every mode, before reading the SRD,
probing anything, or asking the user anything. A delegate invoked by an srd
skill that passed the gate this session reuses that result. `srd:init` alone
skips it: it writes the file the gate reads.

## 1. Find the config

1. Walk up from the SRD's directory (the working directory when no SRD is
   named) to the first directory holding `project-config.md`; that directory
   is the **project root**.
2. Read the file's YAML front matter; keys are flat. Ignore keys not listed
   below — they belong to the server.

| Key            | Holds                                                                      |
|----------------|----------------------------------------------------------------------------|
| `mcp-server`   | server name; its tools are `mcp__<mcp-server>__<tool>`                     |
| `kb`           | knowledge-base folder; confirmed facts land in `<kb>/_inbox.md`            |
| `initiatives`  | SRD folder, one folder per SRD; the server gives its documents no `rank`   |
| `srd-standard` | identity of the SRD standard, read with `get_doc`                          |
| `glossary`     | shared glossary location; glossary links must point under it               |
| `gaps`         | server's gap folder, one `gap-NNNN-<slug>.md` per gap; reach it via tools  |
| `precedence`   | server's trust order: folders, most trusted first; drives each `rank`      |
| `srd-work`     | folder for SRD working files (see "5. Working files")                      |

Every srd skill needs the first five: each one delegates to the others. Every
path is relative to the project root; an absolute path is invalid. `gaps` and
`precedence` are optional and server-validated: never read the gap folder or
the `precedence` list directly — use the gap tools and the `rank` on results.
`srd-work` is optional; the skills read it themselves.

## 2. Check the server

3. Confirm tools named `mcp__<mcp-server>__*` are in this session.
4. Call `mcp__<mcp-server>__search` with a one-word query and `k` 1. Any
   answer passes, hits or none; an error or no answer fails.

## 3. Stop on any failure

Stop before any other work and say exactly which check failed, in one line:

- `project-config.md` not found in `<start dir>` or any parent.
- `project-config.md` has no `<key>` (one of the first five; an optional key
  may be absent).
- `<key>` is absolute (`<value>`); paths are relative to the project root.
- No `mcp__<mcp-server>__*` tools in this session.
- `mcp__<mcp-server>__search` failed: `<error>`.

For the first two add: run `/srd:init` in the project folder. For the last two
add: start the `<mcp-server>` server, run `/mcp` to connect, then re-run.
Never fall back to a REST call, a local checkout, or offline work.

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
  SRD's folder name under `initiatives` (`export-rate-limit`); an SRD outside
  `initiatives` uses its path from the project root. Never a document
  identity, never an invented id.
- Project data lives in the project or on the server — `<kb>/`, server-side
  gaps — never in per-machine state. Only skill lessons live per machine.

## 5. Working files

`<srd>.<kind>.md` names an SRD's working file of one kind: `review`,
`decisions`, `questions`, `retro`, or `notes`. Every skill reads and writes a
working file at this path, and only there:

- With `srd-work` set, for an SRD under `initiatives`:
  `<srd-work>/<srd-folder>/<name>.<kind>.md`. `<srd-folder>` is the SRD's
  folder under `initiatives`; `<name>` is the SRD's whole file name without
  `.md`, never the folder name: `initiatives/login/login-srd.md` gives
  `<srd-work>/login/login-srd.review.md`.
  Create the folder with the first file written there.
- Otherwise, beside the SRD: its path with `.md` replaced. `specs/login.md`
  gives `specs/login.review.md`, never `specs/login.md.review.md`.

Never look for a working file at the other place, and never move one.
