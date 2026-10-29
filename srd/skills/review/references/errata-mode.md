# errata — re-sorting a review file

The full procedure for `review <srd> errata`, read on demand when that mode
runs. Every other mode can ignore this file.

Re-sort an existing review file so its errata sit in `## Errata`. Reclassify
only — hunt no new defects. Keep every number. Bump `updated:` when something
moved; a run that changes nothing writes nothing, or the pass is not idempotent
and a second run is indistinguishable from a first.

Rewriting a prose fix into the substitution shape needs the SRD's current text
to quote `old` exactly, so this mode reads the SRD as well as the review file.
It still edits only the review file.

1. Test each open finding against the gate and allowlist in `errata.md`. One
   that qualifies and is not yet under `## Errata` moves there keeping its
   number, severity, category, and citation; create the section at the top if
   absent. Classify conservatively: leave ambiguous findings where they are. A
   qualifying finding written as prose ("fix the spelling") is rewritten into
   the substitution shape as it moves. One finding naming several different
   fixes is split into one finding per substitution: each qualifying one moves
   to `## Errata` under a new number, while anything failing the gate stays
   under the original number, rewritten to name only the sites left; when every
   part qualifies, the original number goes with the first substitution. Report
   each split (the defects were already recorded, so this is not hunting).
2. Leave every other finding untouched, and drop any document section the move
   left with no open findings — `review-file.md` omits an empty section, and a
   heading left standing would move on the next run. The pass is idempotent.
3. If the review file does not exist, fall through to a normal review.
4. Report which numbers moved ("moved #4, #6, #9 to Errata"); say so when none
   moved.
