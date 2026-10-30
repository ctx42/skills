---
type: regex
target: {source: file, path: project-config.md}
flags: "m"
---
^sources:(?:[ \t]*\[[ \t]*docs[ \t]*,[ \t]*kb[ \t]*\]|[ \t]*\n[ \t]+- docs[ \t]*\n[ \t]+- kb)[ \t]*$
