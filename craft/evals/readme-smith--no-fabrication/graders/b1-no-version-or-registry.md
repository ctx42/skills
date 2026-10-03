---
type: regex
target: {source: file, path: README.md}
match: "not_contains"
flags: "i"
---
@v\d|\bv\d+\.\d+\.\d+|brew install|apt(-get)? install|docker (pull|run)|npm install|snap install|scoop install
