---
type: regex
target: {source: file, path: project-config.md}
flags: "m"
---
^sources:(?:[ \t]*\[[ \t]*conflu[ \t]*,[ \t]*kb[ \t]*\]|[ \t]*\n[ \t]+- conflu[ \t]*\n[ \t]+- kb)[ \t]*$
