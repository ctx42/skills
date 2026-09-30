# Lessons

- One atomic change split across staged and unstaged files is one commit: stage the rest and commit it whole (amend when a partial commit already landed), never let the staging split decide the commit boundary.
- Re-read the index in the same command that commits (`git diff --cached --stat && git commit -F -`) and compare it with the diff the message was drafted from; a file staged in between rode into a commit whose message never named it.
- Before committing a chunk, compare `git diff --cached --name-only` against the expected file list in the same command and abort on mismatch; printing the stat is not a check, and files the user staged earlier ride along unnoticed.
- Derive every causal claim in the body from the diff; "a rename of X to Y also replaced ..." is a guess about history the diff does not show — state only what the changed lines say.
- Keep conversation facts out of the body even when true (e.g. what another package lacks); if the diff does not show it, the message does not say it.
