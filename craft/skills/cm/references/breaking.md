# Breaking changes

Read before marking a commit breaking, or before deciding it is not.

A change is breaking when it breaks a caller that was correct before — an
exported symbol removed, renamed, or given a new signature; a behavior or
default changed; a config key or wire format no longer accepted. Documented or
not: a caller written against what the code actually did is broken just the
same, so the test is whether correct code stops working, not whether a doc said
so. A bug fix that makes observable behavior *match* what was already promised
is not breaking, or every `fix` would carry a `!`. Say in the body who has to
act anyway: code written against the buggy behaviour stops working, and those
callers — not the ones the bug bit — are the ones with something to do.

An API no release tag contains has no callers to break. In a repo that tags its
releases, run `git tag --contains <sha>` on the commit that added the API, found
with `git log -S'<name>' --reverse --format=%h`; when it lists no tag, the
change gets no `!` and no footer.
