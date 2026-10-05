#!/usr/bin/env node
// Lints the native eval cases (<group>/evals/<case>/) against
// dev/eval/native-cases.md. Mechanical checks only — it never edits files.
// Called by dev/lint-skills.sh; prints ERROR/WARN lines and the error count
// as its last line ("cases: N error(s)"), exit 1 on any error.
//
// For each group with an evals/ dir it checks:
//   - every evals.json scenario has a case `<skill>--<name>` (gate and other
//     suffixed variants `<skill>--<name>--<suffix>` count), and every case
//     belongs to a scenario,
//   - prompt.md tags: `case:<dir>` present; each skill:/sec:/ref: tag names a
//     real skill, `## ` section, or reference; any other tag is a known free
//     tag (FREE_TAGS),
//   - needs-shell is tagged exactly when allowed_tools grants Bash, and
//     always when a tagged skill injects shell output (!`…`); a needs-shell
//     case (run by dev/eval-shell.mjs) has no mocks/ and only the grader
//     types that runner supports,
//   - append_system_prompt exists and opens with the English line,
//   - max_turns <= 80; timeout_seconds <= 300, or <= 600 with the fan-out or
//     long tag,
//   - every grader pattern (regex body, input_match) compiles as JavaScript
//     with its flags and uses no PCRE-only anchor (\A, \Z, \z),
//   - a case mock fixture that shadows a suite one (same path under mocks/,
//     e.g. the frozen srd-standard.md) is byte-identical to it: case mocks
//     cannot reference suite files, so the suite file is the source and the
//     copies must follow it.
import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const ENGLISH = "The user writes English; reply in English.";
const FREE_TAGS = new Set(["needs-shell", "fan-out", "long"]);
const SHELL_GRADERS = new Set(["regex", "tool_used", "tool_order", "file_exists"]);
const MAX_TURNS = 80, TIMEOUT = 300, TIMEOUT_FANOUT = 600;

let errors = 0, warnings = 0;
const err = (m) => { console.log(`ERROR  ${m}`); errors++; };
const warn = (m) => { console.log(`WARN   ${m}`); warnings++; };

const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
const isDir = (p) => fs.existsSync(p) && fs.statSync(p).isDirectory();

// Splits a file into its frontmatter text and body.
function split(text) {
  const m = text.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  return m ? { fm: m[1], body: m[2] } : { fm: "", body: text };
}

// Reads a top-level scalar; strips one layer of YAML quotes.
function scalar(fm, key) {
  const m = fm.match(new RegExp(`^${key}:[ \\t]*(.*)$`, "m"));
  if (!m) return undefined;
  return unquote(m[1].trim());
}

function unquote(v) {
  if (v.startsWith("'") && v.endsWith("'")) return v.slice(1, -1).replace(/''/g, "'");
  if (v.startsWith('"') && v.endsWith('"')) return JSON.parse(v);
  return v;
}

// Every input_match value anywhere in the frontmatter (flow maps included).
function inputMatches(fm) {
  const out = [];
  const re = /input_match:\s*('(?:[^']|'')*'|"(?:[^"\\]|\\.)*"|[^,}\n]+)/g;
  for (const m of fm.matchAll(re)) out.push(unquote(m[1].trim()));
  return out;
}

function compiles(where, pattern, flags) {
  // Valid in PCRE/Python, an identity escape (a literal letter) in JavaScript.
  if (/(?<!\\)(?:\\\\)*\\[AZz]/.test(pattern)) err(`${where}: \\A, \\Z and \\z are not anchors in JavaScript — use ^ and $ without the m flag`);
  try {
    new RegExp(pattern, flags || "");
  } catch (e) {
    err(`${where}: pattern does not compile as JavaScript: ${e.message}`);
  }
}

// The tags --list-tags prints for every skill of a group.
function knownTags(group) {
  const tags = new Set();
  const skillsDir = path.join(ROOT, group, "skills");
  for (const s of fs.readdirSync(skillsDir)) {
    const md = path.join(skillsDir, s, "SKILL.md");
    if (!fs.existsSync(md)) continue;
    tags.add(`skill:${s}`);
    for (const m of fs.readFileSync(md, "utf8").matchAll(/^## (.+)$/gm)) {
      tags.add(`sec:${s}:${slug(m[1])}`);
    }
    const refs = path.join(skillsDir, s, "references");
    if (isDir(refs)) {
      for (const r of fs.readdirSync(refs)) {
        if (r.endsWith(".md")) tags.add(`ref:${s}/${r.slice(0, -3)}`);
      }
    }
  }
  return tags;
}

function scenarios(group) {
  const out = new Map(); // "<skill>--<name>" -> evals.json path
  const skillsDir = path.join(ROOT, group, "skills");
  for (const s of fs.readdirSync(skillsDir)) {
    const f = path.join(skillsDir, s, "evals", "evals.json");
    if (!fs.existsSync(f)) continue;
    for (const e of JSON.parse(fs.readFileSync(f, "utf8")).evals) {
      out.set(`${s}--${slug(e.name)}`, path.relative(ROOT, f));
    }
  }
  return out;
}

// Every file under dir, as paths relative to it.
function walk(dir, rel = "") {
  const out = [];
  for (const e of fs.readdirSync(path.join(dir, rel), { withFileTypes: true })) {
    const r = path.join(rel, e.name);
    if (e.isDirectory()) out.push(...walk(dir, r));
    else out.push(r);
  }
  return out;
}

function lintFixtureCopies(group, dir) {
  const caseMocks = path.join(ROOT, group, "evals", dir, "mocks");
  const suiteMocks = path.join(ROOT, group, "evals", "mocks");
  if (!isDir(caseMocks) || !isDir(suiteMocks)) return;
  for (const rel of walk(caseMocks)) {
    if (!rel.split(path.sep).includes("fixtures")) continue;
    const src = path.join(suiteMocks, rel);
    if (!fs.existsSync(src)) continue;
    if (!fs.readFileSync(src).equals(fs.readFileSync(path.join(caseMocks, rel)))) {
      const to = path.relative(ROOT, path.join(caseMocks, rel));
      err(`${to}: differs from the suite copy — cp ${path.relative(ROOT, src)} ${to}`);
    }
  }
}

function lintCase(group, dir, known) {
  lintFixtureCopies(group, dir);
  const rel = `${group}/evals/${dir}`;
  const promptPath = path.join(ROOT, rel, "prompt.md");
  const { fm } = split(fs.readFileSync(promptPath, "utf8"));

  const tm = fm.match(/^tags:\s*\[([^\]]*)\]/m);
  const tags = tm ? tm[1].split(",").map((t) => t.trim()).filter(Boolean) : [];
  if (!tags.includes(`case:${dir}`)) err(`${rel}/prompt.md: tags lack case:${dir}`);
  for (const t of tags) {
    if (t.startsWith("case:")) {
      if (t !== `case:${dir}`) err(`${rel}/prompt.md: foreign case tag ${t}`);
    } else if (/^(skill|sec|ref):/.test(t)) {
      if (!known.has(t)) err(`${rel}/prompt.md: tag ${t} names no skill, section, or reference`);
    } else if (!FREE_TAGS.has(t)) {
      err(`${rel}/prompt.md: unknown tag ${t} (free tags: ${[...FREE_TAGS].join(", ")})`);
    }
  }

  // eval-changed.sh grants Bash only to needs-shell cases.
  const shell = tags.includes("needs-shell");
  const am = fm.match(/^allowed_tools:\s*\[([^\]]*)\]/m);
  const bash = am && /(^|[\s,])Bash\b/.test(am[1]);
  if (bash && !shell) err(`${rel}/prompt.md: allowed_tools has Bash but tags lack needs-shell`);
  if (shell && !bash) err(`${rel}/prompt.md: tagged needs-shell but allowed_tools has no Bash(<cmd>:*)`);
  for (const t of tags) {
    const s = t.match(/^skill:(.+)$/)?.[1];
    const md = s && path.join(ROOT, group, "skills", s, "SKILL.md");
    if (md && !shell && fs.existsSync(md) && fs.readFileSync(md, "utf8").includes("!`")) {
      err(`${rel}/prompt.md: skill ${s} injects shell output (!\`…\`) but tags lack needs-shell`);
    }
  }

  const asp = fm.match(/^append_system_prompt:\s*\|[-+]?\n[ \t]+(.*)$/m);
  if (!asp) err(`${rel}/prompt.md: no append_system_prompt (it opens with the English line)`);
  else if (asp[1].trim() !== ENGLISH) err(`${rel}/prompt.md: append_system_prompt does not open with "${ENGLISH}"`);

  const turns = Number(scalar(fm, "max_turns"));
  if (!(turns > 0)) err(`${rel}/prompt.md: max_turns missing`);
  else if (turns > MAX_TURNS) err(`${rel}/prompt.md: max_turns ${turns} > ${MAX_TURNS}`);
  const timeout = Number(scalar(fm, "timeout_seconds"));
  const cap = tags.includes("fan-out") || tags.includes("long") ? TIMEOUT_FANOUT : TIMEOUT;
  if (!(timeout > 0)) err(`${rel}/prompt.md: timeout_seconds missing`);
  else if (timeout > cap) err(`${rel}/prompt.md: timeout_seconds ${timeout} > ${cap}${cap === TIMEOUT ? " (fan-out cases tag fan-out, other long runs long, for 600)" : ""}`);

  if (shell && isDir(path.join(ROOT, rel, "mocks"))) err(`${rel}: needs-shell cases run through dev/eval-shell.mjs, which serves no mocks`);
  const graders = path.join(ROOT, rel, "graders");
  if (!isDir(graders)) { err(`${rel}: no graders/`); return; }
  for (const g of fs.readdirSync(graders).filter((f) => f.endsWith(".md"))) {
    const where = `${rel}/graders/${g}`;
    const { fm: gfm, body } = split(fs.readFileSync(path.join(graders, g), "utf8"));
    const type = scalar(gfm, "type");
    if (!type) { err(`${where}: no type`); continue; }
    for (const im of inputMatches(gfm)) compiles(`${where} input_match`, im);
    if (shell && !SHELL_GRADERS.has(type)) err(`${where}: needs-shell cases run through dev/eval-shell.mjs, which grades only ${[...SHELL_GRADERS].join(", ")}`);
    if (shell && /^target:\s*mock_calls/m.test(gfm)) err(`${where}: needs-shell cases run without mocks; no mock_calls target`);
    if (type === "regex") {
      const pattern = body.replace(/\n$/, "");
      if (!pattern) err(`${where}: empty pattern`);
      else compiles(where, pattern, scalar(gfm, "flags"));
    }
  }
}

for (const group of fs.readdirSync(ROOT).sort()) {
  const evals = path.join(ROOT, group, "evals");
  if (!fs.existsSync(path.join(ROOT, group, ".claude-plugin", "plugin.json")) || !isDir(evals)) continue;
  const known = knownTags(group);
  const scen = scenarios(group);
  const cases = fs.readdirSync(evals).filter((d) => fs.existsSync(path.join(evals, d, "prompt.md"))).sort();
  const covered = new Set();
  for (const dir of cases) {
    lintCase(group, dir, known);
    const parts = dir.split("--");
    const key = `${parts[0]}--${parts[1]}`;
    if (scen.has(key)) covered.add(key);
    else err(`${group}/evals/${dir}: no evals.json scenario ${key}`);
  }
  for (const [key, src] of scen) {
    if (!covered.has(key)) err(`${src}: scenario ${key.split("--")[1]} has no native case ${group}/evals/${key}`);
  }
  lintTraceability(group, cases);
}

// Every expectations bullet is checked by something, or says it is not:
// a grader b<N>-* in one of the scenario's cases (gate/stop variants count),
// a probe listing "<scenario-slug>#b<N>" in its `bullets`, or the scenario's
// `blind_only` list (graded only in a blind round).
function lintTraceability(group, cases) {
  const skillsDir = path.join(ROOT, group, "skills");
  for (const s of fs.readdirSync(skillsDir)) {
    const ef = path.join(skillsDir, s, "evals", "expectations.json");
    if (!fs.existsSync(ef)) continue;
    const rel = path.relative(ROOT, ef);
    const pf = path.join(skillsDir, s, "evals", "probes.json");
    const probed = new Set();
    const exps = JSON.parse(fs.readFileSync(ef, "utf8")).expectations;
    const names = new Map(exps.map((e) => [slug(e.name), e.expected_behavior.length]));
    if (fs.existsSync(pf)) {
      for (const p of JSON.parse(fs.readFileSync(pf, "utf8")).probes) {
        for (const b of p.bullets || []) {
          const m = b.match(/^([a-z0-9-]+)#b(\d+)$/);
          if (!m || !names.has(m[1]) || +m[2] < 1 || +m[2] > names.get(m[1])) {
            err(`${path.relative(ROOT, pf)}: probe ${p.id}: bullet "${b}" names no expectations bullet`);
          } else probed.add(b);
        }
      }
    }
    for (const e of exps) {
      const sl = slug(e.name);
      const graded = new Set();
      for (const dir of cases.filter((d) => d === `${s}--${sl}` || d.startsWith(`${s}--${sl}--`))) {
        const gd = path.join(ROOT, group, "evals", dir, "graders");
        if (!isDir(gd)) continue;
        for (const g of fs.readdirSync(gd)) {
          const m = g.match(/^b(\d+)-/);
          if (m) graded.add(+m[1]);
        }
      }
      const blind = new Set(e.blind_only || []);
      for (let i = 1; i <= e.expected_behavior.length; i++) {
        const n = [graded.has(i), probed.has(`${sl}#b${i}`), blind.has(i)].filter(Boolean).length;
        if (n === 0) err(`${rel}: ${e.name} b${i} has no grader, probe, or blind_only entry`);
        if (blind.has(i) && n > 1) err(`${rel}: ${e.name} b${i} is blind_only but is also checked — drop it from blind_only`);
      }
      for (const i of blind) {
        if (!(i >= 1 && i <= e.expected_behavior.length)) err(`${rel}: ${e.name}: blind_only ${i} names no bullet`);
      }
    }
  }
}

console.log(`cases: ${errors} error(s), ${warnings} warning(s)`);
process.exit(errors ? 1 : 0);
