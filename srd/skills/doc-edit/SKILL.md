---
name: doc-edit
description: >
  Edits one documentation-corpus page in place (a glossary page, a synced
  documentation page, a knowledge-base page), one confirmed change at a time,
  checking each fact against the corpus, filing what nobody can confirm as a
  doc gap, and filling the gaps the edit answers. Use when asked to update,
  correct, or extend a glossary entry or a documentation page with platform
  facts. Not for SRDs (srd:edit) or for working the gap backlog (srd:backlog).
argument-hint: "<document path> [<what to change>]"
license: MIT
---

# doc-edit

## Usage

```
/doc-edit <doc> <change>  make the asked change, one confirmed edit at a time
/doc-edit <doc>           ask what to change, then as above
```

Edits one corpus document and keeps the gap store in step with it: a fact
nobody can confirm becomes a gap; a gap the edit answers is filled from the
section that now states it.

## Boundaries

- Edit only the named document; read any other, edit none.
- A document under `initiatives` is an SRD: invoke `srd:edit` with its path and
  the request, then stop. Its companion files belong to their skills.
- A page under `kb`: propose here, write nothing; `srd:kb` writes it (see
  [Document kinds](#document-kinds)).
- Never add, remove, or change front matter or a marker; both stay as found.
- Never capture or file a gap yourself: `srd:report-doc-gap` does. Fill only per
  [Resolving a gap](#resolving-a-gap); never wontfix or reopen one (that is
  `srd:backlog`), and never touch the `gaps` folder.
- Never propose publishing, pushing, or syncing.

## Sources of truth

- [../create/references/project-config.md](../create/references/project-config.md)
  (eager) — the gate, identity, and the front-matter rule.
- [../create/references/doc-corpus.md](../create/references/doc-corpus.md)
  (eager) — the tools, section references, trust by `rank`, gap statuses.

## Session start

1. Run the gate, walking up from the document's directory.
2. Under `initiatives`: hand off per Boundaries. Else `list_docs`: the
   document's entry gives its identity (`id`) and kind
   ([Document kinds](#document-kinds)). No entry: say it is not in the corpus
   and stop.
3. Read the whole file.
4. `list_gaps` `status: open`: keep the gaps whose `doc_id` is the identity —
   the open gaps on this document. `list_gaps` `status: draft`, `srd_ref` the
   document's path: any record, invoke `srd:report-doc-gap` with the path.
5. One setup line: the kind, and the open gaps on it by id. Then the first
   proposal; with no change named, ask what to change.

## Edit loop

Per change:

1. Look up before proposing: `search` each platform fact the change writes
   and each the section it touches states; `get_doc` a hit when its context
   matters.
2. Propose exactly one change: the heading it sits under, before and after
   text, a one-line rationale, what the lookup found (`<identity>#<slug>`,
   `rank`), and any gap it fills or leaves.
3. Close with `Y` (apply) / `S` (skip) / `E` (apply the user's text), plus `K`
   (the KB instead) when the change writes a fact the user supplied. Apply
   only on explicit approval; one question per turn; never batch unrelated
   changes.
4. A change that renames or removes a heading breaks every
   `<identity>#<slug>` citing it: say so in its proposal.
5. Then the next change the request needs; none left, session end.

## Facts

Each lookup ends in one of:

- The corpus states it: cite it in the proposal.
- Two sources disagree: the lower `rank` states the platform; the other is a
  `wrong` gap unless this change corrects it. Equal or no ranks: put both to
  the user. Never settle by folder name.
- The corpus is silent: the proposal says so. The user states or confirms it
  (in the request, or answering the proposal): it is attested; write it. Write
  no fact neither the corpus nor the user gives.
- The user does not confirm it, defers it, or nobody can answer: leave the
  text unchanged and hand the gap to `srd:report-doc-gap`
  as a capture with the document's path, then go on. It dedups by `list_gaps`
  `query` and takes a hit on a repeat. Pass `doc_id` the identity and
  `heading_path` the section when the gap is about this document; `answer:
  deferred` when the user defers it, `unknown` when nobody can answer.

## Resolving a gap

A gap resolves when the user supplies or confirms its fact: an open gap on
this document, or one the capture dedup matched. The proposal states the fact
and names the gap; the key picks its home:

- `Y` — this document: apply, then `fill_gap` with `filled_by`
  `<identity>#<heading-slug>` of the section that now states it; the server
  reads the file, so it resolves at once. The identity is the `id`, never the
  `path` (`1882030917#recording-overlap`). The whole fact: `complete: true`;
  part: `complete: false`, `remaining` what is still missing.
- `K` — the KB: hand the fact to `srd:kb` with the gap id; this document
  stays. Fill from the KB section (`kb/<page>.md#<slug>`) only once it sits on
  a topic page. In `_inbox.md`: no fill; the gap stays open; offer `/kb file`.
- Never fill from a URL, `_inbox.md`, a document under `initiatives`, or an
  unconfirmed fact.
- A fact this document now states goes nowhere else: the KB holds only what
  the docs do not.

## Document kinds

| Document                  | How it is edited                                         |
|---------------------------|----------------------------------------------------------|
| under `initiatives`       | hand off to `srd:edit`                                   |
| under `kb`                | `srd:kb` writes each confirmed change; `Y` and `K` agree |
| synced (`id` ≠ `path`)    | in place, on the user's ask                              |
| any other corpus document | in place                                                 |

A page under `kb` changes only as `srd:kb` allows: a new fact goes to its
inbox, a corrected fact rewrites its section in place, a move or rename is
`/kb restructure`. Any other change to it is out of reach: say so.

A synced page: say once that the edit reaches its source only when the user
pushes it upstream, and that a pull before then overwrites it; its fills then
go stale for `srd:backlog`.

## Session end

1. Invoke `srd:report-doc-gap` with the document's path to offer the drafts
   this session captured, only when there are any.
2. Close with the manifest: changes applied, by heading; gaps filled, partly
   filled, and captured, by id; the synced-page line when it applies; what was
   skipped. Read every count off the finished file.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/srd/doc-edit.md`,
the sibling winning a conflict — a read-only install writes the second, and
what it learned there stays true once the checkout is writable again. Most
runs have none; absence is the normal case and needs no comment. On a
correction or self-caught mistake, append a one-line rule to the sibling when
this directory is writable, else to the fallback, creating it, and report
where.
