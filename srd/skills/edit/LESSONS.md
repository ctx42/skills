# Lessons

- Never fix a conflict by having one requirement cite others by id ("apply UI-6 through UI-10 only …"); keep each requirement standalone — put the condition in each rule, via a glossary term when it is long.
- Before proposing a fix, grep the knowledge base and <srd>.decisions.md for the quoted text: a prior author ruling (e.g. UI-18 "(reversed drop shape)" is required) means leave it, and recommend withdrawal.
- A bulk rename (e.g. lowercasing defined terms) must exempt UI components from user_interface_glossary.md (Infobar, Data Point Infobar, Toast): check each term's glossary file before lowercasing it.
- Before declaring an entry clean, check every capitalized noun phrase that reads like a name ("Measurements presentation") against the glossaries and the requirements it summarizes; an undefined pseudo-name is a finding.
- When the user rewords a requirement to generalize it, confirm what the generalization means (e.g. "the existing view gains support", not "a new structure") before proposing to remove siblings it seems to make redundant.
- Comment blocks stay read-only unless the user explicitly asks to resolve one: then remove its `> [!comment]` callout and its `[^…]` footnote reference from the requirement, and log the removal.
- Glossary definitions stay general: never name UI surfaces, labels or where a term is shown — those change; put them in UI requirements.
