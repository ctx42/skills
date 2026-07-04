# Skills

This repository is a collection of for the reusable skills use by both **Grok** 
and **Claude** AI agents. The skills ship as **Claude Code plugins**; Grok 
reads the same Claude marketplace ad plugins directly, so one catalog serves
both tools.

## Purpose

All skills are maintained here and distributed through a plugin marketplace
([`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json)). This
keeps every machine on the same versioned catalog with no manual copying or
symlinking.

## Organization

Skills are grouped into three plugins, one directory per plugin, each with its
own manifest and a `skills/` folder:

```
<repo-root>/
├── README.md  CONTRIBUTING.md  STRUCTURE.md  ONBOARDING.md  AGENTS.md
├── dev/                                 # maintainer scripts (lint, version sync)
├── .claude-plugin/marketplace.json      # the marketplace catalog (3 plugins)
│
├── golang/
│   ├── .claude-plugin/plugin.json
│   └── skills/{style,review,cover}/
├── srd/
│   ├── .claude-plugin/plugin.json
│   └── skills/{create,review,edit,system-check}/
└── craft/
    ├── .claude-plugin/plugin.json
    └── skills/{cm,grill-me,skill-smith}/
```

| Plugin   | Skills                                     | Purpose                                              |
|----------|--------------------------------------------|------------------------------------------------------|
| `golang` | `style`, `review`, `cover`                 | Go write-time style, done-time review, test coverage |
| `srd`    | `create`, `review`, `edit`, `system-check` | Software Requirement Document lifecycle              |
| `craft`  | `cm`, `grill-me`, `skill-smith`            | Commit messages, planning interview, skill authoring |

Plugin skills are **namespaced** by their plugin (e.g. `/srd:review`),
so they never silently shadow a personal or project skill of the same name.

## Install

### Claude Code

```shell
# add this repo as a marketplace (once per machine)
/plugin marketplace add ctx42/skills

# install the groups you want
/plugin install golang@ctx42-skills
/plugin install srd@ctx42-skills
/plugin install craft@ctx42-skills
```

Update to the latest with `/plugin marketplace update ctx42-skills`.

### From a local clone

Install straight from your working copy instead of a published remote — same
**global** result (skills land in the user-scope cache and every Claude Code
session on the machine sees them), but you own the source on disk. Do this once
per machine.

1. **Clone the repo somewhere permanent.** The install references this path, so
   don't put it in `/tmp` or a throwaway dir:

   ```shell
   git clone https://github.com/ctx42/skills.git ~/ws/ctx42-skills
   ```

2. **Register the clone as a marketplace.** Point it at the clone directory;
   Claude reads the catalog in place (no copy of the marketplace itself):

   ```shell
   claude plugin marketplace add ~/ws/ctx42-skills
   ```

   Equivalent inside a session: `/plugin marketplace add ~/ws/ctx42-skills`.

3. **Install the plugins you want.** Each is copied into the user-scope cache
   (`~/.claude/plugins/cache/ctx42-skills/…`) and enabled for all sessions:

   ```shell
   claude plugin install golang@ctx42-skills
   claude plugin install srd@ctx42-skills
   claude plugin install craft@ctx42-skills
   ```

4. **Restart Claude** (or run `/reload-plugins`), then verify with `/plugin` or
   by calling a namespaced skill such as `/srd:review`.

Prefer config over commands? Declare the same thing in `~/.claude/settings.json`
— it applies to every session and travels with the file if you sync your
dotfiles:

```json
{
  "extraKnownMarketplaces": {
    "ctx42-skills": {
      "source": { "source": "directory", "path": "/home/you/ws/ctx42-skills" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": {
    "golang@ctx42-skills": true,
    "srd@ctx42-skills": true,
    "craft@ctx42-skills": true
  }
}
```

Use an **absolute** path (no `~`), and see [Develop](#develop) for how edits to
the clone reach your sessions.

### Grok

Grok reads Claude marketplaces and plugins directly, so a Claude install is
picked up automatically. To manage it from Grok instead:

```shell
grok plugin marketplace add ctx42/skills
grok plugin install srd@ctx42-skills
```

## Develop

Iterate on a skill without reinstalling — load the group straight from the repo
and reload after edits:

```shell
claude --plugin-dir ./srd   # repeat the flag to load several groups
# …edit a SKILL.md…
/reload-plugins             # picks up the change live
/srd:system-check           # test it (skills are namespaced)
```

`--plugin-dir` reads the directory live (uncommitted edits included), but only
for **that one session**. To push an edit to *every* session that installed the
plugin (see [From a local clone](#from-a-local-clone)), you must bump the repo
version and commit — the cache is keyed on each plugin's `version`, so
`claude plugin update <plugin>@ctx42-skills` at an unchanged version is a no-op.
Set the version once in the `VER` file and commit; a `pre-commit` hook derives
every manifest version from `VER` so nothing drifts (never edit manifest
versions by hand — see [Versioning](CONTRIBUTING.md#versioning)):

```shell
# in your clone (once: ./dev/version.sh install-hooks)
# bump VER + CHANGELOG, commit, tag, push — the hook syncs all manifests
claude plugin update golang@ctx42-skills     # copies the new version into the cache
```

Then restart running sessions (or `/reload-plugins`) to load it. In short:
`--plugin-dir` for live iteration in one session; **bump `VER` + `update`** to
publish an edit to all sessions.

**Editing rules that a skill grows itself** — e.g. `golang:review`/`golang:style`
rule edits via `/golang:review add …` — must be done against your clone with
`--plugin-dir ./golang`, then committed, so the change reaches the repo. A
marketplace install is a versioned *copy* under `~/.claude/plugins/cache/`; edits
made there land in that throwaway copy and are lost on the next update, never
reaching the source of truth. (Per-machine data like `srd:system-check`'s memory
is exempt — it lives at a fixed external path, not inside the plugin.)

Run `./dev/lint-skills.sh` before committing; it checks every skill against the
mechanical parts of the authoring standard and the marketplace wiring.

## More detail

- [STRUCTURE.md](./STRUCTURE.md) — directory map and the plugin model
- [CONTRIBUTING.md](./CONTRIBUTING.md) — add, rename, and retire a skill
- [ONBOARDING.md](./ONBOARDING.md) — set up a new machine
- [AGENTS.md](./AGENTS.md) — guide for AI agents working in this repo
