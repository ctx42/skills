---
type: regex
target: {source: file, path: craft/skills/foo/SKILL.md}
---
^---\nname: foo\ndescription: >\n  Formats the quarterly widget report\.\nlicense: MIT\n---\n\n# foo\n\nFormats the quarterly widget report from the raw export\.\n\n## Usage\n\n```\n\/foo <export\.csv>\n```\n\n## Steps\n\n1\. Read the export the user names\.\n2\. Group rows by widget family; sum each family's units\.\n3\. Write `report\.md` beside the export\.\n\n## Output\n\nName the report written and the families it covers; nothing else\.
