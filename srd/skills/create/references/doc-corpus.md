# Documentation Corpus

How the SRD skills ground claims about the existing platform in its live
documentation, and where what a lookup teaches goes. Shared by `create`,
`review`, `edit`, `doc-edit`, and `system-check`: each skill says *when* it
consults the corpus, this file says *how*. The gate in [project-config.md](project-config.md)
guarantees the server answers before any skill starts. An assertion about
existing system behavior that no lookup confirms stays unconfirmed and is
flagged as such; silently accepting a platform claim is the one outcome this
file rules out.

## Contents

- Tools
- Identity
- Trust
- Citing a source
- Gaps
- Where a lookup's outcome goes

## Tools

All corpus and gap-store calls go to `mcp__<mcp-server>__<tool>`, with
`<mcp-server>` from `project-config.md`:

- Read: `search` (query, optional `k`), `get_doc` (identity or path),
  `list_docs` (no args), `glossary_terms` (optional substring filter).
- Gaps: `report_gap` (optional `draft: true`), `update_gap` (only the fields
  given change; `add_hit` counts a repeat encounter), `submit_gap`,
  `discard_gap`, `list_gaps` (filters `status`, `srd_ref`, `stale`, `ask`,
  `asked`; ranked `query`, each result scored), `fill_gap`, `reopen_gap`,
  `wontfix_gap`.
  `srd:report-doc-gap` and `srd:backlog` own which may be called and when;
  `srd:doc-edit` also fills the gaps its own edits resolve.

Default to `search` with `k` about 5; `get_doc` only when a hit needs its full
table or context; `list_docs` to orient. A call that errors is reported, never
retried or worked around. The read tools query the docs, never edit the SRD.

## Identity

Every `search`, `get_doc`, `list_docs`, and `glossary_terms` result carries
`id` (the identity: front-matter `id`, else the path) and `path` (where the
file is now). A synced page's `id` differs from its path (`1774485611` at
`docs/concepts/tags.md`); a local file's `id`, a KB page's included, is its
path.

- Every stored document reference is the identity: copy the result's `id` as
  is, never its `path`, a checkout path, or a URL. A section is
  `<identity>#<slug>`: the heading slug, the GitHub-style slug of the heading
  text (a repeated heading takes `-1`, `-2`, … in order).
- Document references: gap `doc_id` and `filled_by`, a KB inline-code
  citation (`` `1774485611#tag-names` ``), a `> Contradicts` line. An SRD
  reference is its folder name instead
  ([project-config.md](project-config.md#4-use-what-it-names)).
- A Markdown link stays a relative path built from `path`: it is navigation,
  not a reference.
- A citation is stale only when it matches no `list_docs` `id` or `path`; one
  written as a checkout path matches when its tail equals a `path`. Comparing
  raw strings condemns every live source on the page.

## Trust

`search` orders by term placement, never trust. With `precedence` configured,
each result carries `rank`: 1 is the most trusted, a higher number less;
results under `initiatives` (SRDs) carry none.

- Two corpus sources disagree: the lower `rank` states the platform; the
  other's statement is a `wrong` doc gap for `srd:report-doc-gap`. Name both
  and the ranks that settled it.
- Equal ranks, or no `rank` on either side: nothing settles it — surface both
  to the user as a finding.
- Never settle by folder name, source type, or a remembered order — only by
  `rank`.

The KB and the SRDs both describe the target system — what the platform is or
will be — and must never contradict. An SRD carries no `rank`, so no rank
settles an SRD claim a KB section contradicts: it is a finding; surface both
sides. Only the user's confirmation settles it, and a confirmed fact changes
the KB at once (`srd:kb`) — never when other SRDs agree, never at acceptance.

## Citing a source

Much of the corpus is stale or wrong, and only the user can judge a page, so
corpus content never reaches SRD or corpus-page text unseen. Every proposal,
interview question, restatement, or suggested fix whose text rests on a
corpus result names each result it rests on, one line per source:

`Source: <title> › <heading> (rank <n>, 1 = most trusted) — <source_url>`

- Rests on: the text adds what the result states, was reworded because of
  it, or keeps a claim the result only confirmed. Figures and rules (a
  value, a limit, a MUST) above all.
- `<heading>`: the result's `heading_path` joined with ` › `; a hit with none
  names the page alone. No `rank`: `unranked`. A KB section or an SRD (no
  `source_url`): `Source: <path> › <heading>`.
- Never a quote, a summary of the page, a caution line, or a rank total: the
  source line is the warning, and the `precedence` scale is not readable.
- A lookup that found nothing gives no line; the proposal says it found
  nothing.
- Ask before the content lands: the user's confirmation of the proposal is
  the ask, so the line sits in it. Nothing the user stated and no lookup
  touched carries one; errata (formatting, a GLO-4 link) add no content and
  carry none.

## Gaps

A **gap** is a fact SRD work needs that the corpus — pulled documentation or
the `kb` folder — does not supply reliably: missing, wrong, incomplete, or
ambiguous. Only a corpus section fills it: a KB topic page or a pulled doc
page, cited `<identity>#<slug>`; a URL or an unpulled draft never does. A gap
with `answer` set records a platform question: `deferred` (someone knows, not
asked yet) or `unknown` (nobody has pinned it down). It is captured, offered,
and filed like any other gap. `ask` lists the people who can answer it, as the
user typed them; `asked` is the date (`YYYY-MM-DD`) the questions went out,
set only by `srd:backlog`.

| Status    | Means                                              | Leaves by                          |
|-----------|----------------------------------------------------|------------------------------------|
| `draft`   | captured, unconfirmed                              | `submit_gap` → open; `discard_gap` |
| `open`    | confirmed, unfilled or partly filled (`filled_by`) | `fill_gap` → filled; `wontfix_gap` |
| `filled`  | the `filled_by` sections state the fact            | `reopen_gap` → open                |
| `wontfix` | the corpus will not carry it; `detail` says why    | —                                  |

## Where a lookup's outcome goes

A lookup that confirms the claim needs nothing more. The other outcomes each
have an owner; the calling skill only spots them and delegates:

- The corpus cannot confirm the claim (content missing, wrong, incomplete, or
  ambiguous): a documentation gap. Hand it to `srd:report-doc-gap`, which
  captures it as a server-side draft and owns the grill and the filing. A
  defect in the SRD itself is never a doc gap; it stays in the calling skill's
  own findings.
- The corpus is silent but the user confirms the fact: tribal knowledge. Hand
  it to `srd:kb` once confirmed; it writes it to `<kb>/_inbox.md` at once. A
  term the user defines because no glossary carries it is the same case. The
  failed lookup is a gap too: send it to `srd:report-doc-gap` as well, which
  records it until a KB topic page or pulled doc page states it.
- A platform question the user defers, or nobody can answer: a gap with
  `answer: deferred` or `answer: unknown`. Hand it to `srd:report-doc-gap`,
  whose dedup decides what a match gets (a repeat never files twice); never
  write it to the KB.
  A user who does not know the answer gets [Who would know](#who-would-know)
  first.
- A KB section contradicts the SRD: a finding (see [Trust](#trust)). The user
  either fixes the SRD or confirms its fact, which `srd:kb` writes over the
  section at once.
- A requirement cut from an SRD (or an SRD abandoned): each KB section whose
  attestation line names that SRD and states a fact the cut requirement
  introduced gets one `wrong` gap through `srd:report-doc-gap`, its `detail`
  naming the cut requirement and every other SRD attesting the section. The
  KB section stays until the gap is worked. `srd:backlog` sweeps abandoned
  (`REJECTED`) SRDs at every run; no other skill files their gaps.

**Draft check at start.** A calling skill with an SRD calls `list_gaps` with
`status: draft` and `srd_ref` the SRD reference, and invokes
`srd:report-doc-gap` only when that returns a record — an empty list is the
usual case and needs no skill loaded. The calling skill's report says, in one
clause, that the check ran and what it found. With no SRD path yet there is
nothing to check.

When the calling skill finishes, it invokes `srd:report-doc-gap` to offer the
drafts captured this session, only when there are any. `review` hands nothing
to `srd:kb`: a read-only review confirms no platform fact with the user.

The user must never experience a second track beside the skill's own work: no
knowledge-base phase, no separate questions, no "bank this?" prompt.
Confirmation of a platform fact rides on the calling skill's own confirmation
step, and `srd:kb` may ask only to deepen a subject that step already opened,
never to open a new one. An SRD reference is the SRD's folder name
([project-config.md](project-config.md#4-use-what-it-names)); never invent one.

### Who would know

The user says they do not know a platform answer: ask exactly one follow-up,
"Who would know?", then move on. It belongs to the same exchange, not a second
track.

- Names: `answer: deferred`, `ask` each person's name exactly as typed, the
  name alone (`piotr k`, not `piotr k from billing`) — no @, no completion,
  no correction.
- "Nobody", "not sure", or no name: `answer: unknown`, no `ask`.
- Names volunteered unprompted ("Piotr knows"): recorded the same way; skip
  the question.
- The user knows but defers ("not now"): `answer: deferred`, no `ask`, no
  question.

Hand the outcome to `srd:report-doc-gap`: in the capture when the gap is not
captured yet, else as an update to the draft already captured; its dedup
merges names into a matching gap's `ask`. Never ask it twice for one question
in a session.
