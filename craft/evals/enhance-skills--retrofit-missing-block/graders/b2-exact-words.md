---
type: regex
target: {source: file, path: craft/skills/foo/SKILL.md}
---
##\s+Self-learning\s+Obey\s+this\s+skill's\s+lessons\s+when\s+it\s+has\s+any:\s+read\s+both\s+a\s+sibling\s+`LESSONS\.md`\s+and\s+`\$\{AGENT_DATA_DIR:-\$HOME\/\.agent-data\}\/ctx42-skills\/lessons\/craft\/foo\.md`,\s+the\s+sibling\s+winning\s+a\s+conflict\s+—\s+a\s+read-only\s+install\s+writes\s+the\s+second,\s+and\s+what\s+it\s+learned\s+there\s+stays\s+true\s+once\s+the\s+checkout\s+is\s+writable\s+again\.\s+Most\s+runs\s+have\s+none;\s+absence\s+is\s+the\s+normal\s+case\s+and\s+needs\s+no\s+comment\.\s+On\s+a\s+correction\s+or\s+self-caught\s+mistake,\s+append\s+a\s+one-line\s+rule\s+to\s+the\s+sibling\s+when\s+this\s+directory\s+is\s+writable,\s+else\s+to\s+the\s+fallback,\s+creating\s+it,\s+and\s+report\s+where\.
