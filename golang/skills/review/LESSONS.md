# review — lessons

- Never "improve" a `"" + "line\n"` multi-line string into a backtick raw
  string; the `"" +` segmented form is the required style (raw strings break
  indentation, existing rule) — leave it.
