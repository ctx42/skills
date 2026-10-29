# check — re-verifying findings

The full procedure for `review <srd> check`, read on demand when that mode
runs. Every other mode can ignore this file.

Re-verify only — hunt no new defects. Keep every number; bump `updated:` only
if something else in the file changed (review-file.md).

Trailing finding numbers scope the pass to those findings; the rest stay
untouched. Write them `#n,n` — `check #4,6` names #4 and #6; any other form: say
so and ask. Report any listed number that is absent or already
resolved/withdrawn, and check the rest. Omitted, check every open finding.

1. Judge each finding in scope against the current text:
   - fixed → tick `[x]` and move to `## Resolved`.
   - partial → stays `[ ]` in its section with `*(Partial — …)*` appended;
     never ticks.
   - not addressed → stays `[ ]`, untouched — once the KB pages whose
     `srd_ref` names the SRD are read: an author answer banked there that
     invalidates the finding withdraws it (step 2), citing that page.
2. Withdrawal is check-only: a finding that proves invalid (mistaken, the
   author justified the text, or it cites a rule identifier the fetched
   standard does not state) moves to `## Withdrawn` with a reason, stamped with
   this run's `updated:` time (review-file.md). Never carry a
   non-enforceable finding open. No other mode withdraws — which is why this
   mode is where another skill's invalidity report lands: `srd:questions`
   cannot write the review file, so it names the numbers its corpus lookups
   disproved and the user runs `check #n…` over them. Re-verify such a number
   like any other and withdraw it on the evidence, never on the report alone:
   `get_doc` the document the report names; when it cannot be read, the
   finding stays open, its assessment saying the source was unreachable.
3. Close with both, in this order: the status table — number, current state,
   assessment — then the task-oriented line (Modes) beneath it. The table says
   what this pass did to each finding; the line says where the SRD now stands.
