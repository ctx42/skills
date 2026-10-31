// eval-guard.mjs — keeps a shell-run case out of the real home.
//
// eval-shell.mjs points $HOME at the case workspace, but an agent can still
// name an absolute path in the real home. denyHomeEdits makes the CLI refuse
// such edits; homeWrites and homeCommands find any edit or Bash call that got
// through, so the case fails instead of passing silently.
import path from "node:path";

const EDITS = { Write: "file_path", Edit: "file_path", NotebookEdit: "notebook_path" };

function inside(p, dir) {
  const rel = path.relative(dir, p);
  return rel === "" || (!rel.startsWith("..") && !path.isAbsolute(rel));
}

// denyHomeEdits returns the `claude` flags that refuse every file edit under
// realHome, or none when the workspace itself lies there.
export function denyHomeEdits(realHome, workspace) {
  if (inside(workspace, realHome)) return [];
  return ["--disallowedTools", `Edit(/${realHome}/**)`];
}

// calls returns the tool_use blocks of the trace events whose result came back
// without an error, in order.
function calls(events) {
  const uses = [], ok = new Set();
  for (const e of events) {
    for (const b of e?.message?.content || []) {
      if (e.type === "assistant" && b.type === "tool_use") uses.push(b);
      if (e.type === "user" && b.type === "tool_result" && !b.is_error) ok.add(b.tool_use_id);
    }
  }
  return uses.filter((u) => ok.has(u.id));
}

// homeWrites returns the paths under realHome, outside workspace, that a
// file-edit tool call in the trace events wrote: only calls whose result came
// back without an error count. Relative and `~` paths resolve inside the
// workspace, so they never count.
export function homeWrites(events, realHome, workspace) {
  return calls(events).filter((u) => EDITS[u.name]).map((u) => u.input?.[EDITS[u.name]])
    .filter((p) => typeof p === "string" && path.isAbsolute(p) && inside(p, realHome) && !inside(p, workspace));
}

// homeCommands returns the Bash commands in the trace events that name
// realHome as a path and came back without an error.
export function homeCommands(events, realHome) {
  const named = new RegExp(`${realHome.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}(?![^/\\s'"])`);
  return calls(events).filter((u) => u.name === "Bash").map((u) => u.input?.command)
    .filter((c) => typeof c === "string" && named.test(c));
}
