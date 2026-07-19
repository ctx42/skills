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
- `srd`: `/srd:create`, `/srd:review`, `/srd:edit`, `/srd:system-check`
- `craft`: `/craft:cm`, `/craft:grill-me`, `/craft:plan-smith`,
  `/craft:skill-smith`, `/craft:readme-smith`, `/craft:doc-smith`,
  `/craft:enhance-skills`

Each skill has its own `README.md` with usage examples.

---

## 4. system-check memory

`system-check` builds a curated platform-knowledge base as you use it. It is
your data, stored once per machine at:

```
~/.agent-data/ctx42-skills/srd/memory.md
```

The `srd/` segment scopes it to the `srd` skills, so only they load it. It is
created on first use from the shipped template and survives plugin updates;
older installs migrate per
`srd/skills/system-check/references/memory-migration.md`.
Nothing to set up; back this file up if the knowledge is valuable.

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
