# Loop and stop rule

How a `loop` run goes on after each change, and when it stops (SKILL.md
section 9). Read after the first commit or drop of a `loop` run.

With `loop`, after each commit or drop, re-measure the views the change touched
and take the next finding. Stop when no remaining finding past its threshold,
or counted, is one the run may fix — counting only findings not dropped, not
forbidden, and not blocked by sections 3 to 5 or a dirty file — or when the run
has made `max` change commits. No cap by default. Before stopping on the stop
rule, measure the whole scope once more: a fix can move cost elsewhere, and a
new finding there continues the loop.
