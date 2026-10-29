// Wrapper: the script ships in the craft:skill-eval skill; it runs on this repo.
import path from "node:path"; process.env.SKILL_EVAL_ROOT = path.resolve(import.meta.dirname, ".."); await import("../craft/skills/skill-eval/scripts/lint-cases.mjs");
