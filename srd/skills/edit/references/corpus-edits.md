# Corpus-grounded edits

When and how `edit` consults the documentation corpus, and what a confirmation
attests. Read before the first proposal that changes a requirement's meaning
or removes a requirement; a run that does neither needs none of it.

The corpus itself — backends, trust, and where a lookup's outcome goes — is in
[../../create/references/doc-corpus.md](../../create/references/doc-corpus.md).

## The lookup lands before the proposal

When a new or changed requirement changes what the SRD means — one the user
dictates mid-walk included — `search` the corpus and grep the knowledge base,
`<kb>/_inbox.md` included, for the fact it changes **before the proposal is
put** (loop step 1); a KB section stating the old fact is named in the proposal,
never found after the `Y`. State what the lookup found in the proposal, each
result it rests on as a source line ([Citing a
source](../../create/references/doc-corpus.md#citing-a-source)) — a lookup that
only confirms the text included; one that found nothing says so and gives none,
nor does its log entry: attestation works on the first reading, so the fact and
where it came from have to be in front of the user when they press the key.
Step 3 re-validates only what the edit touched and never returns to the corpus
for a claim the proposal already carried.

## Set versus reported

A figure the SRD *sets* needs no lookup; one it *reports* does. Only the author
knows which, and the loop's one question is the confirmation — so read it from
the requirement's voice (a rule imposed on the system sets its figure; a
sentence describing what the platform already does reports it), say which
reading you took in the proposal's rationale, and let `E` or a correction
overturn it. Never a second question.

## What a confirmation attests

A proposal resting on a platform fact states it, so `Y`/`YN`/`E` attests the
fact and `S` withholds it — an attested fact goes to `srd:kb` at once, which
writes it to the inbox; `srd:kb` may only sharpen a fact the edit already
put in play. A deferred platform question goes to `srd:report-doc-gap` as a
gap with `answer: deferred`, not to `edit`'s own `## Open questions`, which
tracks questions about this SRD and empties with the session. A user who does
not know a fact the proposal rests on answers it as `S`: nothing applies,
nothing goes to `srd:kb`, and
[Who would know](../../create/references/doc-corpus.md#who-would-know) sets
the gap's `answer`.

## A KB section contradicts the change

This section covers a new or changed requirement — a changed value replaces the
old fact, so `srd:kb` rewrites the section and no gap is filed. Only a removal
with no replacing fact is [Cutting a requirement](#cutting-a-requirement). A
lookup hit on a KB section that states otherwise is a finding, never a
tie-break: the proposal names the section and both claims. Never align the SRD
to the KB, or the KB to the SRD, by `rank`: an SRD has none. `Y`/`YN`/`E`
attests the SRD's fact and `srd:kb` rewrites the section at once; `E` aligning
the SRD to the section settles it the other way.

## Cutting a requirement

A removal (deletion, or the STA-8 strike) in any mode that reaches it gets a
lookup too, before the proposal: `search` the corpus for the facts the
requirement asserted, resolve each hit under the `kb` prefix to its file, and
keep each section whose attestation line names this SRD and states a fact the
requirement introduced. The proposal names those sections. Its `Y`/`YN`/`E`
confirms the cut and each gap with it: hand each section to
`srd:report-doc-gap` at once as a confirmed `wrong` gap — `doc_id` and
`heading_path` the section, `srd_ref` this SRD, `detail` naming the cut
requirement (`specs/gw.md GR-6, cut <date>`) and every other SRD the
attestation line names. Never edit the KB section: the gap carries it to
`srd:backlog`. A section whose fact a surviving requirement of this SRD still
asserts gets no gap: the cut did not make it wrong. The manifest lists each
gap id beside its cut.
