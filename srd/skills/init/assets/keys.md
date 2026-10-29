## Front matter keys

The front matter above configures the MCP doc server and the srd skills. Keys
are flat. Every path is relative to the folder holding this file; an absolute
path is an error. `/srd:init` adds the keys the skills need and never changes a
value that is set.

| Key              | Read by        | Meaning                                                                                                                                    |
|------------------|----------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| `mcp-server`     | server, skills | Name the server is registered under in `.mcp.json`; the skills call its tools as `mcp__<name>__<tool>`                                     |
| `mcp-port`       | server         | Port the server listens on; the docket plugin moves it to a free port, and updates `.mcp.json`, when it is busy                            |
| `sources`        | server         | Top-level folders the server indexes; each name is the first part of its documents' paths                                                  |
| `watch`          | server         | Rebuild the index when a source or the gap folder changes, without a restart                                                               |
| `watch-debounce` | server         | How long changes must be quiet before a rebuild (for example `500ms`, at most `1m`)                                                        |
| `precedence`     | server         | Folders from most to least trusted; each result carries its folder's `rank` (1 = first), and unlisted folders rank last                    |
| `gaps`           | server         | Gap folder, one Markdown file per documentation gap; it must lie outside every source                                                      |
| `kb`             | server, skills | Knowledge base folder; confirmed facts land in its `_inbox.md`                                                                             |
| `initiatives`    | server, skills | SRD folder, one subfolder per SRD; its documents carry no `rank`                                                                           |
| `srd-standard`   | skills         | The SRD standard document; the skills read it through the server, never a copy                                                             |
| `glossary`       | server, skills | The shared glossary, a file or a folder; its terms come from the server                                                                    |
| `srd-work`       | skills         | Folder for SRD working files (`review`, `decisions`, `questions`); keep it out of `sources`. `none`, or no key, keeps them beside each SRD |

A document's identity is its front-matter `id` when it has one (every synced
page has one), otherwise its path from this folder. An SRD is named by its
folder under `initiatives`, for example `export-rate-limit`.
