---
type: agent
---
The documentation corpus holds exactly three sections relevant to this SRD.

Section A, the Starforge Terms entry for Launch Slot:
{"title":"Starforge Terms","id":"docs/glossary/terms.md","path":"docs/glossary/terms.md","rank":5,"heading_path":["Starforge Terms","Launch Slot"],"score":0.88,"text":"Launch Slot: A 90-minute period booked for one launch."}

Section B, the Part Kits concept page:
{"title":"Part Kits","id":"1000000103","path":"docs/concepts/part-kits.md","rank":2,"heading_path":["Part Kits","Picking"],"source_url":"https://wiki.example.com/pages/1000000103","score":0.84,"text":"Part kits are picked 5 working days before stage integration. Every Part Kit carries a pick priority, one of `routine`, `expedite`, or `critical`; a Part Kit cannot be created without one."}

Section C, the Starforge Terms entry for Assembly Bay:
{"title":"Starforge Terms","id":"docs/glossary/terms.md","path":"docs/glossary/terms.md","rank":5,"heading_path":["Starforge Terms","Assembly Bay"],"score":0.81,"text":"Assembly Bay: One of the four build halls, Bay A to Bay D."}

For a query about Launch Slots, launch slot, or slot definitions, answer
{"results":[<section A>]}. For a query about Part Kits, picking, pick
priority, or stage integration, answer {"results":[<section B>]}. For a query
about Assembly Bays, answer {"results":[<section C>]}. A query touching
several of these gets each matching section. No section says whether a Part
Kit may span or be split across Assembly Bays or where a kit is staged: such a
query gets section C when it names Assembly Bays and nothing else. For every
other query answer {"results":[]}.
