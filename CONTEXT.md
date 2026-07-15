# ding113/skills

A collection of personal agent skills, shared publicly and consumed by Claude Code, Codex, and other Agent-Skills-standard harnesses.

## Language

**Skill**:
One directory under `skills/<bucket>/<name>/` holding a `SKILL.md` (the behavior) and `agents/openai.yaml` (Codex metadata).
_Avoid_: command, plugin (the plugin is the shipped bundle, not one skill)

**Bucket**:
A top-level folder under `skills/` stating a skill's lifecycle stage and audience: `engineering`, `writing`, `misc`, `personal`, `in-progress`, `deprecated`.
_Avoid_: category, group

**Promoted**:
In a bucket shipped to users — `engineering/` or `writing/`. A promoted skill appears in the top-level `README.md`, the plugin manifest, and `docs/`.
_Avoid_: published, public (the whole repo is public; promoted is about shipping)

**Draft**:
A skill in `in-progress/` — real frontmatter, unfinished body, excluded from the plugin and the top-level README reference.
_Avoid_: placeholder, stub, WIP

**Graduation**:
Moving a draft into a promoted bucket together with everything that implies: bucket README entries, top-level README reference, `plugin.json` entry, docs page, changeset.

**Gate**:
The checks that must pass before merge — `scripts/validate-skills.mjs` plus `claude plugin validate . --strict`, run by `.github/workflows/validate.yml`.
_Avoid_: lint, CI (the gate runs in CI; it isn't CI itself)

**Docs page**:
The human-facing page at `docs/<bucket>/<name>.md` for a promoted skill — orientation for a person, never a copy of `SKILL.md`.

## Relationships

- A **Skill** lives in exactly one **Bucket**
- A **Draft** is a **Skill** in `in-progress/`; **Graduation** moves it to a **Promoted** bucket
- The plugin ships exactly the **Promoted** skills
- The **Gate** blocks merge whenever the tree, manifests, READMEs, and docs pages disagree

## Flagged ambiguities

- "placeholder" vs "draft" — resolved: **Draft** is the term; "placeholder" survives only in informal chat.
