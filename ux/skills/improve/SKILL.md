---
name: improve
description: >
  Improves a running web app's UX one committed change at a time: audits it in
  a visible Chrome (accessibility, Nielsen's heuristics, 1440px and 390px
  layouts, loading, empty, and error states), builds the top-ranked fix, and
  commits it with before/after screenshots. Use when asked to improve, polish,
  or fix a web app's UX, UI, accessibility, or layout, or a part a screenshot
  shows.
argument-hint: "[auto] [loop] [max <n>] [<focus>]"
license: MIT
---

# improve

## Usage

```
/ux:improve                   audit the app, build the top fix, stop for commit, drop, or a prompt
/ux:improve auto              the same, committing without stopping
/ux:improve loop              one change after another until the stop rule
/ux:improve auto loop max 5   unattended, at most 5 commits
/ux:improve <focus>           do what the focus asks to the part it names or a screenshot shows
```

`auto`, `loop`, and `max <n>` are leading keywords in any order; the first
other token starts the focus, free text to the end. A pasted image, or an image
path in the focus, shows the part. `max <n>` counts commits only — drops and
discarded failures do not count — and needs `loop`: given without it, say
"`max` needs `loop`" and stop before any other step. Without `loop` a run makes
at most one change. No focus audits the whole app.

Arguments: $ARGUMENTS

Report tersely: no preamble or narration; state each fact once. Never push,
amend, rebase, or touch a commit the run did not make.

## 1. Start — before any edit

Check in order. The first that fails is named as the missing prerequisite and
the run stops, editing and committing nothing:

1. The working directory is a web app's source tree: markup, styles, or
   scripts the app serves, beside a manifest or dev config (`package.json`, a
   framework or bundler config, a `Makefile` target that serves it).
2. A dev server is reachable. Never start one, even when the config says how.
   Take candidate URLs from the dev config (a script's `--port`,
   `server.port`, `.env` `PORT`, compose ports, the framework's default),
   cross-check them with the listening ports (`ss -ltn`), and probe each with
   `curl -sS -o /dev/null -w '%{http_code}'`. Nothing listening: stop. One
   match: that URL. Several: list them and ask which. Ports listening but none
   matching the config: ask for the URL.
3. Chrome DevTools MCP is available (`new_page`, `emulate`, `take_screenshot`,
   `lighthouse_audit`, `evaluate_script`) and its window is visible: open the
   URL with `new_page`; a `navigator.userAgent` containing `HeadlessChrome`
   means headless — say to restart the MCP server without `--headless`.
4. The craft plugin is installed: `craft:cm` is in your skill list.

Then:

5. Record the start commit (`git rev-parse HEAD`) and the dirty files
   (`git status --porcelain`).
6. Find the project's checks as `craft:fix-all` finds them — `AGENTS.md`,
   `CLAUDE.md`, `CONTRIBUTING.md`, a `Makefile`, the package manifest: build,
   test, lint, format, e2e included — and run them once on the untouched tree.
   A check already red there is known: name it in the message below, and
   leave it out of every gate (run the others by name) — it never blocks a
   commit.
7. Send one message and wait: the detected URL, open in the Chrome window, and
   a request to log in there if the app needs it, then reply (or give the right
   URL). When the user's instructions or the harness forbid committing, the
   same message asks leave to commit every change of this run, as
   `craft:fix-all` does. A reply without that leave: list the ranked findings
   the run would act on, write no report, and stop before any edit — never
   edit and leave the change uncommitted instead. An app with no login
   proceeds on the reply. The start asks nothing else.

## 2. Audit

Scope: with no focus, every page reachable from the app's navigation (its
shared header, sidebar, menus, and footer); with a focus, only the views that
show the focused part. Never click logout, nor submit, delete, or otherwise
change data the app stores: reach a state by navigation, filters, emulation,
and reading the code.

Per page:

- Accessibility: `lighthouse_audit` accessibility failures (WCAG 2.2 AA);
  text contrast below 4.5:1 (3:1 for large text).
- Layout at 1440px and 390px (`emulate` viewport `1440x900x1` and
  `390x844x3,mobile,touch`): horizontal overflow
  (`document.documentElement.scrollWidth` above the width set — a mobile
  viewport widens to its content, so never compare with `innerWidth`),
  clipped or overlapping content.
- States: loading (`networkConditions` `Slow 3G`), empty, error (`Offline`
  after load, or a failed request), long content (the longest record the data
  holds). `emulate` reloads the page and drops an injected stub
  (`initScript`): set the viewport first, then navigate with the stub, and
  confirm the state before each measurement or picture.
- Nielsen's 10 heuristics: a finding names the heuristic it breaks.

Before choosing a change, search the source for `UX:` comments
(`grep -rn 'UX:'`, skipping dependency and build dirs). A `UX:` comment is the
only binding previous decision: it states what never to do at the code it sits
on. Never act against one unless a focus says to (section 3); a finding it
forbids goes to Recommendations, citing the comment. Test assertions and
earlier commits do not bind: a change may alter asserted behaviour and rewrite
the test.

Rank, top first:

1. Measurable defects — an accessibility audit failure, overflow or clipping,
   a broken or empty state, unreadable contrast — before named-heuristic
   violations with a concrete fix. Nothing else (a product decision, taste)
   becomes a change without a focus.
2. Within a tier, shared chrome (header, navigation, footer, a layout every
   page uses) and the landing page before deeper pages.
3. Ties go to the smaller change.

## 3. Focus

A focus — any text after the keywords — names a part of the UI or shows it in a
screenshot, with what the user wants; one naming only a part audits that part.
The description is an instruction: implement it even when it is a product
decision. It beats a `UX:` comment, which the same commit removes, its body
saying so. The instruction is the run's first change; with `loop`, the run then
keeps improving that part by the normal rules. With a focus, no commit touches
markup or styles outside the focused part; a fix that would goes to
Recommendations.

## 4. Change cycle

One commit per UX change. One rule applied in several places is one commit with
a picture pair per place; unrelated changes never share a commit. Per change:

1. Pick the top-ranked finding not dropped this run, not forbidden by a `UX:`
   comment, and touching no file the start found dirty (that one goes to
   Recommendations, naming the file — a focus instruction included).
2. Before any edit, delete every untracked `dev/ux/*.png`, then shoot each view
   the change will touch, at each width where it shows, in the state it needs
   (`take_screenshot` with `filePath`; `fullPage: true` where the defect
   lies outside the viewport — horizontal overflow always, since a viewport
   shot crops it away). One pair is `dev/ux/before.png` and
   `dev/ux/after.png`; several are `before-1.png` and `after-1.png` on,
   numbered as in the message. A change that alters nothing on screen (an
   accessible name, an ARIA attribute) shoots no pictures.
3. Make the smallest change that fixes the finding. A behaviour change (what
   the UI does, not how it looks) gets a test.
4. Reload each view bypassing the cache (`navigate_page` `type: "reload"`,
   `ignoreCache: true`; a navigation by URL can keep the old file), confirm
   the page runs the change, re-run the measurement that found the defect —
   it must pass now — and shoot the same views, widths, state, and
   `fullPage` setting to the `after` files. A pair whose files are
   byte-identical (`cmp`) shows nothing: re-shoot both so the defect shows.
5. Run the project's checks on exit status, never on piped or filtered output.
   A check red that was green at the start gets one repair; still red: under
   `auto`, discard the change (restore its files, delete its new files and
   pictures) and list it under Dropped with the failing check; interactive,
   show the failure at the stop.
6. Interactive: stop (section 6). `auto`: commit.
7. Commit: unstage everything (`git restore --staged .`), stage the change's
   code with a plain `git add -- <paths>`, never `-f`, then its pictures by
   file name in their own `git add -f -- <pictures>` (so an ignored `dev/`
   still ships them) — never force a directory, which stages everything its
   ignore rules keep out — `git rm -q --` every tracked `dev/ux/*.png` this
   commit did not write, and write the message (section 5). Then, in one
   command, re-run the checks gated on exit status
   (`make check >out 2>&1 || exit 1`), exit on any byte-identical pair
   (`cmp -s before-1.png after-1.png && exit 1`), compare
   `git diff --cached --name-only` with that list, and `git commit -F -`. A
   red re-run commits nothing and returns to step 5; an identical pair, to
   step 4.

## 5. Commit message

Invoke `craft:cm` at `mini` on the staged diff for the summary and body. After
its body, before any footer it wrote, append three fields wrapped at 72
columns, continuation lines indented two spaces:

```
fix(nav): keep the header inside a phone screen

The header kept a 700px minimum width, so phones scrolled sideways on
every page.

UX-Finding: the header overflows a 390px viewport by 310px on every
  page (horizontal overflow)
UX-Change: drop the header's minimum width and let its links wrap
UX-Pictures: 1 Today, 390px; 2 Settings, 390px
```

`UX-Finding:` what was wrong and the defect or heuristic it breaks;
`UX-Change:` what changed; `UX-Pictures:` each pair's view, width, and state,
numbered as the files — unnumbered for a single pair, `none` for a
comment-only commit or a change with nothing on screen. Never add a trailer
beyond what `cm` allows.

## 6. Interactive stops

Without `auto`, stop once per change, after building it and writing its
pictures to `dev/ux/`:

```
Change 2 — Today, 390px: long task titles clipped mid-word (clipping)
Change: wrap long titles
Pictures: dev/ux/before.png, dev/ux/after.png
Checks: pass
Reply: commit · drop · or say what to change
```

- `commit`: commit it (section 4, step 7). While a check is red, say so and
  stop again instead.
- `drop`: restore the tree as it was before the change, pictures included; the
  idea is not proposed again this run. Drops are remembered for the current
  run only.
- Anything else is a prompt: rework the change, keep its before pictures,
  re-shoot every after, shoot a before for any view the rework newly touches
  (with the change's files stashed), re-run the checks, and stop again, with
  no commit in between.
- A reply saying "never …" also writes a `UX: never …` comment, in the file's
  comment syntax, at the code concerned: with `commit`, into that change's
  commit; with neither `commit` nor `drop`, into the reworked change, which
  stops again; on a drop, into its own commit adding that comment alone —
  summary `docs(ux): never <x>`, no body, the three fields with
  `UX-Pictures: none`.
  That commit counts toward `max` like any other, so reaching `max` with it
  ends the run; without `loop`, the drop still ends the run.
- A reply asking to stop ends the run: restore the tree as `drop` does, not
  counted as a drop, and list the change's finding under Recommendations.

## 7. Loop and stop rule

With `loop`, after each commit or drop, re-check the pages the change touched
and take the next finding. Stop when no remaining finding is a measurable
defect or a named-heuristic violation with a concrete fix — counting only
findings not dropped, not forbidden, and not blocked by a dirty file — or when
the run has made `max` commits. No cap by default. Without `loop`, stop after
one change, committed, dropped, or discarded. What is left (product decisions,
taste, findings a `UX:` comment forbids or a dirty file blocks, and on a stop
at `max` or after one change every finding still qualifying) goes to
Recommendations; ideas dropped this run are listed under Dropped.

## 8. Report

Read every count and hash off `git log <start>..HEAD` and `git show --stat`,
never from memory. Interactive runs end with the same report; a run stopped
at the start (section 1) writes none. Print it in
exactly this shape: the count line first, nothing before it, in the sample's
exact format with its numbers and reason read off this run, and the headings
`Dropped` and `Recommendations` as written.

```
3 commits, 1 dropped; stopped: stop rule

| Commit  | Summary                                         | Pictures |
|---------|-------------------------------------------------|----------|
| a1b2c3d | fix(nav): keep the header inside a phone screen | 2        |

Dropped
- Today, 390px: wrap long task titles — `./check.sh` fails after the change

Recommendations
- Today: deleting a task has no undo (user control and freedom) — `UX:`
  comment at `app.js:41` forbids it
```

`N` is the number of commits `git log <start>..HEAD` lists — a
`docs(ux): never` commit among them, a dropped or discarded change never — and
the table lists each; `M` counts drops and discarded failures. The reason is
`stop rule`, `max reached`, `single run`, or `user` (only when a reply asked
to stop). Pictures counts the pairs a commit carries, `0` for one with
`UX-Pictures: none`. Size each table column from its longest cell before
writing the table. A drop's reason is the failing check or "dropped by the
user". Omit an empty section.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/ux/improve.md` (pass `~` as is,
the file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable. A missing file needs no comment. On a correction or self-caught
mistake, append a one-line rule — general, naming nothing from the project at
hand (its files, tests, tickets) — to the sibling when this directory is
writable, else to the fallback, creating it, and report where.
