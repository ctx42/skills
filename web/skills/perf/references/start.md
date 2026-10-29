# Start

How `perf` runs start steps 2, 3, and 6 to 9 (SKILL.md section 1). Read at the
start, before step 2.

## Dev server

Step 2. Take candidate URLs from the dev config (a script's `--port`,
`server.port`, `.env` `PORT`, compose ports, the framework's default),
cross-check them with the listening ports (`ss -ltnp`), and probe each with
`curl -sS -o /dev/null -w '%{http_code}'`. Nothing listening: stop. One
match: that URL. Several, or ports listening but none matching the config:
ask which URL in the step 9 message, not before it.

## Chrome

Step 3. Chrome DevTools MCP is available (`new_page`, `emulate`, `click`,
`evaluate_script`, `list_network_requests`, `take_heapsnapshot`) and its
window is visible: open the URL with `new_page`; a `navigator.userAgent`
containing `HeadlessChrome` means headless — say to restart the MCP server
without `--headless`.

## Back end

Step 6. The back end is the server answering the app's API (the dev config's
proxy target, or the origin of the API requests the page makes). Its dev setup
live-reloads when the server runs under air, nodemon, `node --watch`,
`tsx watch`, `uvicorn --reload`, or a file watcher wrapping it.

## Build

Step 7. The build command is a `package.json` `build` script or a `Makefile`
target. Point its output at the scratch directory
(`vite build --outDir <scratch>/build`, the bundler's equivalent flag) — a
plain build empties the project's output directory, deleting tracked files and
replacing what a server may embed.

## Checks

Step 8. Find the project's checks as `craft:fix-all` finds them — `AGENTS.md`,
`CLAUDE.md`, `CONTRIBUTING.md`, a `Makefile`, the package manifest: build,
test, lint, format, e2e included. The targeted checks are the static ones
(lint, format, typecheck, vet), each by its own command, even inside a
combined target, plus the tests covering the files a change touches
(`vitest related --run <files>`, `go test <their packages>`); the full checks
are all of them. Run the full checks once on the untouched tree. A check
already red there is known: name it in the step 9 message and save its failing
test names. A known test check stays in every gate, passing while every test
it fails also failed at the start, never judged by its failure count; any
other known check stays out of every gate (run the others by name) and never
blocks a commit.

## Message

Step 9. Send one message and wait: the detected URL, open in the Chrome window,
whether back-end edits are on or off and why, and a request to log in there if
the app needs it, then reply (or give the right URL). An app with no login
proceeds on the reply. The start asks nothing else.
