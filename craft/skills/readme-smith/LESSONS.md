- Before writing/formatting a Markdown file, read the repo `.editorconfig` (and
  any `.markdownlint`/`.prettierrc`) for `[*.md] max_line_length`; wrap prose
  AND tighten/align tables to it. Count characters, not bytes — an em-dash is 3
  bytes but 1 column, so byte-based `awk length` over-reports.
- When a README has both a Features list and a step-by-step Usage/run sequence,
  keep their jobs distinct: Features states capabilities (what it does — terse,
  scannable bullets), Usage owns mechanics (how to run — the ordered steps and
  example). If a Features bullet re-narrates a run step, cut the mechanics from
  the bullet.
- When the tool offers more than one install or integration mechanism, document
  each one, and enumerate them from the tool's own docs — not from what sibling
  READMEs happen to show. A mode absent from a sibling README is not evidence it
  doesn't exist.
