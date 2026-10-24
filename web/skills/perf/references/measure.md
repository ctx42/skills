# Measuring

How to take each number `perf` acts on. Every capture, trace, snapshot, and
build goes to the run's scratch directory, never into the tree.

## Contents

- [Setup](#setup)
- [Interactions and long tasks](#interactions-and-long-tasks)
- [Layout shift](#layout-shift)
- [Leaks](#leaks)
- [Network](#network)
- [Bundle](#bundle)
- [Visible-change check](#visible-change-check)

## Setup

Before each series: `emulate` with `cpuThrottlingRate: 4` and nothing else
(no `networkConditions`); repeat it after any other `emulate` call, since each
call replaces all settings. Install the observers with `navigate_page`'s
`initScript`, so they see the page from its first script:

```js
window.__perf = { events: [], long: [], shift: 0 };
new PerformanceObserver((l) => { for (const e of l.getEntries()) if (e.interactionId) __perf.events.push(e.duration); })
  .observe({ type: "event", durationThreshold: 16 });
new PerformanceObserver((l) => { for (const e of l.getEntries()) __perf.long.push(e.duration); })
  .observe({ type: "longtask" });
new PerformanceObserver((l) => { for (const e of l.getEntries()) if (!e.hadRecentInput) __perf.shift += e.value; })
  .observe({ type: "layout-shift" });
```

Reset between samples with `evaluate_script`:
`() => { __perf.events = []; __perf.long = []; __perf.shift = 0; }`. Read a
sample once the page is quiet — 500 ms after the last DOM change:

```js
async () => {
  await new Promise((r) => setTimeout(r, 500));
  return { inp: Math.max(0, ...__perf.events), longTask: Math.max(0, ...__perf.long), cls: __perf.shift };
}
```

A sample is one value; a series is 5 samples of the same action from the same
state, and its median is the measurement. Put the state back between samples
(reload, or undo the action: clear the search, sort back) so every sample
starts alike.

## Interactions and long tasks

Drive each interaction with the input tools (`click`, `fill`, `press_key`),
never with `evaluate_script` — synthetic events carry no `interactionId`.
`inp` is the slowest interaction in the sample; `longTask` the longest task
during it. A view's load is a sample too: navigate to it (a full load, or the
app's own link for a client-side route) and read `longTask`.

A finding needs the cause before the fix: take `performance_start_trace`
(`reload: false`, `autoStop: false`), repeat the action once,
`performance_stop_trace`, and read the insights it lists
(`performance_analyze_insight`) — forced reflow, long script, render-blocking
work — down to the function in the source.

## Layout shift

Load the view fresh (`navigate_page` with `ignoreCache: true`), wait for the
network to go quiet, read `cls`. The trace's `CLSCulprits` insight names the
shifting element.

## Leaks

Per view: load it, then 5 times navigate to another view and back by the
app's own navigation. After the first visit and after each return,
`take_heapsnapshot` (it forces a full GC first) to
`<scratch>/heap-<view>-<n>.heapsnapshot` and read its object count:

```bash
head -c 65536 <file> | grep -o '"node_count":[0-9]*'
```

A leak: the count rises at each of the 5 steps after the first snapshot. The
cause is in the last snapshot: compare it with the first by constructor
(detached `HTMLElement`s, closures held by a listener or timer) and find the
code that adds without removing. A fix's after series repeats the 5 cycles; the
measurement is the growth from first to last snapshot.

## Network

`list_network_requests` with `resourceTypes: ["fetch", "xhr"]` after a view
loads, and after every action while playing:

- A write: any `POST`, `PUT`, `PATCH`, or `DELETE` outside a flow the focus
  names. Stop using that control (SKILL.md section 2).
- Duplicate: the same method and URL twice in one view's load.
- Sequential: from
  `performance.getEntriesByType("resource").filter((e) => ["fetch", "xmlhttprequest"].includes(e.initiatorType))`,
  a request whose `startTime` is after another's `responseEnd`. It is a
  finding only when the code shows the later request uses nothing from the
  earlier response.

A counted metric is the request count of the view's load. An API call's
latency, for the proof of a back-end change, is its `responseEnd - startTime`,
as a series of 5.

## Bundle

Run the build into `<scratch>/build-<n>` (start step 7). The first-load bundle
is every script and stylesheet the built entry HTML references, as
`<script src>`, `<link rel="modulepreload">`, or `<link rel="stylesheet">`,
plus their static imports. Its size, the counted metric, is the sum of
`gzip -9c <file> | wc -c` over those files.

- Lazy candidate: a route's component, or a library only one deep view uses,
  imported statically into a first-load chunk — the router or the view's
  import in the source shows it.
- Whole import: `import x from "<lib>"` or `import * as x from "<lib>"` of a
  library whose `package.json` `exports` offers per-function subpaths, or whose
  default export defeats tree-shaking.

## Visible-change check

Proves a change leaves what the user sees unchanged. A capture is this
signature of the settled view, saved with `evaluate_script`'s `filePath`:

```js
() => [...document.querySelectorAll("body *")].flatMap((el) => {
  const r = el.getBoundingClientRect(), s = getComputedStyle(el);
  if ((!r.width && !r.height) || s.visibility === "hidden" || +s.opacity === 0) return [];
  const text = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent.trim()).join(" ");
  return [[el.tagName, Math.round(r.x), Math.round(r.y + scrollY), Math.round(r.width), Math.round(r.height), s.color, s.backgroundColor, text].join("|")];
}).join("\n")
```

Settled means loaded, network quiet, scrolled to the top, then — for a view
reached by an interaction — after that interaction. Take two before captures,
reloading between them, then the after capture the same way:

```bash
python3 -I - <scratch>/b1 <scratch>/b2 <scratch>/a <<'EOF'
import sys
b1, b2, a = (open(p).read().split("\n") for p in sys.argv[1:])
if len(a) != len(b1): sys.exit(f"line count {len(b1)} -> {len(a)}")
bad = [i for i, (x, y, z) in enumerate(zip(b1, b2, a)) if x == y and x != z]
sys.exit(f"changed: {[a[i] for i in bad[:5]]}" if bad else 0)
EOF
```

A line that differs between the two before captures is volatile (a relative
time, live data) and masked; exit 0 means unchanged. A count that differs
between the two before captures (live data adds rows) leaves the view
unprovable: a change touching it goes to Recommendations, and the view under
Not measured.
