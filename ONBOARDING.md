# Onboarding Guide: Setting Up the Skills

This guide sets up the skills on a new machine so that **Claude** can use them.
The skills ship as Claude Code plugins from this repo's marketplace.

---

## 1. Install from the marketplace (recommended)

You do not need to clone the repo to *use* the skills — install them from the
marketplace.

### Claude Code

```shell
/plugin marketplace add ctx42/skills
/plugin install golang@ctx42-skills
/plugin install srd@ctx42-skills
/plugin install craft@ctx42-skills
```

Update later with `/plugin marketplace update ctx42-skills`.

---

## 2. Clone the repo (only to develop skills)

If you will edit skills, clone the repo and use the dev loop:

```bash
git clone https://github.com/ctx42/skills.git
cd skills
./dev/version.sh install-hooks  # once: enables the version-sync pre-commit hook
claude --plugin-dir ./srd       # load a group straight from the repo
# …edit a SKILL.md…  then in the session:
/reload-plugins                        # picks up the change live
```

`install-hooks` points git at the tracked `.githooks/`, so bumping the version
keeps every plugin/marketplace version in lockstep with `VER` (see
[Versioning](CONTRIBUTING.md#versioning)).

---

## 3. Verify the setup

List available skills. They are namespaced by plugin, e.g.:

- `golang`: `/golang:style`, `/golang:review`, `/golang:cover`, `/golang:doc`, `/golang:reshape`
- `srd`: `/srd:create`, `/srd:review`, `/srd:edit`, `/srd:system-check`,
  `/srd:report-doc-gap`, `/srd:backlog`, `/srd:kb`
- `craft`: `/craft:cm`, `/craft:grill-me`, `/craft:plan-smith`,
  `/craft:readme-smith`, `/craft:doc-smith`, `/craft:enhance-skills`

Each skill's `SKILL.md` opens with a `## Usage` block; its `evals/evals.json`
holds the scenarios it is expected to handle.

---

## 4. The knowledge base

The SRD skills build a knowledge base about your platform as you use them —
facts you confirm during an interview become Markdown pages that every agent can
search. `srd:kb` owns it; you never invoke it directly.

It lives in a directory you choose on first use, remembered at:

```
~/.agent-data/ctx42-skills/srd/kb-root
```

Pick a directory in a git repository that **no Confluence sync manages** — a
sync pull would clobber agent writes. Serve it to agents by adding it as a
source in your `mcp-doc.yaml`, then work what it still owes with
`/srd:backlog`.

---

## 5. Troubleshooting

- **Skills not appearing**: confirm the marketplace is added
  (`claude plugin marketplace list`) and the plugin installed
  (`claude plugin list`); run `/reload-plugins` or restart the tool.
- **Editing a skill has no effect**: a marketplace-installed copy is cached. Use
  `--plugin-dir ./<group>` + `/reload-plugins` for live edits, or
  `claude plugin marketplace update ctx42-skills` after pushing.
- **Old symlinks**: earlier setups symlinked skills into `~/.claude/skills/`.
  Remove any that point into this repo — the plugin install replaces them, and
  leaving them causes duplicate skills.

---

That's it. This setup keeps Claude aligned with the same engineering standards.
