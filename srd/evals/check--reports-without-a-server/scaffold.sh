#!/usr/bin/env bash
set -euo pipefail
cat > project-config.md <<'EOF_PC'
---
mcp-server: docs
mcp-port: 7777
sources:
  - docs
kb: kb
initiatives: docs/initiatives
srd-standard: docs/srd-standard.md
glossary: docs/glossary
precedence:
  - kb
  - docs/api
srd-work: srd-work
watch: true
---

# Project configuration

## SRD skill keys

The srd skills read three keys that only they use. `/srd:init` proposes them
and writes them after you confirm, and never changes another key; the docket
plugin writes the rest of this file and runs the doc server. A skill that
finds one of these keys missing, `kb` not in `sources`, or a `srd-work` folder
inside a source stops and says how to fix it. `/srd:check` reports every
problem at once.

### `kb`

The knowledge base folder. It holds facts about the platform that SRD work
uncovered and a person confirmed, but the documentation does not state.
`/srd:kb` writes each new fact to `<kb>/_inbox.md` first, then sorts the inbox
into topic pages, one page per subject. List this folder in `sources` too, or
its facts cannot be searched.

### `srd-standard`

The document that defines what an SRD must contain: its metadata fields,
status values, sections and their order, identifier format, and wording
rules. The value is the document's path, or its `id`. The skills read it
through the doc server at the start of every session and apply only the rules
it states; they never keep a copy, so a change takes effect in the next
session.

### `srd-work`

The folder for SRD working files (`review`, `decisions`, `questions`). An SRD
at `initiatives/login/login-srd.md` gets its review at
`<srd-work>/login/login-srd.review.md`. Keep this folder out of every source,
so drafts and review notes never appear as search results or as facts. Set it
to `none` to keep the working files next to each SRD instead. Choose one
layout and keep it: the skills look for working files in one place only and
never move them.

### How the skills use the doc server's keys

The docket plugin's section defines these keys; the skills rely on them so:

- `initiatives` holds the SRDs, one subfolder per SRD. The subfolder's name is
  the SRD's short reference everywhere else: in gaps, in knowledge base pages,
  and in working file paths.
- `glossary` is where the skills check an SRD's terms and what they link
  terms to.
- `gaps` holds the documentation gaps. `/srd:report-doc-gap` records them and
  `/srd:backlog` works through them, only through the doc server's gap tools.
- `precedence` settles disagreements: when two documents say different things
  and their ranks differ, the skills take the better-ranked one and record the
  other as a documentation gap; with equal ranks they show you both.
EOF_PC
cat > .mcp.json <<'EOF_MJ'
{"mcpServers": {"srd": {"type": "http", "url": "http://localhost:7777/mcp"}}}
EOF_MJ
mkdir -p docs/api docs/glossary docs/initiatives/pay kb gap srd-work/pay
touch gap/.gitkeep
printf '# Invoices\n' > docs/api/invoices.md
printf '# Payments\n' > docs/api/payments.md
printf '# SRD standard\n' > docs/srd-standard.md
printf '# Terms\n' > docs/glossary/terms.md
printf '# Card Payments\n' > docs/initiatives/pay/pay-srd.md
printf '# Billing\n' > kb/billing.md
printf '# Review\n' > srd-work/pay/pay-srd.review.md
