# Mirror mattpocock/skills conventions; ship drafts in `in-progress/`, not in the plugin

This repo hosts personal agent skills, shared publicly. It was rebuilt on 2026-07-15 as a single initial commit; the previous history (a couple of standalone skill experiments) was deliberately discarded.

Rather than inventing a layout, we adopt the conventions of [mattpocock/skills](https://github.com/mattpocock/skills) wholesale: a bucketed `skills/` tree with a curated **promoted** set (`engineering/`, `writing/`), a `.claude-plugin/` manifest pair making the repo its own single-plugin marketplace, per-skill `agents/openai.yaml` Codex metadata, changesets for versioned releases, and repo docs (`CLAUDE.md` + `AGENTS.md` symlink, `CONTEXT.md`, `.agents/`). Both install philosophies work from day one: skills.sh-style copy-install for people who want to own and edit the files, and the read-only plugin subscription for people who want the set to just work and stay current.

Two deviations from the reference repo:

1. **The invariants are executable.** The reference repo enforces its rules by convention; here they are a gate — `scripts/validate-skills.mjs` checks the tree layout, frontmatter, invocation-flag sync, manifests, READMEs, and docs pages, and `.github/workflows/validate.yml` runs it plus `claude plugin validate . --strict` on every push and PR.
2. **Founding skills start as drafts.** `article-writing`, `get-pr-comments`, and `fix-ci` live in `skills/in-progress/` with real frontmatter and draft bodies, and the plugin's `skills` array stays empty until the first graduation. Shipping an unfinished skill would hijack real requests — a model-invoked draft with a rich description *will* fire — and then deliver nothing.

## Invariants this creates

- `.claude-plugin/plugin.json`'s `skills` array lists exactly the promoted skills; drafts and the other non-promoted buckets never appear in it.
- `plugin.json`'s `version` tracks `package.json`'s. Changesets bumps only `package.json`, so the version PR must mirror the bump into `plugin.json` — the gate stays red until it does.
- Every promoted skill has a top-level `README.md` reference, a bucket `README.md` entry, and a docs page; the gate blocks merge when any of this drifts.
