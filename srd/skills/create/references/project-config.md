# Project config and the gate

Every srd skill runs this gate first, in every mode, before reading the SRD,
probing anything, or asking the user anything. A delegate invoked by an srd
skill that passed the gate this session reuses that result.

## 1. Find the config

1. Walk up from the SRD's directory (the working directory when no SRD is
   named) to the first directory holding `project-config.md`; that directory
   is the **project root**.
2. Read the file's YAML front matter; keys are flat. Ignore keys not listed
   below — they belong to the server.

| Key            | Holds                                                           |
|----------------|-----------------------------------------------------------------|
| `mcp-server`   | server name; its tools are `mcp__<mcp-server>__<tool>`          |
| `kb`           | knowledge-base folder; confirmed facts land in `<kb>/_inbox.md` |
| `initiatives`  | SRD folder, one folder per SRD                                  |
| `srd-standard` | document id of the SRD standard, read with `get_doc`            |
| `glossary`     | the Company Glossary location (a file or a folder)              |

Every srd skill needs all five: each one delegates to the others. Every path is
relative to the project root; an absolute path is invalid.

## 2. Check the server

3. Confirm tools named `mcp__<mcp-server>__*` are in this session.
4. Call `mcp__<mcp-server>__search` with a one-word query and `k` 1. Any
   answer passes, hits or none; an error or no answer fails.

## 3. Stop on any failure

Stop before any other work and say exactly which check failed, in one line:

- `project-config.md` not found in `<start dir>` or any parent.
- `project-config.md` has no `<key>`.
- `<key>` is absolute (`<value>`); paths are relative to the project root.
- No `mcp__<mcp-server>__*` tools in this session.
- `mcp__<mcp-server>__search` failed: `<error>`.

For the last two add: start the `<mcp-server>` server, run `/mcp` to connect,
then re-run. Never fall back to a REST call, a local checkout, or offline work.

## 4. Use what it names

- A document id is its path from the project root: `<kb>/_inbox.md` is both the
  file and its id, because each server source is a top-level folder named as
  its id prefix.
- The SRD standard is `get_doc` on the `srd-standard` id, fetched once per
  session before the first rule check; it is the only source of the `STR`,
  `STA`, `LANG`, `REQ`, `GLO`, `SCO` rules and the Quality Bar. Never use a
  stored or remembered copy. A not-found id stops the run like a gate failure:
  `srd-standard` names no document (`<value>`).
- The standard's "Company Glossary" is the `glossary` location; its terms come
  from the server ([srd-procedures.md](srd-procedures.md)).
- An SRD's `srd_ref` is its path from the project root.
- Project data lives in the project or on the server — `<kb>/`, server-side
  gaps — never in per-machine state. Only skill lessons live per machine.
