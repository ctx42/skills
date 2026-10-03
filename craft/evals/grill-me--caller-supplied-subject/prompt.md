---
tags: [case:grill-me--caller-supplied-subject, skill:grill-me, sec:grill-me:usage, sec:grill-me:how-it-works, sec:grill-me:rules, sec:grill-me:self-learning]
runs: 1
max_turns: 40
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
append_system_prompt: |
  The user writes English; reply in English.

  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.
  Before taking a scripted answer, write out in full, as your reply text, the
  message you would send the user at that point.

  1. The order is not cancelled. It stays queued on the server and is delivered when the station reconnects.
  2. If the station stays offline for more than 24 hours the order expires and the dispatcher gets a notification. Orders the station acknowledged before it dropped are not affected.
  3. The readers are dispatchers using the web console; while the station is offline the order shows the status "Pending delivery".
  4. The UI calls an offline station "Disconnected". "In-flight" means sent to the station but not yet acknowledged.
  5. That is everything I know; nothing else is open.
---

/craft:grill-me the docs don't say what happens to an in-flight order when a station goes offline
