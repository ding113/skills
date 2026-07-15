---
name: get-pr-comments
description: Find the active pull request for the current branch or repo, pull its review comments, judge each review point as valid or a false positive, address the valid ones, and resolve every thread. Use when the user wants PR review feedback fetched, triaged, addressed, or resolved.
---

> **Draft** — scope agreed, behavior not yet written. Do not rely on this skill yet.

The planned loop:

1. **Locate the PR** — the one for the current branch (`gh pr view`), falling back to the repo's active PRs (`gh pr list`).
2. **Pull every review thread** — inline review comments and top-level review bodies, via `gh api` / GraphQL, including each thread's resolved state.
3. **Judge each point** — valid finding, false positive, or question; check the claim against the actual code before deciding.
4. **Handle each point** — fix valid ones; answer questions; rebut false positives with evidence in a reply.
5. **Resolve** — reply on every thread with what was done and resolve it; finish with a per-comment verdict table.
