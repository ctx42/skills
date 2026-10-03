---
type: agent
---
The corpus holds two sections relevant to this SRD.

Section A, a knowledge-base page (the page file is also at `kb/sound-file-tags.md`
in the workspace):
{"doc_id":"kb/sound-file-tags.md","heading_path":["Sound File Meta Tags","Sound File meta tags imported as platform Tags"],"source_url":"","score":0.86,"text":"When the platform ingests a Sound File, it imports each tag of the file's `meta` chunk as a platform Tag under the `snd` node, keeping the tag's own name: `rec.gain` becomes `snd.rec.gain`. A Tag lookup therefore finds a Sound File by its imported `meta` tags."}

Section B, the Sound File format documentation:
{"doc_id":"confluence/infraport/formats/sound_file_documentation.md","heading_path":["Sound File Documentation","meta chunk"],"source_url":"https://confluence.example.com/infraport/formats/sound-file#meta-chunk","score":0.71,"text":"The `meta` chunk carries the sub-type `tags`. Each tag is one sub-chunk of the `meta` chunk: the sub-chunk ID names the tag and its data holds the value."}

For a query about Sound File `meta` tags, importing tags, the `snd` node, or
how a Tag lookup finds Sound Files, answer {"results":[<section A>, <section B>]}.
For a query about the `meta` chunk or the Sound File format, answer
{"results":[<section B>]}. No document other than the knowledge-base page
states that `meta` tags are imported as platform Tags. The corpus says nothing
about Tag lookup speed or performance targets: for such a query answer
{"results":[]}. For every other query answer {"results":[]}.
