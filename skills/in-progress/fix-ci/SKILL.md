---
name: fix-ci
description: Fetch the CI status for the current PR or branch, pull the failing run logs via the GitHub API, diagnose the failure, reproduce it locally, fix it, and push. Use when the user says CI is red, checks are failing, the build is broken, or asks to fix CI.
---

> **Draft** — scope agreed, behavior not yet written. Do not rely on this skill yet.

The planned loop:

1. **Status** — `gh pr checks` / `gh run list` for the current PR or branch; pick the failing runs.
2. **Logs** — pull the failing job logs via `gh api`, and extract the first real error rather than the last.
3. **Diagnose** — separate root cause from cascade noise; classify it (code, test, config, flake, infra).
4. **Reproduce locally** — run the same command the workflow runs; a fix is only trusted once the failure has been seen locally.
5. **Fix and push** — the smallest fix that addresses the root cause; push; watch the new run until green. Flakes get re-run and reported, not papered over.
