---
type: regex
target: {source: file, path: project-config.md}
flags: "m"
---
^sources:(?:[ \t]*\[[ \t]*wiki[ \t]*,[ \t]*kb[ \t]*\]|[ \t]*\n[ \t]+- wiki[ \t]*\n[ \t]+- kb)[ \t]*$
