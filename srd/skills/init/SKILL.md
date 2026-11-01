---
name: init
description: >
  Adds the keys only the srd skills read (kb, srd-standard, srd-work) to the
  project-config.md the docket plugin wrote at the vault root: proposes their
  values, writes them after one confirmation, creates their folders. Use to
  set up or initialize a vault for SRD work. Not for checking a setup
  (srd:check) or writing an SRD (srd:create).
argument-hint: ""
license: MIT
---

# init

## Usage

```
/srd:init               add the srd skills' keys to the vault root's project-config.md
```

Run it from the vault root. It finds a value for each of `kb`, `srd-standard`,
and `srd-work` the config lacks, proposes them all at once, and writes them
after one confirmation. A `key=value` that names no control here, or a word
left over once the modes, the target, and any text the skill takes are read:
say it was not recognized, name the ones that exist, and run with the defaults
as if it were absent — unless dropping it would widen what the run changes;
then ask. A target that resolves to nothing: say so and ask — never guess what
to work on.

## Boundaries

- The docket plugin owns `project-config.md`: it creates the file, writes
  every other key, and runs the doc server. This skill writes only the lines
  of `kb`, `srd-standard`, and `srd-work`, its own body section
  ([Key reference](#key-reference)), this skill's lesson file
  ([Self-learning](#self-learning)), and one empty `.gitkeep` in the `kb` or
  `srd-work` folder when it does not exist; `srd-work: none` names no folder.
  Read anything under the vault root; edit nothing else.
- Never create the file, and never change or remove another key, its value,
  or any other line: added keys go at the end of the front matter.
- Skip the gate: this skill writes keys the gate reads. Call no server tool,
  start no server, and never touch `.mcp.json`.

## Sources of truth

- [../create/references/project-config.md](../create/references/project-config.md)
  (eager) — what each key holds, who writes it, and "5. Working files".

## Run

1. No `project-config.md` in the working directory: say the docket plugin
   writes it — turn on its MCP server in this vault, then re-run — and stop.
2. Read its front matter. `kb`, `srd-standard`, and `srd-work` all set (for
   `srd-work`, `none` counts) and the body holding the key reference: go to
   step 6. Otherwise find a value for each missing key
   ([Finding values](#finding-values)).
3. Propose once: the three keys as they will be, in a fenced `yaml` block —
   set ones as found, added ones with their values — then one line per added
   key: `found <where>`, `new folder`, or `not found` with the candidates seen,
   and whether the key reference will be appended. Ask one question: write it
   as shown, or which values to change.
4. `srd-standard` still `not found` blocks the write. After the user answers
   step 3, even with a yes, ask for it, then write at once with the answer in
   place, and do not show the proposal again: the answer is the confirmation.
5. On yes, or after the step-4 answer, with the user's changes: write the
   added keys, then the `.gitkeep` files, then the key reference.
6. Check what the gate needs from the plugin's keys, reading the front matter
   and the disk: `kb` among `sources`; a `srd-work` folder no source and inside
   none; `mcp-server`, `sources`, `initiatives`, `glossary`, `gaps`, and
   `precedence` set. Each one missing is a line of the report naming its fix:
   set it in the docket plugin's settings. Never write one of them.

## Finding values

Paths are relative to the vault root; find them with Glob and Grep. Two or
more candidates for one key: `not found`, naming them.

| Key            | Proposed value                                                                                                             |
|----------------|----------------------------------------------------------------------------------------------------------------------------|
| `kb`           | the top-level `kb` folder, else `kb` (new folder)                                                                          |
| `srd-standard` | the path of the document whose title names guidelines or a standard for software requirements documents                    |
| `srd-work`     | `srd-work` (new folder), no source and inside none; its proposal line adds: answer `none` to keep working files beside each SRD |

## Key reference

Append [assets/keys.md](assets/keys.md) verbatim, never reworded, to the end of
the body after one blank line, when the body has no `## SRD skill keys`
heading. With that heading present, replace that section — the heading to the
next `## ` heading or the end — with the asset when they differ. Never touch
any other part of the body.

## Report

One line: the keys added, whether the key reference was appended or updated,
the folders created. Then each line of step 6, numbered, or `Ready for SRD
work.` Then: run `/srd:check` for the full check.

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
