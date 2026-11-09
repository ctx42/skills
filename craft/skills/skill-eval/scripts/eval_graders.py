"""What a native case's grader can prove.

A case passes when every grader passes, so a case whose graders only say what
must not happen passes on an empty reply. And a `tool_used` grader with
`max: 0` only bites when the run may call that tool at all.
"""


def asserts(g):
    """Report whether grader g (its front matter fields: type, match, min,
    max, exists) checks that something happened, not only that something
    did not."""
    if g.get("type") == "regex":
        return (g.get("match") or "contains") not in ("not_contains", "count:0")
    if g.get("type") == "tool_used":
        lo = int(g["min"]) if g.get("min") is not None else 1
        return lo >= 1 and not (g.get("max") is not None and int(g["max"]) == 0)
    if g.get("type") == "file_exists":
        return str(g.get("exists")).lower() != "false"
    return True


def can_use(tool, allowed, shell):
    """Report whether a run of the case may call tool: the case's
    allowed_tools grant it (by name, `Bash(git:*)` grants Bash), it is a mocked
    MCP tool (allowed on its own), or the case is plain (not needs-shell),
    whose runs eval-changed also grants Write, Edit, and LSP."""
    name = tool.split("(")[0]
    if name.startswith("mcp__"):
        return True
    if any(a.split("(")[0] == name for a in allowed):
        return True
    return not shell and name in ("Write", "Edit", "LSP")
