---
name: init
description: >
  Sets up a folder for the srd skills — proposes the project-config.md keys it
  lacks, writes them after one confirmation, creates their folders — or, in
  check mode, reports how the project is configured and what is wrong. Use to
  set up, initialize, check, or validate a vault or folder for SRD work. Not
  for writing an SRD (srd:create).
argument-hint: "[check] [<dir>]"
license: MIT
---

# init

## Usage

```
/srd:init               set up the working directory
/srd:init <dir>         set up <dir>
/srd:init check [<dir>] report how it is configured and what is wrong; write nothing
```

Setup finds a value for every srd key the folder's `project-config.md` lacks,
proposes them all at once, and writes them after one confirmation. `check` may
stand anywhere; the other token is `<dir>`, one per run. A `key=value` that
names no control here, or a word left over once the modes, the target, and any
text the skill takes are read: say it was not recognized, name the ones that
exist, and run with the defaults as if it were absent — unless dropping it would
widen what the run changes; then ask. A target that resolves to nothing: say so
and ask — never guess what to work on.

## Boundaries

- Write only `<dir>/project-config.md`, this skill's lesson file
  ([Self-learning](#self-learning)), and one empty `.gitkeep` in each folder
  `kb`, `gaps`, or `srd-work` names — set before or added now — that does
  not exist; `srd-work: none` names no folder. Read anything under `<dir>`;
  edit nothing else.
- Never change or remove a key the file sets, its value, or any other line:
  added keys go at the end of the front matter, and the body stays as found
  but for the [Key reference](#key-reference) appended at its end.
- The server keys belong to the server's host: the docket plugin writes a
  starter config (`mcp-server`, `sources`, `watch`) when its doc server is
  switched on in a folder without one, and the port on first start; this
  skill adds the rest. Keep `mcp-server`, `mcp-port`, `watch`, and
  `watch-debounce` as found, and write them only into a new file. `sources`
  changes only by adding `kb` as its last item, in place and in the list's own
  style.
- Skip the gate: this skill writes the file the gate reads, and the server
  may not run yet. In setup, call no server tool, start no server, and never
  touch `.mcp.json`.
- `check` is read-only: it writes nothing and fixes nothing in the project
  (its lesson file aside), and calls only the server's read tools (`search`,
  `list_docs`, `get_doc`, `list_gaps`).

## Sources of truth

- [../create/references/project-config.md](../create/references/project-config.md)
  (eager) — what each key holds, and "5. Working files".

## Run

1. `<dir>` is the target, else the working directory. Not a folder: say so
   and ask. `check`: run [Check mode](#check-mode) instead.
2. Read `<dir>/project-config.md` when it exists. An existing file without
   `mcp-server` or `sources` is not set up: for each, the proposal opens with
   a note above the `yaml` block, never inside it, and the write never adds
   the key:
   - "`mcp-server` is not set: add it yourself (the docket plugin uses
     `docs`), then restart the doc server."
   - "`sources` is not set: add your doc folders and `kb` yourself, then
     restart the doc server."

   A new file gets the server keys instead ([Finding values](#finding-values)).
   Then check the srd keys (`kb`, `initiatives`, `srd-standard`, `glossary`,
   `gaps`, `precedence`, `srd-work`; for `srd-work`, `none` counts as set):
   - All set: the proposal holds only what is left — those notes, if any;
     `kb` added to `sources`, when `sources` is set and lacks it; the key
     reference, when the body lacks it; and one line per folder `kb`,
     `gaps`, or `srd-work` names that does not exist (`gap/` missing — will
     create `gap/.gitkeep`). Only notes left: give them and stop. Nothing
     left: say it is set up and stop, writing nothing.
   - Otherwise go on.
3. Find a value for each missing key ([Finding values](#finding-values)),
   and add `kb`, set before or added now, to a `sources` that lacks it, a new
   file's included.
4. Propose once: the whole front matter as it will be, in a fenced `yaml`
   block — kept lines as found, added keys after them — then one line per
   added key: `found <where>`, `new folder`, or `not found` with the
   candidates seen, and whether the key reference will be appended. Ask one
   question: write it as shown, or which values to change.
5. A required key (`kb`, `initiatives`, `srd-standard`, `glossary`) still
   `not found` blocks the write. After the user answers step 4, even with a
   yes, ask for each such value in turn, one question per message, until none
   is left. Then write at once with the answers in place, and do not show the
   proposal again: the answers are the confirmation, even though the front
   matter now differs from the one shown. An optional key not found is left
   out.
6. On yes, or after the last step-5 answer, with the user's changes: write
   the file, then the `.gitkeep` files. Report per [Report](#report).

## Finding values

Paths are relative to `<dir>`; find them with Glob and Grep. A required key
no search finds goes into the proposal as `not found`; ask for it only after
the proposal (step 5).
Two or more candidates for one key: `not found`, naming them.

| Key            | Proposed value                                                                                                                            |
|----------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| `sources`      | new file only: each top-level folder holding Markdown, except dot-folders and the `gaps` and `srd-work` folders                           |
| `kb`           | the top-level `kb` folder, else `kb` (new folder)                                                                                         |
| `initiatives`  | the folder inside a source named `srd` or `initiatives`, else the one whose subfolders each hold a `*-srd.md`                             |
| `srd-standard` | the path of the document whose title names guidelines or a standard for software requirements documents                                   |
| `glossary`     | the folder or Markdown file named `glossary` inside a source                                                                              |
| `gaps`         | always `gap`, whatever other folders exist; a new folder when missing                                                                     |
| `precedence`   | `kb`, then each other source's subfolders (or the source, having none) in name order, leaving out `initiatives` and any folder holding it |
| `srd-work`     | `srd-work` (new folder), outside every source; its proposal line adds: answer `none` to keep working files beside each SRD                |

A new file also gets `mcp-server: docs`, `mcp-port: 7777`, and
`watch: true`; a server host may move the port.

## Key reference

Copy [assets/keys.md](assets/keys.md) verbatim, never reworded, to the end of
the body after one blank line. A new file's body is `# Project configuration`
followed by it. Skip it when the body already has a `## Front matter keys`
heading or a table row naming `mcp-server`: the keys are documented there.

## Report

One line: the file, the keys added, whether the key reference was appended,
the folders created. Then the next step: start the server (the docket
plugin's MCP switch, or `docket mcp`) and connect it with `/mcp`.

## Check mode

Run every check below; never stop at the first problem.

1. Read `<dir>/project-config.md` and `<dir>/.mcp.json`. No config: say so,
   point to `/srd:init`, and stop.
2. Server: tools `mcp__<mcp-server>__*` in this session and `search`
   answering. Either missing: report it as a problem, and report the lines
   that need the server as `not checked`.
3. With the server, call `list_docs` once and read everything from it: the
   documents per source (a path's first folder), the trust order as the
   `rank`s show it, the SRD folders under `initiatives`, the documents under
   `glossary` and `kb`. Then `get_doc` the `srd-standard` identity, and
   `list_gaps` with `status: open`, then `draft`.
4. Check the file against the disk with Glob, and the server's answers
   against the file:

| Problem                                                                     | Fix                                                                                 |
|-----------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| a required srd key missing, or any path absolute                            | run `/srd:init`                                                                     |
| `mcp-server` missing                                                        | add `mcp-server: docs` (or the name `.mcp.json` registers), then restart the server |
| `.mcp.json` lacks the server, or names another port                         | restart the server (its host rewrites it), or fix the URL                           |
| a `sources` folder missing                                                  | create it, or remove it from `sources`                                              |
| `kb` not in `sources`                                                       | add it: the KB is not searchable                                                    |
| `srd-work` in `sources`                                                     | remove it: working files are indexed as documents                                   |
| `gaps` inside a source                                                      | move it out of every source                                                         |
| `get_doc` finds no `srd-standard`                                           | point it at the standard's id or path                                               |
| `initiatives` holds no SRD                                                  | point it at the SRD folder                                                          |
| a `precedence` folder missing, outside the sources, or inside `initiatives` | fix or remove the entry                                                             |
| no key reference in the body                                                | run `/srd:init` to append it                                                        |

Report an overview, one line per area, then the problems numbered with their
fixes, or `No problems.`:

```
Server     <name> on port <port>: connected | not connected
Indexes    <source> (<n> documents), …
Trust      1 <folder> · 2 <folder> · …; unlisted folders rank last
SRDs       <initiatives>: <n> SRDs
Standard   <srd-standard>: found | not found
Glossary   <glossary>: <n> documents
KB         <kb>: <n> pages
Gaps       <gaps>: <n> open, <n> drafts
Work files <srd-work>: outside the sources | indexed | none or not set (beside each SRD)
```

Read every count off the server's answers, never estimate one.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/srd/init.md` (pass `~` as is, the
file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable; this block never moves or merges lessons. A missing file needs no
comment. On a correction or self-caught mistake, append a one-line rule —
general, naming nothing from the project at hand (its files, tests, tickets) —
to the sibling when this directory is writable (creating it even when only the
fallback holds lessons so far; both stay read), else to the fallback, creating
it, and report where. A lesson write is not a project write: a read-only or
no-change run still makes it.
