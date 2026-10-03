#!/usr/bin/env bash
set -euo pipefail
mkdir -p craft/skills/foo
cat > craft/skills/foo/SKILL.md <<'EOF_0'
---
name: foo
description: >
  Formats the quarterly widget report.
license: MIT
---

# foo

Formats the quarterly widget report from the raw export.

## Usage

```
/foo <export.csv>
```

## Steps

1. Read the export the user names.
2. Group rows by widget family; sum each family's units.
3. Write `report.md` beside the export.

## Output

Name the report written and the families it covers; nothing else.
EOF_0
