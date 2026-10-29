# Final check

How `perf` runs the end-of-run full checks (SKILL.md section 10): on exit
status, a known test check gated on its failing test names and any other known
red check left out (SKILL.md section 1, step 8).

The steps below run when a check turns red that was green on the untouched
tree. Their commits write no pictures and `git rm -q` every tracked
`dev/perf/*.png`. They obey the focus limit and never touch a file the start
found dirty; a repair that would counts as failed. A repair commits without a
stop; an interactive run stops only once it failed (step 3).

1. Pin it on a commit: `git bisect start HEAD <start>`,
   `git bisect run <check>`, `git bisect reset`.
2. One repair, committed as a `fix` (`craft:cm` at `mini`, no Perf fields, the
   body naming the commit it repairs) once the full checks pass and a
   re-measure shows the commit's gain kept (SKILL.md section 2's noise rule).
3. Still red, or the gain lost: under `auto`, revert that commit
   (`git revert --no-commit <hash>`, summary `revert: <its summary>`) and list
   its change under Dropped with the failing check. Interactive: stop showing
   the failure and the commit — reply `revert`, or a prompt for one more
   repair, after which a check still red reverts.
4. A revert that conflicts is aborted (`git revert --abort`) and the check
   stays red in the report.
5. Bisect pins no single commit (the check flakes, or only the changes
   together fail): re-run it once; still red, one repair at HEAD as a `fix`,
   kept only with every gain kept; still red, it stays red, nothing is
   reverted, and no stop asks.
