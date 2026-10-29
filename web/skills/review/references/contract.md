# review API contract

Read in Check mode when the API contract is in scope. The frontend's types for
server answers are written by hand; this check holds them to the JSON the Go
server in the same repository actually sends. Findings use the dimension
`api-contract`.

## Out of reach

No Go code in the repository serves the client's paths (an external API, a
proxy that forwards bodies untouched): say so in one line and skip the check.
Never guess a server's shape from the frontend alone.

## Pairing

1. In the API client module (the one module that calls `fetch`), list every
   exported function with the method and path it requests and the type it
   returns, following the response through any normalizer to the interface
   the app uses.
2. For each, find the Go handler serving that method and path — the mux
   pattern (`"GET /api/devices/{id}"`), a router call, or a proxy rule — and
   follow it to the value it encodes (`json.NewEncoder(w).Encode(v)`, a
   `write(w, status, v)` helper), through any envelope type (`{data: [...]}`)
   and conversion function (`toDevice`).
3. A path the client requests that no handler serves is a Blocker.

## Comparing

Compare the encoded Go type with the TS type field by field, both ways:

- Name: the `json` tag's name, else the Go field name; `json:"-"` is never
  sent; an embedded struct's fields sit at the outer level.
- Presence: `omitempty`/`omitzero` means the field may be missing; a pointer,
  slice, or map without them may be `null` (a nil slice encodes as `null`,
  not `[]`).
- Type: `string` → string; integer and float kinds → number; `bool` →
  boolean; `time.Time` → an RFC 3339 string; a `json:",string"` option → a
  string; a map → `Record<string, …>`; a type with `MarshalJSON` →
  whatever that method writes, read it.

Report:

- A field the TS type declares that the server never sends under that name (a
  rename on either side), or sends as another JSON type: Blocker when the app
  reads it — a normalizer that silently defaults the missing value still
  shows a wrong one — else Should-fix.
- A field the server may omit or send as `null` that the TS type declares as
  always present: Should-fix when every read is guarded or normalized, or
  shows the missing value as it would an empty one; Blocker when a read
  throws or shows a wrong value.
- A field the server sends that the TS type does not declare: Nit when the
  frontend reads it anyway (through a cast, an index, or a raw body);
  otherwise nothing.
- Request side: a query parameter, path segment, or body field the client
  sends that the handler never reads, or reads under another name: Blocker.

Each finding cites both sides — the TS field at its `file:line` and the Go
field or tag at its `file:line` — and the fix says which side changes. A type
that matches field for field yields nothing; never list a match.
