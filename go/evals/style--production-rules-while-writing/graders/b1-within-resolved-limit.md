---
type: regex
target: {source: file, path: service.go}
match: not_contains
flags: "m"
---
^\t{0}[^\t\n]{73,}$|^\t{1}[^\t\n]{69,}$|^\t{2}[^\t\n]{65,}$|^\t{3}[^\t\n]{61,}$|^\t{4}[^\t\n]{57,}$|^\t{5}[^\t\n]{53,}$|^\t{6}[^\t\n]{49,}$
