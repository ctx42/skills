# Focus pictures

Picture pairs for a visible change a focus names (SKILL.md section 4). No
other change writes into `dev/perf/`.

1. Before any edit (SKILL.md section 6, step 2), delete every untracked
   `dev/perf/*.png`. One pair is `dev/perf/before.png` and
   `dev/perf/after.png`; several are `before-1.png` and `after-1.png` on,
   numbered as in the message.
2. Instead of the visible-change check (step 6), shoot its pictures, after
   first: per touched view, scroll to the first element the change adds (a
   pager, a placeholder, a "load more" button), else to where it removed
   content, and `take_screenshot` with `filePath`; then
   `git stash push -u -- <the change's files>`, reload, shoot `before` at the
   same scroll, and `git stash pop`.
