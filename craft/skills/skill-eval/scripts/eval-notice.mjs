// eval-notice.mjs — drops an account-level notice from a case's last message.
//
// Some accounts carry instructions that make every session append a one-paragraph
// notice to its reply. That paragraph is the account's, not the skill's, and a
// grader on the last message would fail on it. The pattern comes from the
// EVAL_STRIP_NOTICE environment variable, so no account's wording lives here.

// stripNotice returns text without its last paragraph when that paragraph
// matches pattern (a JavaScript regex source) and is not the only one. With no
// pattern, it returns text unchanged.
export function stripNotice(text, pattern) {
  if (!pattern) return text;
  const paras = text.trimEnd().split(/\n\s*\n/);
  if (paras.length < 2 || !new RegExp(pattern).test(paras[paras.length - 1])) return text;
  return paras.slice(0, -1).join("\n\n").trimEnd();
}
