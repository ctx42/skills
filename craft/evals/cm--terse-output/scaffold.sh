#!/usr/bin/env bash
set -euo pipefail
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
cat > go.mod <<'EOF_0'
module example.com/app

go 1.22
EOF_0
mkdir -p cmd/greet
cat > cmd/greet/main.go <<'EOF_1'
// Command greet prints a greeting.
package main

import (
	"flag"
	"fmt"
)

func main() {
	name := flag.String("name", "world", "who to greet")
	flag.Parse()
	fmt.Printf("hello, %s\n", *name)
}
EOF_1
git add -A
git commit -qm 'feat(greet): add greet command'
mkdir -p cmd/greet
cat > cmd/greet/main.go <<'EOF_0'
// Command greet prints a greeting.
package main

import (
	"flag"
	"fmt"
	"strings"
)

func main() {
	name := flag.String("name", "world", "who to greet")
	shout := flag.Bool("shout", false, "print the greeting in upper case")
	flag.Parse()
	msg := fmt.Sprintf("hello, %s", *name)
	if *shout {
		msg = strings.ToUpper(msg)
	}
	fmt.Println(msg)
}
EOF_0
git add -A
