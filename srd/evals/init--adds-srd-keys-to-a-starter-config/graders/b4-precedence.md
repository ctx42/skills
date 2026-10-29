---
type: regex
target: {source: file, path: project-config.md}
flags: "m"
---
^precedence:(?:[ \t]*\[[ \t]*kb[ \t]*,[ \t]*wiki/doc[ \t]*\][ \t]*|[ \t]*\n[ \t]+- kb[ \t]*\n[ \t]+- wiki/doc[ \t]*)$(?![\s\S]*^[ \t]+- wiki/srd)
