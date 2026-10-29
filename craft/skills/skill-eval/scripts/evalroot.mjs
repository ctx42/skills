// Where the skills repo under test lives, for the node eval scripts. They ship
// inside the skill-eval skill, so they cannot find the repo from their own
// path: the root is $SKILL_EVAL_ROOT when set, else the git top level of the
// working directory, else the working directory itself.
import { execFileSync } from "node:child_process";
import fs from "node:fs";

export function findRoot(env = process.env, cwd = process.cwd()) {
  if (env.SKILL_EVAL_ROOT) return fs.realpathSync(env.SKILL_EVAL_ROOT);
  let top = "";
  try {
    top = execFileSync("git", ["rev-parse", "--show-toplevel"], { cwd, env, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim();
  } catch {
    // not a git checkout: fall back to the working directory
  }
  return fs.realpathSync(top || cwd);
}
