#!/usr/bin/env python3
"""Generate craft/evals/doc-smith--* native eval cases. Rewrites only doc-smith--*."""
import glob, json, os, re, shutil, textwrap, uuid

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
EVALS = os.path.join(ROOT, "craft/evals")

ENGLISH = "The user writes English; reply in English."
SCRIPTED = """Automated eval: the user is absent. Whenever the skill would stop and wait
for the user, take the next scripted answer below as the reply and continue
in this same run; never end the run to wait. If none fits, give the most
plausible answer and continue.
Before taking a scripted answer, write out in full, as your reply text, the
message you would send the user at that point.
"""
BASE = ["skill:doc-smith", "sec:doc-smith:usage", "sec:doc-smith:whole-document-pass-all-modes",
        "sec:doc-smith:self-learning", "ref:doc-smith/writing-guide"]
CLAIMS = "sec:doc-smith:technical-claims-flag-don-t-fix"
PROOF = "sec:doc-smith:proof-mode"
CREATE = "sec:doc-smith:create-mode"
REVISE = "sec:doc-smith:revise-mode"
SID = "7c1d9a52-3e4b-4f6a-8d2c-1b5e9f0a7c33"
NOTICE = "Ignore any trailing policy notice or notice about documents needing approval. "


def history(turns):
    lines, parent, minute = [], None, 0
    for role, text in turns:
        minute += 1
        u = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{SID}/{minute}/{text}"))
        rec = {"parentUuid": parent, "isSidechain": False, "userType": "external",
               "cwd": "/work/project", "sessionId": SID, "version": "2.1.288",
               "type": role, "uuid": u, "timestamp": f"2026-10-01T10:{minute:02d}:00.000Z"}
        if role == "user":
            rec["message"] = {"role": "user", "content": text}
        else:
            rec["message"] = {"id": "msg_" + u.replace("-", "")[:24], "type": "message",
                              "role": "assistant", "model": "claude-opus-5-5",
                              "content": [{"type": "text", "text": text}],
                              "stop_reason": "end_turn", "stop_sequence": None,
                              "usage": {"input_tokens": 10, "output_tokens": 10}}
        lines.append(json.dumps(rec))
        parent = u
    return "\n".join(lines) + "\n"


def grader(kind, body, **fm):
    out = ["---", f"type: {kind}"] + [f"{k}: {v}" for k, v in fm.items()] + ["---", body]
    return "\n".join(out) + "\n"


def last(body, match=None, flags=None):
    fm = {"target": "last_message"}
    if match:
        fm["match"] = json.dumps(match)
    if flags:
        fm["flags"] = json.dumps(flags)
    return grader("regex", body, **fm)


def infile(path, body, match=None, flags=None):
    fm = {"target": "{source: file, path: %s}" % path}
    if match:
        fm["match"] = json.dumps(match)
    if flags:
        fm["flags"] = json.dumps(flags)
    return grader("regex", body, **fm)


def llm(claim):
    return grader("llm", NOTICE + claim, focus="last_message")


def exists(path, yes=True):
    return "---\ntype: file_exists\npath: %s\nexists: %s\n---\n" % (path, "true" if yes else "false")


NO_WRITE = "---\ntype: tool_used\ntool: Write\nmin: 0\nmax: 0\narm: both\n---\n"
NO_EDIT = "---\ntype: tool_used\ntool: Edit\nmin: 0\nmax: 0\narm: both\n---\n"


def words(s):
    """Pattern matching the sentence with any whitespace between words."""
    return r"\s+".join(re.escape(w) for w in s.split())


def lines_of(doc, needle):
    return [i + 1 for i, l in enumerate(doc.split("\n")) if needle in l]


OVERVIEW = r"^#[^#\n][^\n]*\n\s*(?:[^#\s][^\n]*\n|## [^\n]*(?:overview|about|introduction|what)[^\n]*\n)"


def lineref(nums):
    alt = "|".join(str(n) for n in sorted(set(nums)))
    # A list counts: "lines 5–7 vs 27, 39, 45" or "L5–7 vs. L27, L39" cites 27 too.
    return r"(?:\blines?\s*|\bL|\.md:)(?:[\d\s,–-]|\bvs\b\.?|\band\b|\bL(?=\d)){0,40}?(?<!\d)(?:%s)\b" % alt


def scaffold(files):
    out = ["#!/usr/bin/env bash", "set -euo pipefail"]
    for i, (path, body) in enumerate(files.items()):
        d = os.path.dirname(path)
        if d:
            out.append(f"mkdir -p {d}")
        tag = f"EOF_{i}"
        out.append(f"cat > {path} <<'{tag}'")
        out.append(body.rstrip("\n"))
        out.append(tag)
    return "\n".join(out) + "\n"


def write_case(name, tags, query, graders, files=None, hist=None, answers=None,
               max_turns=40, timeout=240, tools=None):
    d = os.path.join(EVALS, name)
    os.makedirs(os.path.join(d, "graders"))
    tools = tools or ["Read", "Glob", "Grep", "Skill", "Write", "Edit"]
    asp = ENGLISH + "\n"
    if answers:
        asp += SCRIPTED + "\n" + "".join(f"{i}. {a}\n" for i, a in enumerate(answers, 1))
    asp_block = "".join("  " + l + "\n" if l else "\n" for l in asp.rstrip("\n").split("\n"))
    fm = (f"---\ntags: [case:{name}, " + ", ".join(tags) + "]\nruns: 1\n"
          f"max_turns: {max_turns}\ntimeout_seconds: {timeout}\n"
          f"allowed_tools: [{', '.join(tools)}]\nappend_system_prompt: |\n{asp_block}---\n\n{query}\n")
    open(os.path.join(d, "prompt.md"), "w").write(fm)
    if files or hist:
        ctx = []
        if files:
            ctx.append("  scaffold_script: scaffold.sh")
            p = os.path.join(d, "scaffold.sh")
            open(p, "w").write(scaffold(files))
            os.chmod(p, 0o755)
        if hist:
            ctx.append("  history_file: history.jsonl")
            open(os.path.join(d, "history.jsonl"), "w").write(history(hist))
        open(os.path.join(d, "case.yaml"), "w").write(
            f'schema_version: "1.1"\nname: {name}\ncontext:\n' + "\n".join(ctx) + "\n")
    for gname, body in graders.items():
        open(os.path.join(d, "graders", gname + ".md"), "w").write(body)


def blocker_has(*parts):
    stop = r"(?:(?!Should[- ]?fix)[\s\S])*?"
    return r"Blockers?\b" + "".join(f"(?={stop}(?:{p}))" for p in parts)


def numbered_groups():
    return {
        "b4-groups-in-order": last(r"Blockers?\b[\s\S]*Should[- ]?fix[\s\S]*\bNits?\b", flags="i"),
        "b4-numbered": last(r"^\s*(?:[-*]\s+)?(?:\*\*)?\d+[.)]", flags="m"),
        "b4-numbering-runs-on": last(
            r"Should[- ]?fix[^\n]*\n(?:\s*\n)*\s*(?:[-*]\s+)?(?:\*\*)?1[.)]", match="not_contains", flags="i"),
    }


# ---------------------------------------------------------------- 1
MANUAL_ACME = """# Acme User Manual

## Overview

Acme is a hosted web platform for planning maintenance work on water
networks. Your work orders, crews, and schedules are stored on Acme's
servers, so everyone on your team sees the same plan.

## Signing in

To sign in, open the address your administrator sent you and enter your
email address and password. After three failed attempts, your account is
locked for 15 minutes.

## Creating a work order

To create a work order, follow these steps.

1. Select **New work order** on the dashboard.
2. Enter a title and choose the asset that needs work.
3. Select **Save**.

The work order appears in the backlog of the crew you assigned it to.

## System requirements

Acme runs entirely in your web browser. You need a current version of
Chrome, Firefox, or Edge, and there is nothing to install.

## Assigning crews

To assign a crew, open a work order and choose a crew from the **Crew**
list. The crew lead receives an email with the details of the job.
Please note that you can simply reassign the work order later if plans
change.

## Working offline

Remember that Acme runs entirely in your web browser. When your
connection drops, Acme shows a banner and retries until it is back.

## Exporting schedules

To export a schedule, select **Export** on the schedule page and choose
CSV or PDF. Acme runs entirely in your web browser, so the file is saved
to your browser's download folder.
"""


def case1():
    host = lineref(range(5, 8))
    host_loc = r"Overview|" + host
    br = lines_of(MANUAL_ACME, "runs entirely in your web browser") + lines_of(MANUAL_ACME, "runs entirely in your web")
    br_loc = r"System requirements|Working offline|Exporting schedules|" + lineref(br)
    g = {
        "b0-no-write": NO_WRITE, "b0-no-edit": NO_EDIT,
        "b1-both-ends-cited-together": last(
            f"(?:{host_loc})[\\s\\S]{{0,400}}?(?:{br_loc})|(?:{br_loc})[\\s\\S]{{0,400}}?(?:{host_loc})", flags="i"),
        "b2-contradiction-is-blocker": last(blocker_has("hosted", "browser", host_loc, br_loc), flags="i"),
        "b3-repetition-flagged": last(r"repeat|repetit|redundan|restate|duplicat", flags="i"),
    }
    g.update(numbered_groups())


# ---------------------------------------------------------------- 2
API_GUIDE = """# Orders API Guide

## Overview

The Orders API lets your application create, read, and delete orders over
HTTPS. Every endpoint accepts and returns JSON. REST APIs are stateful by
design.

## Authentication

Each request needs an access token in the `Authorization` header. The
token expires after one hour, you must request a new one from the `/token`
end-point.

## Creating an order

To create an order, send a `POST` request to the `/orders` endpoint. The
request body names the product and the quantity, the response returns the
new order's ID.

## Reading an order

To read an order, send a `GET` request to the `/orders/{id}` end-point.
The client sends the order ID in the path, and then the order is looked up
by the server and returned with its current status.

## Rate limits

Each endpoint allows 100 requests per minute for each access token.
"""


def case2():
    p = "docs/api-guide.md"
    g = {
        "b1-splice-token-fixed": infile(p, r"one\s+hour,\s+you\s+must", match="not_contains"),
        "b1-splice-quantity-fixed": infile(p, r"quantity,\s+the\s+response", match="not_contains"),
        "b1-endpoint-one-spelling": infile(p, r"end-point", match="not_contains", flags="i"),
        "b1-subject-shift-fixed": infile(p, r"looked\s+up\s+by\s+the\s+server", match="not_contains"),
        "b2-claim-kept-in-file": infile(p, words("REST APIs are stateful by design")),
        "b2-raised-with-expectation": last(r"stateless", flags="i"),
        "b2-reason-given": last(
            r"stateless[^\n]{0,200}(no (session |client )?state|keeps? no|stores? no|each request|between requests|"
            r"self-contained|(does not|doesn't|never) (keep|store|remember|hold)|constraint|Fielding)", flags="i"),
        "b3-listed-for-decision": last(r"^\s*(?:[-*]|\d+[.)])[^\n]*stateful", flags="im"),
        "b4-no-invented-fact": infile(p, r"stateless", match="not_contains", flags="i"),
    }
    write_case("doc-smith--flag-dubious-claim", BASE + [PROOF, CLAIMS],
               "/craft:doc-smith proof docs/api-guide.md", g, files={p: API_GUIDE})


# ---------------------------------------------------------------- 3

NO_PASTE_PULSE = last(r"^#{1,3} Adding a logger\s*\n\s*\n?To add a logger|^Pulse Logger records pressure readings from field loggers and shows them\s*$",
                      match="not_contains", flags="m")


def case3():
    p = "docs/manual.md"
    gate = {
        "b0-no-write": NO_WRITE, "b0-no-edit": NO_EDIT,
        "b1-opens-with-scope": last(r"^\s*[^\n]*manual\.md"),
        "b2-no-narration": last(
            r"^\s*(?:[#*_>]\s*)*(let me|i'll|i will|i'm going to|now i|next,? i|first,? i|reading|i've read|i have read)\b",
            match="not_contains", flags="im"),
        "b3-no-closing-recap": last(
            r"^\s*(?:#+\s*|\*\*)(summary|recap|key findings|overview of findings)\b|\b(in summary|to summari[sz]e|in short)\b",
            match="not_contains", flags="im"),
        "b5-no-paste": NO_PASTE_PULSE,
    }
    full = {
        "b4-fixes-applied-filler": infile(p, r"In order to|\bsimply\b|Please note", match="not_contains", flags="i"),
        "b4-fixes-applied-drift": infile(p, r"The device appears", match="not_contains"),
        "b4-states-path": last(r"manual\.md"),
        "b4-states-edit-classes": last(r"filler|terminolog|wording|voice|passive|table|align|step|clarity|formatting", flags="i"),
        "b5-no-paste": NO_PASTE_PULSE,
    }


# ---------------------------------------------------------------- 4
BILLING = {
    "package.json": """{
  "name": "billing-dashboard",
  "version": "1.4.0",
  "private": true,
  "scripts": { "dev": "vite", "api": "node server/index.js" }
}
""",
    "README.md": """# billing-dashboard

React front end and Express API for the billing dashboard.

## Development

Run `npm install`, then `npm run dev` and `npm run api`.
""",
    "src/screens/InvoiceList.tsx": """// Invoices screen: the landing page after sign-in.
export function InvoiceList() {
  return (
    <Page title="Invoices">
      <StatusFilter options={["All", "Open", "Paid", "Overdue"]} />
      <Table columns={["Number", "Issued", "Due", "Amount", "Status"]} source="/api/bills" />
      <Button label="Download PDF" />
    </Page>
  );
}
""",
    "src/screens/InvoiceDetail.tsx": """// One invoice with its line items.
export function InvoiceDetail({ id }: { id: string }) {
  return (
    <Page title="Invoice">
      <LineItems source={`/api/bills/${id}`} />
      <Button label="Download PDF" href={`/api/bills/${id}/pdf`} />
      <Button label="Pay now" action={`/api/bills/${id}/pay`} disabledWhen="status === 'Paid'" />
    </Page>
  );
}
""",
    "src/screens/PaymentMethod.tsx": """// The card the account is charged with.
export function PaymentMethod() {
  return (
    <Page title="Payment method">
      <CardForm fields={["Card number", "Expiry", "CVC", "Name on card"]} />
      <Button label="Save card" action="PUT /api/payment-method" />
    </Page>
  );
}
""",
    "src/screens/Usage.tsx": """// API calls per day in the current billing period.
export function Usage() {
  return (
    <Page title="Usage">
      <BarChart source="/api/usage" x="day" y="calls" />
      <Note text="Usage above your plan's included calls is billed on the next invoice." />
    </Page>
  );
}
""",
    "server/routes.js": """// Express routes for the billing dashboard API.
router.get("/api/bills", listBills);             // ?status=open|paid|overdue
router.get("/api/bills/:id", getBill);
router.get("/api/bills/:id/pdf", billPdf);
router.post("/api/bills/:id/pay", payBill);      // charges the saved card
router.put("/api/payment-method", saveCard);     // 402 when the card is declined
router.get("/api/usage", usageThisPeriod);
""",
}


def case4():
    gate = {
        "b0-no-write": NO_WRITE, "b0-no-edit": NO_EDIT,
        "b1-asks-audience": last(r"audience|who (will |would )?(use|read)|reader|\buser(s)? (is|are) (it|this) for", flags="i"),
        "b1-asks-key-tasks": last(r"task|what (do|does|should) (they|the user|users) (need to )?do|workflows?", flags="i"),
        "b1-asks-terminology": last(r"invoices?[\s\S]{0,200}\bbills?\b|\bbills?\b[\s\S]{0,200}invoices?|terminolog", flags="i"),
        "b1-only-gaps": llm("The reply does not ask the user which screens exist, what the API routes "
                            "are, or what the product is — facts the repository already shows. Questions "
                            "about audience, terminology, output location, or behaviour the code leaves "
                            "unspecified are allowed."),
    }
    p = "docs/user-manual.md"
    full = {
        "b2-one-term": infile(p, r"(?<![/\w`])bills?\b", match="not_contains", flags="i"),
        # The overview is a lead paragraph under the title or an overview section.
        "b2-overview-first": infile(p, OVERVIEW, flags="im"),
        "b2-tasks-after-overview": infile(p, OVERVIEW + r"[\s\S]*^#{2,3} [^\n]*\b(pay|paying)\b", flags="im"),
        "b2-no-empty-section": infile(p, r"^## [^\n]+\n\s*## |\b(TBD|TODO|coming soon)\b", match="not_contains", flags="im"),
        "b3-file-written": exists(p),
        "b3-states-path": last(r"docs/user-manual\.md"),
        "b3-no-paste": last(r"^#{1,3} [^\n]+\n(?:[\s\S]*?^#{1,3} [^\n]+\n){3}", match="not_contains", flags="m"),
        "b4-names-pass-changes": llm("The reply states what the self-review (whole-document pass) of the written "
                                     "file changed, naming at least one concrete fix, or says explicitly that "
                                     "the pass found nothing to change."),
    }
    write_case("doc-smith--create-grounded-manual", BASE + [CREATE],
               "/craft:doc-smith create a user manual for the billing dashboard", full, files=BILLING,
               answers=["Accountants at our customer companies who pay for the service; they are not technical. "
                        "Key tasks: find and download an invoice, pay an open invoice, update the payment method, "
                        "and check usage. Call them invoices everywhere, never bills. Write it to docs/user-manual.md.",
                        "The outline is fine, go ahead."],
               max_turns=60, timeout=300)


# ---------------------------------------------------------------- 5


def case5():
    both = r"install\.md[\s\S]{0,400}?config\.md|config\.md[\s\S]{0,400}?install\.md"
    g = {
        "b0-no-write": NO_WRITE, "b0-no-edit": NO_EDIT,
        "b1-all-three-in-scope": last(r"^(?=[\s\S]*install\.md)(?=[\s\S]*config\.md)(?=[\s\S]*usage\.md)"),
        "b1-not-file-by-file": last(r"^#{1,4}\s*`?(docs/)?(install|config|usage)\.md`?\s*$", match="not_contains", flags="im"),
        "b2-drift-names-both-files": last(
            f"(?:workspace|project)[\\s\\S]{{0,500}}?(?:{both})|(?:{both})[\\s\\S]{{0,500}}?(?:workspace|project)", flags="i"),
        "b2-called-drift": last(r"(?=[\s\S]*workspace)(?=[\s\S]*project)[\s\S]*(drift|terminolog|inconsisten|two names|one term)", flags="i"),
        "b3-backup-is-a-gap": last(
            r"backup[^\n]{0,200}(missing|does not exist|doesn't exist|no such|dangling|broken|not (found|present)|none of|absent|nowhere)"
            r"|(missing|does not exist|doesn't exist|no such|dangling|broken|absent|nowhere)[^\n]{0,200}backup", flags="i"),
        "b3-backup-not-a-nit": last(r"(Blockers?|Should[- ]?fix)\b(?:(?!\bNits?\b)[\s\S])*Backup", flags="i"),
    }


# ---------------------------------------------------------------- 6
GUIDE_FB = """# Getting started with Fieldbook

Fieldbook is an app that simply keeps your survey notes, photos, and maps
together in one workspace, and the workspace can be shared by you with
your team.

## Creating a workspace

To create a workspace, select **New** on the home screen and enter a
name. You become the owner of the workspace.

## Inviting your team

To invite a colleague, open the workspace and select **Invite**. Each
member can add notes and photos to the workspace but cannot delete it.

## Archiving a workspace

When a survey is finished, archive its workspace to make it read-only.
Archived workspaces stay searchable.
"""
P1_NEW = """Fieldbook keeps your survey notes, photos, and maps together in one
project that you can share with your team."""
REVISE_Q = "/craft:doc-smith work through docs/guide.md with me"
TURN1 = """Revise mode on `docs/guide.md`: 4 units (intro paragraph, then one paragraph per section). The whole-document pass finds one term per concept ("workspace" throughout) and no contradictions. Starting at the top.

**Unit 1: intro paragraph (lines 3-5)**

Findings:
- Filler: "is an app that simply".
- Passive with a buried agent: "the workspace can be shared by you with your team".

Proposed revision:

> Fieldbook keeps your survey notes, photos, and maps together in one
> workspace that you can share with your team.

Coherence check: no break elsewhere.

Apply this?"""
RENAME = "Apply it, but call it a project instead of a workspace. That is the name in the new app."
NO_REPRINT_FB = last(r"To invite a colleague, open the|Archived (workspaces|projects) stay searchable",
                     match="not_contains")


def case6():
    p = "docs/guide.md"
    gate = {
        "b0-no-write": NO_WRITE, "b0-no-edit": NO_EDIT,
        "b1-not-an-audit": last(r"Should[- ]?fix|\bBlockers?\b", match="not_contains", flags="i"),
        "b1-starts-at-the-top": last(r"simply|shared by you|share (it )?with your team|\btop\b|first (unit|paragraph)|intro|lines? 3\b", flags="i"),
        "b5-no-reprint": NO_REPRINT_FB,
    }
    full = {
        "b1-agreed-revision-applied": infile(p, words(P1_NEW)),
        "b2-rest-not-swept": infile(p, r"^(?=[\s\S]*## Creating a workspace)(?=[\s\S]*open the workspace)(?=[\s\S]*Archived workspaces)"),
        "b3-later-sites-reported": last(
            r"^(?=[\s\S]*\bworkspaces?\b)(?=[\s\S]*(\blines?\s*\d+|\bL\d+|\.md:\d+|Creating a workspace|Inviting your team|Archiving a workspace))",
            flags="i"),
        "b4-no-unasked-sweep": infile(p, r"^#{1,3}\s[^\n]*\bproject", match="not_contains", flags="im"),
        "b5-no-reprint": NO_REPRINT_FB,
    }
    write_case("doc-smith--revise-keeps-the-whole-coherent", BASE + [REVISE, CLAIMS],
               "/craft:doc-smith " + RENAME, full, files={p: GUIDE_FB},
               hist=[("user", REVISE_Q), ("assistant", TURN1)])
    sweep = {
        "b4-swept-on-request": infile(p, r"\bworkspaces?\b", match="not_contains", flags="i"),
        "b4-content-intact": infile(p, r"^(?=[\s\S]*## Inviting your team)(?=[\s\S]*select \*\*Invite\*\*)(?=[\s\S]*read-only)"),
        "b4-unit-1-intact": infile(p, words(P1_NEW)),
        "b5-no-reprint": NO_REPRINT_FB,
    }


# ---------------------------------------------------------------- 7
def wrap(par, width=100):
    return "\n".join(textwrap.wrap(par, width))


MAP_PARS = [
    "The map view shows every asset in your network on one screen, and you can customise how it looks so that "
    "the information you need stands out. This guide explains the colour settings, the label options, and the "
    "way the map remembers your choices between sessions.",
    "Each asset type has its own colour. Pipes are drawn in blue by default, valves in orange, and hydrants in "
    "red, but your organisation can change these colours centrally so that every user sees the same scheme. If "
    "your administrator has locked the colour scheme, the **Colour** menu is greyed out and shows a short note "
    "instead.",
    "To change the color of an asset type, open **Settings**, select **Map**, and pick a new colour from the "
    "palette. The change applies at once, and the map remembers it the next time you sign in from the same "
    "browser on the same computer.",
    "Labels show the asset ID next to each symbol. When the map is zoomed out, labels are hidden automatically "
    "to keep the view readable, and they reappear as soon as you zoom in to street level again.",
]
LONG = ("Colour-blind users can switch to the high-contrast palette, which replaces the default colors with shapes "
        "and patterns\nthat remain distinct without relying on colour at all, and the palette applies to printed "
        "maps as well as to the screen.")
TABLE_BAD = """The following table lists the default colour for each asset type.

| Asset type | Default colour | Can be changed |
|------------|----------------|----------------|
| Pipe       | Blue           | Yes            |
| Valve      | Orange         | Yes            |
| Hydrant | Red | Only by an administrator |"""
ROWS = [("Asset type", "Default colour", "Can be changed"), ("Pipe", "Blue", "Yes"),
        ("Valve", "Orange", "Yes"), ("Hydrant", "Red", "Only by an administrator")]


def case7():
    body = "# Customising the Map View\n\n" + "\n\n".join(wrap(x) for x in MAP_PARS[:2]) + "\n\n"
    body += wrap(MAP_PARS[2]) + "\n\n" + TABLE_BAD + "\n\n" + wrap(MAP_PARS[3]) + "\n\n" + LONG + "\n"
    assert max(len(l) for l in body.split("\n") if not l.startswith("|")) > 100
    widths = [max(len(r[i]) for r in ROWS) for i in range(3)]
    def row(r):
        return "| " + " | ".join(c.ljust(w) for c, w in zip(r, widths)) + " |"
    rows = "|".join(re.escape(row(r)) for r in ROWS)
    p = "docs/guide.md"
    g = {
        "b1-us-outliers-fixed": infile(p, r"\bcolor(s|ed|ing)?\b", match="not_contains", flags="i"),
        "b1-british-kept": infile(p, r"^(?=[\s\S]*customise)(?=[\s\S]*organisation)(?=[\s\S]*greyed)(?:[\s\S]*?\bcolours?\b){9}"),
        "b2-counts-british-form": last(
            r"(?<![\w:.\-–]|lines? |L)(([4-9]|1\d)|four|five|six|seven|eight|nine|ten|eleven|twelve)\b(?!\))[^\n.;]{0,40}(\bcolours?\b|British)"
            r"|(\bcolours?\b|British)[^\n.;]{0,40}(×\s*([4-9]|1\d)\b|\(([4-9]|1\d)\)|\b([4-9]|1\d) (times|sites|uses|occurrences|places)\b)",
            flags="i"),
        "b2-counts-us-form": last(
            r"(\b\d+\b|×\s*\d+|\b(one|two|three)\b)[^\n]{0,80}\bcolors?\b|\bcolors?\b[^\n]{0,80}(\b\d+\b|×\s*\d+|\b(one|two|three)\b)",
            flags="i"),
        "b2-names-chosen-variety": last(r"British|\bUK\b|en-GB|Commonwealth|predominant|majority|dominant", flags="i"),
        "b3-reported-as-spelling-variety": last(r"spelling|variet(y|ies)", flags="i"),
        "b4-table-aligned": infile(p, f"^(?:{rows})$(?:[\\s\\S]*?^(?:{rows})$){{3}}", flags="m"),
        "b4-no-line-over-100": infile(p, r"^(?![|#])[^\n]{101,}$", match="not_contains", flags="m"),
        "b4-keeps-100-col-wrap": infile(p, r"(?:^[^|#\n][^\n]{85,99}$[\s\S]*?){3}", flags="m"),
        "b5-states-counts": last(r"\b\d+\b[^\n]{0,60}(spelling|reflow|line|table|row|cell|edit|fix|outlier|change)", flags="i"),
        "b5-no-paste": last(r"^\| Pipe +\| Blue|^Labels show the asset ID next to each symbol\. When the map", match="not_contains", flags="m"),
    }


if __name__ == "__main__":
    for d in glob.glob(os.path.join(EVALS, "doc-smith--*")):
        shutil.rmtree(d)
    for f in (case1, case2, case3, case4, case5, case6, case7):
        f()
    print("\n".join(sorted(os.path.basename(d) for d in glob.glob(os.path.join(EVALS, "doc-smith--*")))))
