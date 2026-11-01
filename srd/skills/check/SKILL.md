---
name: check
description: >
  Checks, read-only, whether a vault is ready for the srd skills: every key
  the gate needs in project-config.md, the docket doc server's connection, and
  what the server indexes — the SRDs, the standard, the glossary, the
  knowledge base, the gaps — and names the fix for each problem. Use to check,
  validate, or diagnose a vault's SRD setup. Not for setting one up
  (srd:init).
argument-hint: ""
license: MIT
---

# check

## Usage

```
/srd:check              report how the vault is set up for SRD work and what is wrong
```

Run it from the vault root. A `key=value` that names no control here, or a
word left over once the modes, the target, and any text the skill takes are
read: say it was not recognized, name the ones that exist, and run with the
defaults as if it were absent — unless dropping it would widen what the run
changes; then ask. A target that resolves to nothing: say so and ask — never
guess what to work on.

## Boundaries

- Read-only: write nothing and fix nothing in the project (this skill's
  lesson file aside), and call only the server's read tools (`list_docs`,
  `get_doc`, `list_gaps`).
- Skip the gate: report every problem it would stop on, all at once.
- The docket plugin owns `project-config.md`, the doc server, and
  `.mcp.json`, and refuses to start the server on a key the server cannot
  use; `srd:init` writes `kb`, `srd-standard`, and `srd-work`. Each fix names
  one of them.

## Sources of truth

- [../create/references/project-config.md](../create/references/project-config.md)
  (eager) — the keys, who writes each, and what the gate checks.

## Run

Run every check below; never stop at the first problem.

1. Read `project-config.md` in the working directory and `.mcp.json` beside
   it. No config: report it — the docket plugin writes it; turn on its MCP
   server in this vault — and stop.
2. From the front matter and the disk (Glob): every key of the gate's table
   set; `kb` among `sources`; `srd-work` relative, inside the project root,
   and, naming a folder, no source and inside none; the `kb` folder, and the
   `srd-work` one unless `none`, existing; the body holding the
   `## SRD skill keys` section.
3. Server: tools `mcp__<mcp-server>__*` in this session. Missing: report it as
   a problem, and report the lines that need the server as `not checked`.
4. With the server, call `list_docs` once and read everything from it: the
   documents per source (a path's first folder), the trust order as the
   `rank`s show it, the SRD folders under `initiatives`, the documents under
   `glossary` and `kb`. Then `get_doc` the `srd-standard` identity, and
   `list_gaps` with `status: open`, then `draft`.

| Problem                                                                   | Fix                                                                     |
|---------------------------------------------------------------------------|-------------------------------------------------------------------------|
| no `project-config.md`                                                    | turn on the docket plugin's MCP server in this vault (it writes the file) |
| `mcp-server`, `sources`, `initiatives`, `glossary`, `gaps`, or `precedence` missing | set it in the docket plugin's settings                        |
| `kb` not in `sources`                                                     | add it in the docket plugin's settings: the KB is not searchable        |
| `kb`, `srd-standard`, or `srd-work` missing, or a bad `srd-work`          | run `/srd:init`                                                         |
| the `kb` or `srd-work` folder missing                                     | run `/srd:init` (it creates the folder)                                 |
| no `## SRD skill keys` section in the body                                | run `/srd:init` to append it                                            |
| no `mcp__<mcp-server>__*` tools                                           | turn on the docket plugin's MCP server, then run `/mcp`                 |
| `.mcp.json` lacks the server, or names another port                       | restart the server in the docket plugin (it rewrites `.mcp.json`)       |
| `get_doc` finds no `srd-standard`                                         | run `/srd:init` and point it at the standard's id or path               |
| `initiatives` holds no SRD                                                | point it at the SRD folder in the docket plugin's settings              |

The server checks its own keys — paths, folders, the gap folder, the trust
order — and does not start on a bad one; a running server has passed them.

## Report

An overview, one line per area, then the problems numbered with their fixes,
or `No problems.`:

```
Server     <name> on port <port>: connected | not connected
Indexes    <source> (<n> documents), …
Trust      1 <folder> · 2 <folder> · …; unlisted folders rank last
SRDs       <initiatives>: <n> SRDs
Standard   <srd-standard>: found | not found
Glossary   <glossary>: <n> documents
KB         <kb>: <n> pages
Gaps       <gaps>: <n> open, <n> drafts
Work files <srd-work>: outside the sources | indexed | none (beside each SRD)
```

Read every count off the server's answers, never estimate one.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/srd/check.md` (pass `~` as is, the
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
