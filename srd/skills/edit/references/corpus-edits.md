# Corpus-grounded edits

When and how `edit` consults the documentation corpus, and what a confirmation
attests. Read before the first proposal that asserts anything about existing
system behavior; a run that asserts none needs none of it.

The corpus itself — backends, trust, and where a lookup's outcome goes — is in
[../../create/references/doc-corpus.md](../../create/references/doc-corpus.md).

## The lookup lands before the proposal

When a new or changed requirement asserts something about existing system
behavior, `search` the corpus **before the proposal is put** (loop step 1) and
state what it found in the proposal: attestation works on the first reading, so
the fact the user's key attests has to be in front of them when they press it.
Step 3 re-validates only what the edit touched and never returns to the corpus
for a claim the proposal already carried. Absent a corpus, edit offline.

## Set versus reported

A figure the SRD *sets* needs no lookup; one it *reports* does. Only the author
knows which, and the loop's one question is the confirmation — so read it from
the requirement's voice (a rule imposed on the system sets its figure; a
sentence describing what the platform already does reports it), say which
reading you took in the proposal's rationale, and let `E` or a correction
overturn it. Never a second question.

## What a confirmation attests

A proposal resting on a platform fact states it, so `Y`/`YN`/`E` attests the
fact and `S` withholds it; `srd:kb` may only sharpen a fact the edit already
put in play. A deferred question goes to the knowledge base's open-questions
list through `srd:kb`, not to `edit`'s own `## Open questions`, which tracks
questions about this SRD and empties with the session.
