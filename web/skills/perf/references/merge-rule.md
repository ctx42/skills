# Merge rule

When `perf` may merge two API calls into one endpoint (SKILL.md section 3).

Merge two calls into one endpoint only when all hold: the view makes both on
every load; they run one after the other, or are always fired together; their
data describes one resource (a list and its counts or statuses). Never add an
endpoint bundling unrelated resources for one page. Keep an old endpoint while
anything else in the repo calls it; remove it in the same commit once nothing
does. Anything outside this rule goes to Recommendations. With back-end edits
off, a pair the rule allows that still runs one after the other at the end
goes there under Back end without live reload; one fired together does not.
