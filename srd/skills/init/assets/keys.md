## SRD skill keys

The srd skills read three keys that only they use; `/srd:init` proposes and
writes them, and never changes another key. The docket plugin writes the rest
of this file and runs the doc server.

| Key            | Meaning                                                                                                              |
|----------------|----------------------------------------------------------------------------------------------------------------------|
| `kb`           | Knowledge-base folder; confirmed platform facts land in its `_inbox.md`. List it in `sources` too, or it is not searched |
| `srd-standard` | The SRD standard document, by path or `id`; the skills read it through the doc server at the start of every session  |
| `srd-work`     | Folder for SRD working files (`review`, `decisions`, `questions`), outside every source; `none` keeps them beside each SRD |

A skill that finds one of these missing, `kb` not in `sources`, or a
`srd-work` folder inside a source stops and names the fix. `/srd:check`
reports every problem at once.
