# The `review` flag

Read when `review` comes with `apply` or `asis` and `.go` files changed.

Before anything is staged, start the `go-change-reviewer` agent with the
repository path as its prompt and commit only after it records a pass, which
means no Blocker; name any lesser findings in the reply. A Blocker stops the
run: commit nothing, not even files it does not touch, and report it. No such
agent: say so, commit nothing, and stop.
