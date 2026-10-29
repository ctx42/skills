# Focus

What a focus does to a run (SKILL.md section 4).

A focus — any text after the keywords — names a part of the UI or shows it in a
screenshot, with what the user wants; one naming only a part measures that part.
The description is an instruction. It beats a `PERF:` comment, which the same
commit removes, its body saying so. It may require a visible change it names
explicitly (pagination, virtualization, a debounce), which then carries picture
pairs ([focus-pictures.md](focus-pictures.md)). The instruction is the run's
first change; with `loop`, the run then keeps improving that part by the normal
rules. With a focus, no commit touches code outside the focused part and what
serves it; a fix that would goes to Recommendations.
