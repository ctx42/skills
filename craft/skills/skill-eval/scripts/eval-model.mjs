// eval-model.mjs — names the model a `claude -p` run used.
//
// A result event's modelUsage maps each model ID the session called to its
// usage. The CLI may also call a cheap helper model, so the session's own
// model is the one that cost the most.

// mainModel returns the model ID with the highest costUSD in usage (a
// result event's modelUsage), or null when usage is missing or empty.
export function mainModel(usage) {
  let best = null, cost = -1;
  for (const [id, u] of Object.entries(usage || {})) {
    if ((u?.costUSD || 0) > cost) { best = id; cost = u?.costUSD || 0; }
  }
  return best;
}
