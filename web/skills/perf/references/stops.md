# Interactive stops

How a run without `auto` stops on each change and reads the reply (SKILL.md
section 8). Read before the first stop.

Without `auto`, stop once per change, after building, measuring, and checking
it. A change with no gain beyond the noise never reaches a stop; it is dropped.

```
Change 2 — Devices: search input runs a 180 ms long task per keystroke
Change: dedupe tags with a Set instead of a nested scan
Measure: long task 180 -> 30 ms, median of 5 at 4x CPU; bench 9.1 -> 0.4 ms/op
Checks: pass (targeted)
Reply: commit · drop · or say what to change
```

- `commit`: commit it (SKILL.md section 6, step 8). While a targeted check is
  red, say so and stop again instead.
- `drop`: restore the tree as it was before the change, pictures included;
  its finding is not taken up again this run, by that change, part of it, or
  any other fix; a user wanting a different fix replies with a prompt, not
  `drop`. Drops are remembered for the current run only.
- Anything else is a prompt: rework the change, re-measure, re-run the
  visible-change check and the targeted checks (a repair already spent is
  not renewed), and stop again, with no commit in between.
- A reply saying "never …" also writes a `PERF: never …` comment, in the file's
  comment syntax, at the code concerned: into that change's commit, or on a
  drop into its own commit adding that comment alone — summary
  `docs(perf): never <x>`, no body, `Perf-Finding:` only. That commit counts
  toward `max` like any other; without `loop`, the drop still ends the run.
- A reply asking to stop ends the loop: restore the tree as `drop` does, not
  counted as a drop.
