# reshape change catalog

Archetype detail for `SKILL.md`'s brainstorm list: when the friction shows, the
API shape that removes it, and a compact Go before/after. Consult the entry for
the archetype you're drafting; don't preload the file. Ordered as in the body.

## Contents

- options-constructor
- default-away-a-param
- absorb-the-sequence
- batch-or-variadic
- iterator
- result-type
- sentinel-error
- expose-the-interface
- testing-helper
- builder
- split-the-god-func
- invert-control
- generics
- move-responsibility-upstream
- shed-a-leaky-return

## options-constructor

When: call sites build a config struct inline or pass a long positional param
list, most fields left at defaults.
Change: `New(required, ...Option)` with `WithX` options; defaults live in the
constructor.

```go
// before — consumer fills a struct every time:
c := lib.New(lib.Config{Host: h, Timeout: 30 * time.Second, Retries: 3})
// after — required arg + only the deviations:
c := lib.New(h, lib.WithTimeout(30*time.Second))
```

## default-away-a-param

When: every call site passes the same value for a parameter, or a nil/empty the
library could treat as a default.
Change: make the zero value meaningful, or add a defaulted form; drop the arg
from the common path.

```go
// before: lib.Encode(v, lib.DefaultIndent)  // always DefaultIndent
// after:  lib.Encode(v)                      // zero indent == DefaultIndent
```

## absorb-the-sequence

When: the same 3–5 line dance around a library call repeats at many sites (open
→ check → defer close → read).
Change: ship the sequence as one library call that returns the end value.

```go
// before: f, err := lib.Open(p); if err != nil {...}; defer f.Close(); b, err := io.ReadAll(f)
// after:  b, err := lib.ReadFile(p)
```

## batch-or-variadic

When: the consumer loops just to call a single-item API.
Change: add a batch/variadic form that takes the slice and loops internally.

```go
// before: for _, id := range ids { lib.Add(id) }
// after:  lib.Add(ids...)
```

## iterator

When: the consumer drives a cursor/index or a `Next()`/`Err()` pair by hand.
Change: expose a range-over-func (`iter.Seq`/`iter.Seq2`).

```go
// before: it := lib.Rows(); for it.Next() { r := it.Row(); ... }; if it.Err() != nil {...}
// after:  for r, err := range lib.Rows() { ... }   // Seq2 carries the error
```

## result-type

When: a function returns an awkward multi-value tuple the consumer must re-bundle,
or positional booleans whose meaning isn't obvious at the call.
Change: return a small named struct with named fields.

```go
// before: host, port, ok, secure := lib.Parse(s)
// after:  r := lib.Parse(s); use r.Host, r.Port, r.OK
```

## sentinel-error

When: the consumer matches on error strings or asserts concrete error types.
Change: export `ErrXxx` sentinels (or typed errors) and support `errors.Is`/`As`.

```go
// before: if strings.Contains(err.Error(), "not found") {...}
// after:  if errors.Is(err, lib.ErrNotFound) {...}
```

## expose-the-interface

When: the consumer declares an interface only to name the library's own method
set — for mocking, or to narrow what it depends on.
Change: the library exports that interface; consumers reference it instead of
re-deriving it. Watch the No-name-stutter contract when they mirror it for a
compile-time assertion.

## testing-helper

When: consumers hand-roll fakes, spies, or fixture setup for the library in their
tests.
Change: ship a `libtest` subpackage or a `Spy`/`Fake`/helper the library owns.

```go
// before: each consumer writes a stub implementing lib.Client
// after:  libtest.NewSpy() returns a ready spy
```

## builder

When: configuration happens in ordered stages the consumer wires inline, or a
call needs many optional refinements that read poorly as flat options.
Change: a fluent builder — `lib.Build().WithX().WithY().Do()`.

## split-the-god-func

When: the consumer sets a mode flag/bool and the library branches on it, and call
sites always know their mode statically.
Change: split into mode-specific functions.

```go
// before: lib.Fetch(url, true /* stream */)
// after:  lib.FetchStream(url)   // plus lib.Fetch(url)
```

## invert-control

When: the consumer orchestrates a multi-step protocol the library exposes as raw
steps, or duplicates a loop the library could run itself.
Change: accept a callback / handler, or return the finished value, so the library
owns the orchestration.

```go
// before: consumer opens, iterates, aggregates, closes
// after:  lib.Walk(root, func(e Entry) error {...})
```

## generics

When: the consumer casts `any`/`interface{}` results, or duplicates the same
logic per type around a non-generic API.
Change: a type-parameterized function/type removes the assertions.

```go
// before: v := lib.Get(k).(User)
// after:  v := lib.Get[User](k)
```

## move-responsibility-upstream

When: several consumers reimplement the same logic on top of the library — retry,
pagination, normalization, config loading — because the library stops one step
short.
Change: the library absorbs that responsibility as a first-class API. The boldest
archetype; justify it by the count of consumers duplicating the work.

## shed-a-leaky-return

When: a function returns an `error` that can never be non-nil at the call site
(everyone drops it with `_`), or bakes presentation (a trailing newline, padding)
into a returned value that consumers strip.
Change: drop the impossible error (return only the value), or return the clean
value and leave presentation to the caller.

```go
// before: s, _ := lib.Name()   // error never occurs; every caller drops it
// after:  s := lib.Name()
```
