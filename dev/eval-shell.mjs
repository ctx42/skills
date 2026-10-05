#!/usr/bin/env node
// eval-shell.mjs — runs the needs-shell native cases without `claude plugin eval`.
//
// `claude plugin eval` wraps every in-run command in a sandbox that nests a
// user namespace inside bwrap's; stock Ubuntu refuses that, so every Bash call
// in a case fails. This runner does the eval's job for those cases with a
// plain `claude -p`, the way a user runs a skill: no OS sandbox, the case's
// allowed_tools only, in a throwaway workspace. Called by dev/eval-changed.sh.
//
// Per case: copy the plugin read-only to <tmp>/plugin, run scaffold.sh in
// <tmp>/home/cwd with $HOME=<tmp>/home, then `claude -p` the prompt body there
// (project setting sources only: no user hooks, CLAUDE.md, plugins, or MCP
// servers), and grade the trace and workspace. Grader types: regex (targets
// last_message, trace, {source: file, path}), tool_used, tool_order,
// file_exists. Patterns are JavaScript regexes, as in `claude plugin eval`.
//
// Usage:
//   node dev/eval-shell.mjs <group> <case>... [--model M] [-j N]
//        [--max-cost-usd N] [--json out.json] [--keep]
//
// Writes the `claude plugin eval --json` result shape (cases[].arms.with[],
// aggregates, costUsd), so dev/eval-ledger.py records it unchanged. Exit 0
// when every case passes, 1 otherwise, 2 when --max-cost-usd stopped it.
import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");

function die(msg) {
  console.error(`eval-shell: ${msg}`);
  process.exit(1);
}

// --- Arguments. ---
const argv = process.argv.slice(2);
let model = "sonnet", jobs = 1, maxUsd = Infinity, jsonOut = "", keep = false;
const rest = [];
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === "--model") model = argv[++i];
  else if (a === "-j") jobs = Math.max(1, Number(argv[++i]));
  else if (a === "--max-cost-usd") maxUsd = Number(argv[++i]);
  else if (a === "--json") jsonOut = argv[++i];
  else if (a === "--keep") keep = true;
  else rest.push(a);
}
const [group, ...cases] = rest;
if (!group || cases.length === 0) die("usage: eval-shell.mjs <group> <case>... [--model M] [-j N] [--max-cost-usd N] [--json out] [--keep]");
if (!fs.existsSync(path.join(ROOT, group, ".claude-plugin", "plugin.json"))) die(`${group}: not a plugin group`);

// --- Case files. ---
function frontmatter(text) {
  const m = text.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  return m ? { fm: m[1], body: m[2] } : { fm: "", body: text };
}

// One YAML scalar: 'single' ('' escapes '), "double" (JSON escapes), or plain.
function scalar(v) {
  v = v.trim();
  if (v.startsWith("'") && v.endsWith("'")) return v.slice(1, -1).replace(/''/g, "'");
  if (v.startsWith('"') && v.endsWith('"')) return JSON.parse(v);
  return v;
}

// A flow map `{a: x, b: 'y, z'}`: split on commas outside quotes.
function flowMap(v) {
  const inner = v.trim().replace(/^\{/, "").replace(/\}$/, "");
  const out = {};
  let key = "", buf = "", quote = "", inKey = true;
  const flush = () => {
    if (key.trim()) out[key.trim()] = scalar(buf);
    key = ""; buf = ""; inKey = true;
  };
  for (let i = 0; i < inner.length; i++) {
    const c = inner[i];
    if (quote) {
      buf += c;
      if (c === quote && !(quote === "'" && inner[i + 1] === "'")) quote = "";
      else if (c === quote) buf += inner[++i];
      else if (quote === '"' && c === "\\") buf += inner[++i];
    } else if (inKey && c === ":") inKey = false;
    else if (inKey) key += c;
    else if (c === "'" || c === '"') { quote = c; buf += c; }
    else if (c === ",") flush();
    else buf += c;
  }
  flush();
  return out;
}

// Top-level `key: value` lines of a grader or prompt frontmatter.
function fields(fm) {
  const out = {};
  for (const line of fm.split("\n")) {
    const m = line.match(/^([a-z_]+):\s*(.*)$/);
    if (!m) continue;
    const v = m[2].trim();
    out[m[1]] = v.startsWith("{") ? flowMap(v) : v.startsWith("[") ? v : scalar(v);
  }
  return out;
}

function loadCase(name) {
  const dir = path.join(ROOT, group, "evals", name);
  const pm = path.join(dir, "prompt.md");
  if (!fs.existsSync(pm)) die(`${group}/evals/${name}: no prompt.md`);
  const { fm, body } = frontmatter(fs.readFileSync(pm, "utf8"));
  const f = fields(fm);
  const list = (f.allowed_tools || "[]").replace(/^\[|\]$/g, "").split(",").map((t) => t.trim()).filter(Boolean);
  const asp = fm.match(/^append_system_prompt:\s*\|[-+]?\n((?:[ \t]+.*\n?|\n)*)/m);
  const yaml = fs.existsSync(path.join(dir, "case.yaml")) ? fs.readFileSync(path.join(dir, "case.yaml"), "utf8") : "";
  const graders = fs.readdirSync(path.join(dir, "graders")).filter((g) => g.endsWith(".md")).sort().map((g) => {
    const { fm: gfm, body: gbody } = frontmatter(fs.readFileSync(path.join(dir, "graders", g), "utf8"));
    return { name: g.replace(/\.md$/, ""), ...fields(gfm), pattern: gbody.trim() };
  });
  return {
    name, dir, prompt: body.trim(), allowed: list, graders,
    asp: asp ? asp[1].replace(/^ {2}/gm, "").trimEnd() : "",
    maxTurns: Number(f.max_turns) || 30,
    timeout: Number(f.timeout_seconds) || 300,
    scaffold: yaml.match(/scaffold_script:\s*(\S+)/)?.[1],
    history: yaml.match(/history_file:\s*(\S+)/)?.[1],
  };
}

// --- Grading. ---
function re(pattern, flags = "") {
  return new RegExp(pattern, flags.replace(/g/g, ""));
}

function count(text, pattern, flags) {
  return [...text.matchAll(new RegExp(pattern, flags.replace(/g/g, "") + "g"))].length;
}

function globRe(glob) {
  const s = glob.split(/(\*\*\/?|\*|\?)/).map((p) =>
    p === "**/" || p === "**" ? ".*" : p === "*" ? "[^/]*" : p === "?" ? "[^/]" : p.replace(/[.+^${}()|[\]\\]/g, "\\$&")).join("");
  return new RegExp(`^${s}$`);
}

function listFiles(dir, rel = "") {
  let out = [];
  for (const e of fs.readdirSync(path.join(dir, rel), { withFileTypes: true })) {
    const r = rel ? `${rel}/${e.name}` : e.name;
    if (e.isDirectory()) { if (e.name !== ".git") out = out.concat(listFiles(dir, r)); }
    else out.push(r);
  }
  return out;
}

function grade(g, run) {
  const ok = (passed, evidence = "") => ({ name: g.name, passed, evidence });
  const matchTool = (spec) => (u) => u.name === spec.tool &&
    (!spec.input_match || re(spec.input_match).test(JSON.stringify(u.input)));
  try {
    if (g.type === "regex") {
      let text;
      const t = g.target;
      if (t === "last_message") text = run.lastMessage;
      else if (t === "trace") text = run.trace;
      else if (t && t.source === "file") {
        const p = path.join(run.cwd, t.path);
        if (!fs.existsSync(p)) return ok(false, `file ${t.path} missing`);
        text = fs.readFileSync(p, "utf8");
      } else return ok(false, `unsupported regex target ${JSON.stringify(t)}`);
      const flags = g.flags || "", match = g.match || "contains";
      const n = count(text, g.pattern, flags);
      if (match === "contains") return ok(n > 0, n ? "" : "no match");
      if (match === "not_contains") return ok(n === 0, n ? `${n} match(es)` : "");
      const want = match.match(/^count:(\d+)$/);
      if (want) return ok(n === Number(want[1]), `${n} match(es), want ${want[1]}`);
      return ok(false, `unsupported match ${match}`);
    }
    if (g.type === "tool_used") {
      const n = run.toolUses.filter(matchTool(g)).length;
      const min = g.min === undefined ? 1 : Number(g.min);
      const max = g.max === undefined ? Infinity : Number(g.max);
      return ok(n >= min && n <= max, `${g.tool} used ${n} time(s), want ${min}..${max}`);
    }
    if (g.type === "tool_order") {
      const b = run.toolUses.findIndex(matchTool(g.before));
      const a = run.toolUses.findIndex(matchTool(g.after));
      if (b < 0 || a < 0) return ok(false, `${b < 0 ? "before" : "after"} call missing`);
      return ok(b < a, b < a ? "" : "after call came first");
    }
    if (g.type === "file_exists") {
      // Only files the run created count, never scaffold-made ones.
      const r = globRe(g.path);
      const made = listFiles(run.cwd).filter((f) => r.test(f) && !run.scaffolded.has(f));
      const want = String(g.exists) !== "false";
      return ok(want === made.length > 0, made.length ? made.join(", ") : `no ${g.path}`);
    }
    return ok(false, `unsupported grader type ${g.type}`);
  } catch (e) {
    return ok(false, `grader error: ${e.message}`);
  }
}

// --- Running one case. ---
const configDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), ".claude");
const goproxy = process.env.GOPROXY ||
  `file://${spawnSync("go", ["env", "GOMODCACHE"], { encoding: "utf8" }).stdout.trim()}/cache/download`;

function projectDir(cwd) {
  return path.join(configDir, "projects", cwd.replace(/[^A-Za-z0-9]/g, "-"));
}

function unseal(dir) {
  spawnSync("chmod", ["-R", "u+rwx", dir], { stdio: "ignore" });
}

async function runCase(c) {
  const started = Date.now();
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "claude-eval-sh-"));
  const home = path.join(tmp, "home"), cwd = path.join(home, "cwd"), out = path.join(tmp, "out");
  const plugin = path.join(tmp, "plugin");
  fs.mkdirSync(cwd, { recursive: true });
  fs.mkdirSync(out);
  // The plugin is read-only in runs: a stray edit must never reach the repo.
  fs.cpSync(path.join(ROOT, group), plugin, { recursive: true, filter: (s) => !s.startsWith(path.join(ROOT, group, "evals")) });
  spawnSync("chmod", ["-R", "a-w", plugin]);
  const env = { ...process.env, HOME: home, GOPROXY: goproxy, GOTOOLCHAIN: "local", GOFLAGS: "" };
  delete env.CLAUDECODE;
  for (const k of Object.keys(env)) if (k.startsWith("CLAUDE_CODE_")) delete env[k];
  env.CLAUDE_CONFIG_DIR = configDir;

  const result = { passed: false, error: null, graders: [], durationSeconds: 0, costUsd: 0, tracePath: path.join(out, "trace.jsonl") };
  let session = "";
  try {
    if (c.scaffold) {
      const s = spawnSync("bash", [path.join(c.dir, c.scaffold)], { cwd, env, encoding: "utf8" });
      if (s.status !== 0) throw new Error(`scaffold failed: ${(s.stderr || s.stdout).trim().split("\n").slice(-3).join(" | ")}`);
    }
    const scaffolded = new Set(listFiles(cwd));

    const args = ["-p", c.prompt, "--plugin-dir", plugin, "--max-turns", String(c.maxTurns),
      "--setting-sources", "project", "--strict-mcp-config",
      "--output-format", "stream-json", "--verbose"];
    if (model !== "default") args.push("--model", model);
    if (c.allowed.length) args.push("--allowedTools", ...c.allowed);
    if (c.asp) args.push("--append-system-prompt", c.asp);
    if (c.history) {
      // Resume a recorded session: it must sit in this workspace's project dir.
      const hist = fs.readFileSync(path.join(c.dir, c.history), "utf8");
      session = JSON.parse(hist.split("\n")[0]).sessionId;
      fs.mkdirSync(projectDir(cwd), { recursive: true });
      fs.writeFileSync(path.join(projectDir(cwd), `${session}.jsonl`), hist);
      args.push("--resume", session);
    } else {
      args.push("--no-session-persistence");
    }

    const trace = fs.openSync(result.tracePath, "w");
    const code = await new Promise((resolve) => {
      const p = spawn("claude", args, { cwd, env, stdio: ["ignore", trace, "pipe"] });
      let err = "";
      p.stderr.on("data", (d) => { err += d; });
      const timer = setTimeout(() => { result.error = `timeout after ${c.timeout}s`; p.kill("SIGTERM"); }, c.timeout * 1000);
      p.on("close", (code) => { clearTimeout(timer); fs.closeSync(trace); if (code && !result.error && err.trim()) result.error = err.trim().split("\n").slice(-2).join(" | "); resolve(code); });
    });

    const text = fs.readFileSync(result.tracePath, "utf8");
    const toolUses = [];
    let lastMessage = "", final = null;
    for (const line of text.split("\n")) {
      let e;
      try { e = JSON.parse(line); } catch { continue; }
      if (e.type === "assistant") {
        const parts = [];
        for (const b of e.message?.content || []) {
          if (b.type === "tool_use") toolUses.push(b);
          if (b.type === "text" && b.text) parts.push(b.text);
        }
        if (parts.length && !e.parent_tool_use_id) lastMessage = parts.join("\n");
      } else if (e.type === "result") final = e;
    }
    if (final) {
      result.costUsd = final.total_cost_usd || 0;
      if (final.result) lastMessage = final.result;
      // A run cut off by the usage limit says nothing about the skill.
      if (final.is_error && /limit/i.test(final.result || "")) result.error = `usage limit: ${final.result}`;
    } else if (!result.error) result.error = `claude exited ${code} without a result`;
    result.lastMessage = lastMessage;

    const run = { cwd, trace: text, lastMessage, toolUses, scaffolded };
    result.graders = c.graders.map((g) => grade(g, run));
    result.passed = !result.error && result.graders.every((g) => g.passed);
  } catch (e) {
    result.error = result.error || e.message;
  } finally {
    // Claude records every workspace under its config dir; drop ours.
    fs.rmSync(projectDir(cwd), { recursive: true, force: true });
    result.durationSeconds = Math.round((Date.now() - started) / 1000);
    if (!keep) {
      // The trace outlives the workspace only on failure (eval-changed keeps it).
      unseal(tmp);
      for (const d of [home, plugin]) fs.rmSync(d, { recursive: true, force: true });
      if (result.passed) fs.rmSync(tmp, { recursive: true, force: true });
    } else unseal(plugin);
  }
  return result;
}

// --- Main: a pool of -j runs, stopping launches at the cost ceiling. ---
const loaded = cases.map(loadCase);
const results = new Array(loaded.length);
let spent = 0, next = 0, capped = false;
const t0 = Date.now();
async function worker() {
  while (next < loaded.length) {
    if (spent >= maxUsd) { capped = true; return; }
    const i = next++;
    const c = loaded[i];
    console.error(`eval-shell: ${c.name} started (${new Date().toTimeString().slice(0, 5)})`);
    const r = await runCase(c);
    spent += r.costUsd;
    results[i] = { name: c.name, arms: { with: [r] } };
    console.error(`eval-shell: ${c.name} ${r.passed ? "PASS" : `FAIL, trace ${r.tracePath}`} (${r.durationSeconds}s, $${r.costUsd.toFixed(2)})`);
  }
}
await Promise.all(Array.from({ length: Math.min(jobs, loaded.length) }, worker));

const done = results.filter(Boolean);
const passed = done.filter((c) => c.arms.with[0].passed).length;
const agg = {
  cases: done,
  aggregates: { casesPassed: passed, casesTotal: done.length },
  durationSeconds: Math.round((Date.now() - t0) / 1000),
  costUsd: spent,
};
if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify(agg, null, 1));
else process.stdout.write(JSON.stringify(agg, null, 1) + "\n");
process.exit(capped ? 2 : passed === loaded.length ? 0 : 1);
