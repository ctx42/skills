# Lessons

Rules learned for the `skill-smith` skill. Read before running; obey each line.

- Before choosing where a skill persists user data, grep the repo for an
  existing storage convention and reuse it instead of inventing a path.
- For skills that persist data, design for read-only installs: write to a
  `$HOME`-rooted store outside the plugin dir, not just report it's read-only.
- When mapping a namespace onto filenames, use nested subdirectories
  (`ns/name`), not a flattened separator like a double underscore.
- When the user supplies a skill or file name, flag a likely typo and confirm
  the spelling before creating files.
