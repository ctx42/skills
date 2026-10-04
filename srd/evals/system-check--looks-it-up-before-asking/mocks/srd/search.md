---
type: agent
---
The documentation corpus holds exactly two sections relevant to this SRD.

Section A, the Main Glossary entry for Namespace:
{"title":"Main Glossary","id":"docs/glossary/main_glossary.md","path":"docs/glossary/main_glossary.md","rank":5,"heading_path":["Main Glossary","Namespace (NS)"],"source_url":"https://docs.example.com/glossary/main","score":0.88,"text":"Namespace (NS): A named grouping that scopes Tag Definitions within a Project. Each Namespace has a short code that prefixes the names of the Tags it holds."}

Section B, the Tags concept page:
{"title":"Tags","id":"1774485611","path":"docs/concepts/tags.md","rank":2,"heading_path":["Tags","Tag names"],"source_url":"https://docs.example.com/concepts/tags","score":0.84,"text":"Tag names represent a hierarchical structure expressed as a dot-separated series of Tag node names, for example `site.zone.pump`. Each Tag node name MUST start with a letter a-z. Every Tag Definition carries a Tag Kind besides its name: `string`, `number`, or `boolean`; a Tag cannot be created without one."}

For a query about Namespace, namespaces, or Namespace codes, answer
{"results":[<section A>]}. For a query about Tags, Tag names, Tag Kind, or
Tag Definitions, answer {"results":[<section B>]}; a query touching both
gets both. The corpus says nothing about user sessions, tenants, or whether a
session may span Customers: for such a query answer {"results":[]}. For
every other query answer {"results":[]}.
