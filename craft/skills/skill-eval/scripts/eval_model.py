"""Names the model a `claude -p` run used.

A result event's modelUsage maps each model ID the session called to its
usage. The CLI may also call a cheap helper model, so the session's own model
is the one that cost the most.
"""


def main_model(usage):
    """Return the model ID with the highest costUSD in usage (a result
    event's modelUsage), or None when usage is missing or empty."""
    best, cost = None, -1.0
    for mid, u in (usage or {}).items():
        c = (u or {}).get("costUSD") or 0
        if c > cost:
            best, cost = mid, c
    return best
