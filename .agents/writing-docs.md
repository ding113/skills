# Writing docs pages

Every skill in `engineering/` and `writing/` has a human-facing **docs page** at `docs/<bucket>/<skill-name>.md` — the docs tree mirrors the two promoted bucket folders under `skills/`. The page is not the skill and not a copy of `SKILL.md`: `SKILL.md` instructs the agent; the docs page orients the human. Only the promoted buckets get pages; `misc/`, `personal/`, `in-progress/`, and `deprecated/` ship none.

The job of a docs page is to relieve cognitive load — orient one reader around one skill so they can hold it in their head, know when to reach for it, and see where it sits among the others.

Act whenever a promoted skill is added, renamed, or has its behaviour changed: create or re-sync its docs page. A rename moves the file too; a skill moving between promoted buckets moves its docs file; a skill graduating into a promoted bucket gains a page, and one moving the other way loses it. The gate enforces existence, not freshness — keeping the content true is on you.

Links may be repo-relative; these pages are read on GitHub, not published to a separate site.

There is no H1 — the filename is the title.

## Page structure

Fill the template below. The **fixed frame** (Quickstart block, source link, `## What it does`, `## When to reach for it`, `## Where it fits`) appears on every page. The **adaptable middle** — `## Prerequisites` and the free-form substance sections — carries only what this particular skill earns; delete the rest.

<page-template>

Quickstart:

```bash
npx skills add ding113/skills --skill=<name>
```

[Source](../../skills/<bucket>/<name>/SKILL.md)

## What it does

One or two plain-language paragraphs. Lead with the skill's one-sentence job, then state the **defining constraint** — the single fact that makes this skill behave differently from the obvious default. Write it as a plain declarative sentence — never a labelled aside like "The key thing:"; the formula reads as filler. This line is the most valuable on the page; never omit it.

## When to reach for it

Two beats, both effectively always present:

- **Invocation mode.** A user-invoked skill: "You invoke this by typing `/<name>` — the agent won't reach for it on its own." A model-invoked skill: "Type `/<name>`, or the agent reaches for it automatically when a task fits."
- **Trigger boundary.** The index entry: "reach for this when …". Where the skill is confusable with a sibling, add the other half — "for X instead, use [sibling](../<bucket>/<sibling>.md)."

## Prerequisites

Optional — include only when the skill needs something in place to be functional (a workspace it writes into, prior setup, repo tooling like `gh`); omit the heading entirely otherwise.

## <free-form middle>

One to three short sections, in the skill's *own vocabulary*, that make it click — the loop it runs, the artifact it produces, the anti-pattern it kills. The single non-negotiable: **surface the skill's leading word / defining idea**, so the reader learns both what the skill is and the word they'll later think with to reach for it.

## It's working if

Optional. A short, checkable list of the observable signals that tell the reader the skill is doing its job. Include it when a skill has crisp tells; omit the heading when the signals are vague.

## Where it fits

Always present. Name the skill's **role** (a chain step, a run-once setup, periodic maintenance, or a reach-for-it-anytime standalone), its one or two **neighbours** with a because-clause, and point at the bucket `README.md` for the full list.

</page-template>

## Conventions

- Explain the **why**, not the process. The page orients and situates the skill; it never reproduces the `SKILL.md` steps — a human choosing a tool does not need the runbook.
- Use the skill's **leading words** so the page and the skill speak one language.
- Keep the page itself low-load — spare headings, no restated links.

## Done when

- The page exists at `docs/<bucket>/<name>.md`, and no stale page survives a rename or bucket move.
- The Quickstart block and source link name the correct bucket and skill.
- `## What it does` states the defining constraint, as plain prose rather than a labelled aside.
- `## When to reach for it` states invocation mode and the trigger boundary.
- `## Where it fits` names the role.
- Every link resolves.
