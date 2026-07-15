Skills are organized into bucket folders under `skills/`:

- `engineering/` — daily code work
- `writing/` — writing and publishing work
- `misc/` — kept around but rarely used, not promoted
- `personal/` — tied to my own setup, not promoted
- `in-progress/` — drafts not yet ready to ship
- `deprecated/` — no longer used

`engineering/` and `writing/` are the **promoted** buckets. Every skill there must have a reference in the top-level `README.md`, an entry in `.claude-plugin/plugin.json`'s `skills` array (the Claude Code plugin ships exactly the promoted set), and a docs page at `docs/<bucket>/<skill-name>.md` (see [.agents/writing-docs.md](./.agents/writing-docs.md)). Skills in the other buckets must appear in none of those three places — the top-level `README.md` may point at drafts only via a link to `skills/in-progress/README.md`, never by linking a draft's `SKILL.md` directly.

The repo is its own single-plugin Claude Code marketplace: `.claude-plugin/marketplace.json` lists the one `ding113-skills` plugin. Keep `.claude-plugin/plugin.json`'s `version` in sync with `package.json`'s — Claude uses the plugin `version` to decide when installed users see an update. Changesets bumps only `package.json`, so mirror the bump into `plugin.json` in the version PR; the gate stays red until you do.

**The gate**: run `npm run validate` (tree, frontmatter, invocation-flag sync, manifests, READMEs, docs pages) and `claude plugin validate . --strict` after touching any skill or manifest. CI runs both on every push and PR (`.github/workflows/validate.yml`); a red gate blocks merge.

Every skill is one folder, `skills/<bucket>/<name>/`, holding `SKILL.md` (frontmatter: single-line `name` and `description`) plus `agents/openai.yaml` (Codex UI metadata: `interface.display_name`, `interface.short_description`). A skill is either **user-invoked** (`disable-model-invocation: true` in `SKILL.md` plus `policy.allow_implicit_invocation: false` in `agents/openai.yaml`) or **model-invoked** (both flags absent) — keep the two flags in sync; the validator checks. See [.agents/invocation.md](./.agents/invocation.md).

Each bucket folder has a `README.md` listing every skill in the bucket with a one-line description, the skill name linked to its `SKILL.md`. The promoted buckets group entries into **User-invoked** and **Model-invoked**; the other buckets use a flat list.

**Graduating a draft** (`in-progress/` → a promoted bucket): move the folder; update both bucket `README.md`s; add the top-level `README.md` reference; add the `plugin.json` entry; write the docs page per [.agents/writing-docs.md](./.agents/writing-docs.md); add a changeset; run the gate.

Releases use [changesets](https://github.com/changesets/changesets): record a change with `npx changeset`; the Release workflow (`.github/workflows/release.yml`) opens a version PR and tags on merge. `CONTEXT.md` holds the repo's shared language; decisions live in `.agents/adr/`.

To (re)link every skill into the local harness skill directories (`~/.claude/skills`, `~/.agents/skills`), run `scripts/link-skills.sh`. Each entry is a symlink into this repo, so a `git pull` keeps installed skills current; re-run the script after adding, removing, or renaming a skill.
