# Agent Skills by ding113

[![skills.sh](https://skills.sh/b/ding113/skills)](https://skills.sh/ding113/skills)

Personal agent skills I use every day, shared so they're easy to install anywhere — Claude Code, Codex, and any other Agent-Skills-standard harness.

## Quickstart

Copy the skills you want into your project with the [skills.sh](https://skills.sh/ding113/skills) installer — editable files you own from then on:

```bash
npx skills@latest add ding113/skills
```

## Install as a Claude Code plugin

Prefer a plug-and-play bundle that updates when this repo ships a new version? Inside Claude Code:

```
/plugin marketplace add ding113/skills
/plugin install ding113-skills@ding113
```

Or from your shell:

```bash
claude plugin marketplace add ding113/skills
claude plugin install ding113-skills@ding113
```

Two installs, two philosophies: **skills.sh** copies files into your repo to hack on and make your own; **the plugin** is a read-only, always-current subscription to the promoted set.

## Working on this repo

- `npm run validate` — the same gate CI runs ([validate.yml](./.github/workflows/validate.yml)); pair it with `claude plugin validate . --strict`
- `scripts/link-skills.sh` — symlink every skill into `~/.claude/skills` and `~/.agents/skills` for local dogfooding
- `scripts/list-skills.sh` — list every `SKILL.md`
- Conventions live in [CLAUDE.md](./CLAUDE.md) (repo rules), [CONTEXT.md](./CONTEXT.md) (shared language), and [.agents/](./.agents/) (invocation model, docs template, ADRs)
- Releases via [changesets](https://github.com/changesets/changesets): `npx changeset` to record a change, merge the version PR to release

## License

MIT
