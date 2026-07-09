- Before writing/formatting a Markdown file, read the repo `.editorconfig` (and
  any `.markdownlint`/`.prettierrc`) for `[*.md] max_line_length`; wrap prose
  AND tighten/align tables to it. Count characters, not bytes — an em-dash is 3
  bytes but 1 column, so byte-based `awk length` over-reports.
