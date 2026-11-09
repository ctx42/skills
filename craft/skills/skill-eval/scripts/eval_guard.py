"""Keeps a shell-run case out of the real home.

eval-shell points $HOME at the case workspace, but an agent can still name an
absolute path in the real home. deny_home_edits makes the CLI refuse such
edits; home_writes and home_commands find any edit or Bash call that got
through, so the case fails instead of passing silently.
"""
import os
import re

EDITS = {"Write": "file_path", "Edit": "file_path", "NotebookEdit": "notebook_path"}


def _inside(p, d):
    rel = os.path.relpath(p, d)
    return rel == "." or not (rel == ".." or rel.startswith(".." + os.sep))


def deny_home_edits(real_home, workspace):
    """Return the `claude` flags that refuse every file edit under real_home,
    or none when the workspace itself lies there."""
    if _inside(workspace, real_home):
        return []
    return ["--disallowedTools", f"Edit(/{real_home}/**)"]


def _calls(events):
    """Return the tool_use blocks of the trace events whose result came back
    without an error, in order."""
    uses, ok = [], set()
    for e in events:
        for b in ((e or {}).get("message") or {}).get("content") or []:
            if not isinstance(b, dict):
                continue
            if e.get("type") == "assistant" and b.get("type") == "tool_use":
                uses.append(b)
            if e.get("type") == "user" and b.get("type") == "tool_result" and not b.get("is_error"):
                ok.add(b.get("tool_use_id"))
    return [u for u in uses if u.get("id") in ok]


def home_writes(events, real_home, workspace):
    """Return the paths under real_home, outside workspace, that a file-edit
    tool call in the trace events wrote: only calls whose result came back
    without an error count. Relative and `~` paths resolve inside the
    workspace, so they never count."""
    paths = [(u.get("input") or {}).get(EDITS[u["name"]])
             for u in _calls(events) if u.get("name") in EDITS]
    return [p for p in paths if isinstance(p, str) and os.path.isabs(p)
            and _inside(p, real_home) and not _inside(p, workspace)]


def home_commands(events, real_home):
    """Return the Bash commands in the trace events that name real_home as a
    path and came back without an error."""
    named = re.compile(re.escape(real_home) + r"(?![^/\s'\"])")
    cmds = [(u.get("input") or {}).get("command") for u in _calls(events) if u.get("name") == "Bash"]
    return [c for c in cmds if isinstance(c, str) and named.search(c)]
