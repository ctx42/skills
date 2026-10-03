# Lessons

- Check `lines-fit-limit` by measuring every line in characters (not bytes — `awk length` counts a UTF-8 em-dash as 3) with tabs expanded to the tab width, in a read-only pass, not a formatter; a read-through missed 20+ over-limit lines in one package.
