"""Drops an account-level notice from a case's last message.

Some accounts carry instructions that make every session append a
one-paragraph notice to its reply. That paragraph is the account's, not the
skill's, and a grader on the last message would fail on it. The pattern comes
from the EVAL_STRIP_NOTICE environment variable, so no account's wording lives
here.
"""
import re

import jsregex


def strip_notice(text, pattern):
    """Return text without its last paragraph when that paragraph matches
    pattern (a JavaScript regex source) and is not the only one. With no
    pattern, return text unchanged."""
    if not pattern:
        return text
    paras = re.split(r"\n\s*\n", text.rstrip())
    if len(paras) < 2 or not jsregex.compile(pattern).search(paras[-1]):
        return text
    return "\n\n".join(paras[:-1]).rstrip()
