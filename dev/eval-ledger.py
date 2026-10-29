#!/usr/bin/env python3
# Wrapper: the script ships in the craft:skill-eval skill; it runs on this repo.
import os, sys; r = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.environ["SKILL_EVAL_ROOT"] = r; os.execv(sys.executable, [sys.executable, os.path.join(r, "craft/skills/skill-eval/scripts", "eval-ledger.py")] + sys.argv[1:])
