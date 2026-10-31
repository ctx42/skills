// eval-graders.mjs — what a native case's grader can prove.
//
// A case passes when every grader passes, so a case whose graders only say
// what must not happen passes on an empty reply. And a `tool_used` grader
// with `max: 0` only bites when the run may call that tool at all.

// asserts reports whether grader g (its frontmatter fields: type, match,
// min, max, exists) checks that something happened, not only that something
// did not.
export function asserts(g) {
  if (g.type === "regex") {
    const m = g.match || "contains";
    return m !== "not_contains" && m !== "count:0";
  }
  if (g.type === "tool_used") {
    const min = g.min === undefined ? 1 : Number(g.min);
    return min >= 1 && !(g.max !== undefined && Number(g.max) === 0);
  }
  if (g.type === "file_exists") return String(g.exists) !== "false";
  return true;
}

// canUse reports whether a run of the case may call tool: the case's
// allowed_tools grant it (by name, `Bash(git:*)` grants Bash), it is a
// mocked MCP tool (allowed on its own), or the case is plain (not
// needs-shell), whose runs eval-changed.sh also grants Write, Edit, and LSP.
export function canUse(tool, allowed, shell) {
  const name = tool.split("(")[0];
  if (name.startsWith("mcp__")) return true;
  if (allowed.some((a) => a.split("(")[0] === name)) return true;
  return !shell && ["Write", "Edit", "LSP"].includes(name);
}
