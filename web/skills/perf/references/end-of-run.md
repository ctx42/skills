# End of run

The report every run ends with (SKILL.md section 11). Read before writing it.

Once stopped, list every finding left under Recommendations, whatever kept the
run from it; ideas dropped or discarded this run go under Dropped.

```
2 commits, 1 dropped; stopped: stop rule
Checks: pass

| Commit  | Summary                                       | Before -> After   |
|---------|-----------------------------------------------|-------------------|
| a1b2c3d | perf(devices): insert the device rows at once | INP 610 -> 140 ms |

Dropped
- Settings: memoize the form — no measurable gain

Recommendations
- External API: the asset service has no batch lookup; one call per device
- Back end without live reload: merge /api/devices and /api/device-status
- Visible change: virtualize the 2000-row device list (long task 120 ms)

Not measured
- Bundle: no build command
- Settings save: a write flow, not in the focus
```

`N` counts the commits `git log <start>..HEAD` lists, the final check's included
(Before -> After `—`); `M` counts drops, discarded failures, and reverted
changes. The checks line is `Checks: pass` (known red checks aside),
`Checks: red — <check>`, or `Checks: none` when the final check was skipped. The
reason is `stop rule`, `max reached`, `single run`, or `user`. Recommendations
group under: External API, Own API outside the merge rule, Back end without live
reload, Visible change, Code quality (naming the rule a gain would break); one
that contradicts a `UX:` comment names that comment's location. Size each table
column from its longest cell before writing the table. Omit an empty section.
