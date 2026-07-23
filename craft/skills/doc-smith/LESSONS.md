# Lessons

- Glossary/definition entries state what a term *means*, not facts about the 
  system — strip behavioral, default, or configuration claims (they belong in
  reference/concept docs and go stale independently of the term).
- Attribute each verb to the agent that performs it — never credit a
  consuming/receiving system with producing or recording data it only ingests.
- Treat every absolute claim ("all", "only", "never", "always") as a
  contradiction magnet — re-verify it against each entity the doc adds later; a
  local exception downstream does not fix the absolute, so scope the absolute
  itself.
- Separate what a format permits from what the domain requires — don't assert an
  optionality the schema allows but the domain rules out; confirm cardinality
  against intent.
- Don't cover materially-different parallel items with one symmetric statement
  true for only one — state the asymmetry.
- When reporting proposed edits, findings, or nits, present them as a numbered
  list so each can be addressed separately.
- Reserve "noise" for unwanted interference; call the signal of interest
  "signal", even when the domain colloquially calls it "noise" — the ambiguity
  causes misunderstandings in signal-processing docs.
