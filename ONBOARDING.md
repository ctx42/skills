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
/plugin install go@ctx42-skills
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

- `go`: `/go:style`, `/go:review`, `/go:cover`, `/go:doc`, `/go:reshape`
- `srd`: `/srd:create`, `/srd:review`, `/srd:edit`, `/srd:system-check`,
  `/srd:report-doc-gap`, `/srd:backlog`, `/srd:kb`
- `craft`: `/craft:cm`, `/craft:grill-me`, `/craft:plan-smith`,
  `/craft:readme-smith`, `/craft:doc-smith`, `/craft:enhance-skills`

Each skill's `SKILL.md` opens with a `## Usage` block; its `evals/evals.json`
holds the scenarios it is expected to handle.

---

## 4. Set up a project for the SRD skills

The SRD skills keep nothing on the machine: everything lives in the project.
Commit a `project-config.md` at the project root whose YAML front matter names:

| Key            | Holds                                                              |
|----------------|--------------------------------------------------------------------|
| `mcp-server`   | the MCP server the skills call (`mcp__<name>__<tool>`)             |
| `kb`           | the knowledge-base folder; confirmed facts land in its `_inbox.md` |
| `initiatives`  | the SRD folder, one folder per SRD                                 |
| `srd-standard` | the document id of the SRD guidelines page                         |
| `glossary`     | the Company Glossary (a file or a folder)                          |

Paths are relative to the project root; an absolute path is an error. Start the
server, connect it with `/mcp`, and run any srd skill from inside the project:
each one stops with the exact problem when the file, a key, or the server is
missing. Facts you confirm during SRD work land in the knowledge base, which
`srd:kb` owns; doc gaps live on the server; work what both still owe with
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
