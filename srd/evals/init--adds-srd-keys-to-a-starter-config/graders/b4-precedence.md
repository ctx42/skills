---
type: regex
target: {source: file, path: project-config.md}
flags: "m"
---
^precedence:(?:[ \t]*\[[ \t]*kb[ \t]*,[ \t]*conflu/doc[ \t]*\][ \t]*|[ \t]*\n[ \t]+- kb[ \t]*\n[ \t]+- conflu/doc[ \t]*)$(?![\s\S]*^[ \t]+- conflu/srd)
