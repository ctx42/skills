---
type: regex
target: {source: file, path: README.md}
flags: "m"
---
^## Features[\s\S]*?^## Install(ation)?\b[\s\S]*?^## Usage[\s\S]*?^##+ (Configuration|Flags|Options)
