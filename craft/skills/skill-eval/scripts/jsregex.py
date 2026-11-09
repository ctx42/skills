"""Read JavaScript grader regexes in Python, the way JavaScript reads them.

Grader patterns are JavaScript regexes, because `claude plugin eval` runs them
in JavaScript. Python's `re` reads some of the same syntax differently, so
compile() rewrites those parts, and check() refuses what it cannot rewrite.
The patterns this accepts form the subset both engines read alike:

- `\\d`, `\\w`, `\\b`, `\\B` are ASCII-only, as in JavaScript without the `u`
  flag; Python stays in Unicode mode, so the `i` flag still folds `É` to `é`.
- `.` (without `s`) and `^`, `$` (with `m`) treat `\\r`, U+2028, and U+2029
  as line ends too; `$` without `m` matches only at the very end.
- `(?<name>` and `\\k<name>` become Python's `(?P<name>` and `(?P=name)`.
- `[`, `&&`, `~~`, `||` inside a class are literal, as in JavaScript.

Refused: flags other than i, m, s; `\\p{`, `\\P{`, `\\u{`; the anchors `\\A`,
`\\Z`, `\\z`; `[]` and `[^]`; `{,n}`; `(?P`, `(?>`, inline flags; possessive
quantifiers; `\\D`, `\\W` inside a class; and anything Python cannot compile,
such as a lookbehind of varying width.

Left as Python reads it: `\\s` and `\\S`. They differ from JavaScript only on
U+001C–U+001F, U+0085, and U+FEFF, which grader targets do not contain.
"""
import re
import warnings

FLAGS = {"i": re.I, "m": re.M, "s": re.S}

WORD = "A-Za-z0-9_"
EOL = "\\n\\r\\u2028\\u2029"
OUTSIDE = {  # escapes rewritten outside a character class
    "d": "[0-9]",
    "D": "[^0-9]",
    "w": f"[{WORD}]",
    "W": f"[^{WORD}]",
    "b": f"(?:(?<=[{WORD}])(?![{WORD}])|(?<![{WORD}])(?=[{WORD}]))",
    "B": f"(?:(?<=[{WORD}])(?=[{WORD}])|(?<![{WORD}])(?![{WORD}]))",
}
INSIDE = {"d": "0-9", "w": WORD}  # the same, inside a character class


def _translate(pattern, flags):
    """Return the Python pattern for a JavaScript one and the reasons it
    falls outside the shared subset."""
    out, why = [], [f"flag '{c}' is not supported" for c in flags if c not in FLAGS]
    i, n, in_class, quant = 0, len(pattern), False, False
    while i < n:
        c = pattern[i]
        nxt = pattern[i + 1:i + 2]
        if c == "\\":
            if not nxt:
                why.append("trailing backslash")
                break
            if nxt in "pPu" and pattern[i + 2:i + 3] == "{":
                why.append(f"\\{nxt}{{ is not supported")
            elif nxt in "AZz":
                why.append(f"anchor \\{nxt} is not JavaScript")
            if nxt == "k" and pattern[i + 2:i + 3] == "<":
                end = pattern.find(">", i + 3)
                if end < 0:
                    why.append("\\k< has no closing >")
                    break
                out.append(f"(?P={pattern[i + 3:end]})")
                i, quant = end + 1, False
                continue
            if in_class:
                if nxt in "DW":
                    why.append(f"\\{nxt} inside [] is not supported")
                out.append(INSIDE.get(nxt, c + nxt))
            else:
                out.append(OUTSIDE.get(nxt, c + nxt))
            i, quant = i + 2, False
            continue
        if in_class:
            if c == "]":
                in_class = False
            elif c == "[" or (c in "&~|" and nxt == c):
                out.append("\\")
            out.append(c)
            i += 1
            continue
        if c == "[":
            rest = pattern[i + 1:i + 3]
            if rest.startswith("]"):
                why.append("empty class [] never matches in JavaScript")
            elif rest == "^]":
                why.append("[^] is not supported")
            in_class, quant = True, False
            out.append(c)
            if rest.startswith("^"):
                out.append("^")
                i += 1
            i += 1
            continue
        if c == "(" and nxt == "?":
            kind = pattern[i + 2:i + 3]
            if kind == "<" and pattern[i + 3:i + 4] not in ("=", "!"):
                out.append("(?P<")
                i, quant = i + 3, False
                continue
            if kind == "P":
                why.append("(?P is Python syntax")
            elif kind == ">":
                why.append("atomic group (?> is not JavaScript")
            elif kind not in (":", "=", "!", "<"):
                why.append("inline flag groups are not supported")
        if c == "{" and re.match(r"\{,\d", pattern[i:]):
            why.append("{,n} is literal in JavaScript but a quantifier in Python")
        if c == "+" and quant:
            why.append("possessive quantifier is not JavaScript")
        if c == ".":
            out.append("." if "s" in flags else f"[^{EOL}]")
        elif c == "^":
            out.append(f"(?<![^{EOL}])" if "m" in flags else "^")
        elif c == "$":
            out.append(f"(?![^{EOL}])" if "m" in flags else "\\Z")
        else:
            out.append(c)
        if c in "*+?":
            quant = c != "?" or not quant  # a ? after a quantifier makes it lazy
        else:
            quant = c == "}" and bool(re.search(r"\{\d+(,\d*)?\}$", pattern[:i + 1]))
        i += 1
    return "".join(out), why


def _flags(flags):
    f = 0
    for c in flags:
        f |= FLAGS.get(c, 0)
    return f


def check(pattern, flags=""):
    """Return why pattern, a JavaScript regex with flags, falls outside the
    subset Python reads alike; an empty list when it is inside. Never raises."""
    py, why = _translate(pattern, flags)
    if why:
        return why
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            re.compile(py, _flags(flags))
    except (re.error, FutureWarning) as e:
        return [f"does not compile in Python: {e}"]
    return []


def compile(pattern, flags=""):  # noqa: A001 - mirrors re.compile
    """Return a Python regex that matches what the JavaScript pattern with
    flags matches; use search() for JavaScript's test(). Raises ValueError
    with the check() reasons for a pattern outside the subset."""
    why = check(pattern, flags)
    if why:
        raise ValueError("; ".join(why))
    py, _ = _translate(pattern, flags)
    return re.compile(py, _flags(flags))

